import json
import logging
import logging.config
import logging.handlers
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import selenium.webdriver.chrome.options

import exampolicy
import sqlite3


class RiskExamAutomaton(object):
    """Perform automatic operations on Risk Exam website according to predefined policies"""

    HOME_PAGE = "http://10.225.4.20/RiskExam/Default.aspx"

    def __init__(self, headless=False, debug=False):
        self.logger = logging.getLogger("RiskExamAutomaton")
        options = selenium.webdriver.chrome.options.Options()
        self.debug = debug
        if headless:
            options.add_argument("--headless")
            options.add_argument("--window-size=1024,768")
            options.add_argument("--disable-gpu")
        self.is_headless = headless
        if self.debug:
            self.driver = webdriver.Remote("http://10.3.1.181:9515", desired_capabilities=options.to_capabilities())
        else:
            self.driver = webdriver.Remote("http://10.3.1.181:4444/wd/hub", desired_capabilities=options.to_capabilities())
        self.policy = exampolicy.ExamPolicy()
        self.skip_list = []

        self.init_sqlite()

    def __del__(self):
        if self.driver is not None and not self.debug:
            self.driver.quit()
            self.driver = None

    def sign_in(self):
        """Sign in with username and password"""
        self.logger.debug("Signing in")
        logon_type_select = self.driver.find_element_by_name("logonType")
        logon_type_select.find_element_by_css_selector("option[value='formsauthentication']").click()
        self.driver.implicitly_wait(1)
        self.driver.find_element_by_name("signInName").send_keys("yuyonghui")
        self.driver.find_element_by_name("password").send_keys("qwer*1234")
        self.driver.find_element_by_name("ctl02$SignInButton").click()

    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open("cookies.txt", "w") as f:
            json.dump(cookies, f)

    def load_cookies(self):
        if os.path.isfile("./cookies.txt"):
            with open("cookies.txt") as f:
                cookies = json.load(f)
            for c in cookies:
                self.driver.add_cookie(c)
            return True
        else:
            return False

    def accept_alert(self, wait_sec=3):
        try:
            self.logger.debug("Detecting alert.")
            WebDriverWait(self.driver, wait_sec, poll_frequency=1).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
            return True
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            alert = self.driver.switch_to.alert
            self.logger.debug("Unexpected alert present: {0}".format(alert.text))
            alert.accept()
            return True
        except selenium.common.exceptions.TimeoutException:
            self.logger.debug("No alert is present.")
            return False

    def apply_exam_policy(self):
        self.logger.debug("Applying exam policies.")
        self.driver.switch_to.window(self.driver.window_handles[-1])

        self.accept_alert(15)

        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.ID, 'IDP_plugin_iform_overlaydiv')))

        # 开始细化
        # TODO: The button may be found not attaching to document.
        btns = self.driver.find_elements_by_xpath('//*[@id="btnstartCommand"]')
        if len(btns) > 0:
            btns[0].click()
            self.accept_alert(10)

        info = self.extract_info()
        self.logger.debug(info)
        outputs = self.policy.evaluate(info)
        self.logger.debug(outputs)

        if not outputs:
            self.logger.info("{0} 报关单信息不符合条件，无法处理".format(info['报关单号']))
            self.skip_list.append(info['报关单号'])
            return

        info = self.fill_form(outputs, info)

        # 下达查验指令
        if not self.debug:
            self.driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
            WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(1))
        self.log_to_sqlite(info)

    def extract_info(self):
        """获取查验信息和报关单信息"""

        info = {
            '布控理由': "\n".join([elem.text for elem in
                               self.driver.find_elements_by_xpath('//*[@id="iform3"]/table/tbody/tr[4]/td[2]/span')]),
            '布控要求': "，".join([elem.text for elem in
                              self.driver.find_elements_by_xpath('//*[@id="iform3"]/table/tbody/tr[5]/td[2]/span')]),
            '备注': "\n".join([elem.text for elem in
                             self.driver.find_elements_by_xpath('//*[@id="iform3"]/table/tbody/tr[7]/td[2]/span')])
        }
        entry_link = self.driver.find_element_by_xpath('//*[@id="entryDetail"]/a')
        window_handles = self.driver.window_handles
        self.logger.info("Extracting info of {0}".format(entry_link.text))
        entry_link.click()
        WebDriverWait(self.driver, 5).until(EC.new_window_is_opened(window_handles))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.ID, 'IDP_plugin_iform_overlaydiv')))

        info['报关单号'] = self.driver.find_element_by_xpath(
            '//*[@id="iform"]/tbody/tr[1]/td/table/tbody/tr[1]/td[3]/span').text
        info['进出口岸'] = self.driver.find_element_by_xpath(
            '//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/span').text
        info['运输方式'] = self.driver.find_element_by_xpath(
            '//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[2]/td[6]/span').text
        info['标记唛码及备注'] = self.driver.find_element_by_xpath(
            '//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[8]/td[2]/span').text
        info['集装箱号'] = self.driver.find_element_by_xpath(
            '//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[9]/td[2]/span').text
        info['商品编码'] = []

        trs = self.driver.find_elements_by_xpath('//*[@id="iform"]/tbody/tr')
        if len(trs) > 2:
            for i in range(2, len(trs)):
                code = trs[i].find_element_by_xpath('td/table/tbody/tr[1]/td[8]/span').text
                info['商品编码'].append(code)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return info

    def fill_form(self, forms: dict, info):
        """填写表单"""

        if 'result' not in info.keys():
            info['result'] = dict()

        for key in forms['ExamModeCodes']:
            v = exampolicy.ExamModeCodes[key]
            checkbox = self.driver.find_element_by_xpath('//*[@id="examModeCodes"]//input[@value="{0}"]'.format(v))
            if not checkbox.is_selected():
                checkbox.click()

        info['result']['ExamModeCodes'] = forms['ExamModeCodes'].copy()

        cbx_b1 = self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B1"]')
        cbx_b2 = self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B2"]')
        cbx_b3 = self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B3"]')

        if 'B' in forms['ExamMethod']:
            self.driver.find_element_by_xpath('//*[@id="radioB"]').click()

            # 如果系统自动判断，且没有强制选定B1 B2 B3，遵循系统判断规则
            if self.accept_alert() and forms['ExamMethod'].isdisjoint({'B1', 'B2', 'B3'}):
                if cbx_b1.is_selected():
                    forms['ExamMethod'].add('B1')
                elif cbx_b2.is_selected():
                    forms['ExamMethod'].add('B2')
                elif cbx_b3.is_selected():
                    forms['ExamMethod'].add('B3')
                else:
                    forms['ExamMethod'].add('B2')
            else:
                if forms['ExamMethod'].isdisjoint({'B1', 'B2', 'B3'}):
                    forms['ExamMethod'].add('B2')

        for key in forms['ExamMethod']:
            if key == 'B':
                continue
            elif key == "B1":
                cbx_b1.click()
                self.driver.find_element_by_xpath('//*[@id="openR"]').click()
                self.driver.find_element_by_xpath('//*[@id="openRate"]').send_keys('3')
            elif key == "B2":
                cbx_b2.click()
                self.driver.find_element_by_xpath('//*[@id="openR"]').click()
                self.driver.find_element_by_xpath('//*[@id="openRate"]').send_keys('10')
            elif key == "B3":
                cbx_b3.click()
                self.driver.find_element_by_xpath('//*[@id="openR"]').click()
                self.driver.find_element_by_xpath('//*[@id="openRate"]').send_keys('30')
            else:
                self.driver.find_element_by_xpath(
                    '//*[@id="iform4"]//input[@name="manChk" and @value="{0}"]'.format(key)).click()

        info['result']['ExamMethod'] = forms['ExamMethod'].copy()

        for key in forms['LocalModeCodes']:
            v = exampolicy.LocalModeCodes[key]
            if v in ("16", "17", "18"):
                continue
            else:
                checkbox = self.driver.find_element_by_xpath('//*[@id="localModeCodes"]//input[@value="{0}"]'.format(v))
                if not checkbox.is_selected():
                    checkbox.click()

        # 根据系统确定的查验方式确定本关区查验要求勾选什么
        if cbx_b1.is_selected():
            cbv = "16"
        elif cbx_b2.is_selected():
            cbv = "17"
        elif cbx_b3.is_selected():
            cbv = "18"
        else:
            cbv = None
        if cbv:
            cb = self.driver.find_element_by_xpath('//*[@id="localModeCodes"]//input[@value="{0}"]'.format(cbv))
            if not cb.is_selected():
                cb.click()

        # 从页面上获取系统判断的查验方式
        cbs = self.driver.find_elements_by_css_selector('#localModeCodes input:checked[type="checkbox"]')
        info['result']['LocalModeCodes'] = set([cb.find_element_by_xpath('..').text for cb in cbs])

        extras = forms.get('Extra', {})
        if 'NoRandomContainer' in extras:
            cbs = self.driver.find_elements_by_xpath('//*[@id="selectedContainer"]//input[@type="checkbox"]')
            for cb in cbs:
                if not cb.is_selected():
                    cb.click()
        else:
            self.driver.find_element_by_xpath('//*[@id="randomConta"]').click()
            self.accept_alert()

        info['result']['selected_containers_count'] = len(self.driver.find_elements_by_css_selector(
                                                                '#selectedContainer input:checked[type="checkbox"]'))

        self.driver.find_element_by_xpath('//*[@id="NoteS"]').send_keys(info['布控要求'] + "(自)")
        self.driver.find_element_by_xpath('//*[@id="SecurityInfo"]').send_keys(info['布控理由'])
        self.driver.find_element_by_xpath('//*[@id="OtherRequire"]').send_keys(info['备注'])
        return info

    def log_to_sqlite(self, info):
        conn = sqlite3.connect('logs.db')
        conn.execute("""insert into logs (entry_id, reason, req, note, 
        container_num, exam_req, exam_method, exam_container_num, exam_time) 
        values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (info['报关单号'], info['布控理由'], info['布控要求'], info['备注'],
                                                len(info['集装箱号'].split(';')), ';'.join(info['result']['ExamModeCodes']),
                                                ';'.join(info['result']['LocalModeCodes']),
                                                info['result']['selected_containers_count'],
                                                datetime.datetime.now()))
        conn.commit()
        conn.close()

    def init_sqlite(self):
        conn = sqlite3.connect('logs.db')
        conn.execute("""CREATE TABLE IF NOT EXISTS logs 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     entry_id text,
                     reason text,
                     req text,
                     note text,
                     container_num integer,
                     exam_req text,
                     exam_method text,
                     exam_container_num integer,
                     exam_time text);""")
        conn.close()

    def run(self):
        self.logger.debug("Opening homepage")
        self.driver.get(RiskExamAutomaton.HOME_PAGE)

        if self.load_cookies():
            self.driver.refresh()

        if not self.driver.current_url.startswith(RiskExamAutomaton.HOME_PAGE[:20]):
            self.sign_in()
            self.save_cookies()
            # self.browser.get(HOME_PAGE)

        menu_opened = False
        while True:
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.logger.debug("Opening 查验指令下达")
            if not menu_opened:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "选择查验"))).click()
                menu_opened = True

            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.LINK_TEXT, "查验指令下达"))).click()

            time.sleep(5)

            self.logger.debug("Waiting for iframe loading")
            frame = self.driver.find_element_by_id("fcontent")
            self.driver.switch_to.frame(frame)
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.ID, 'IDP_plugin_listgrid_loadingdiv')))
            tbl = self.driver.find_element_by_id("applyList1")
            lines = len(tbl.find_elements_by_css_selector('tbody tr'))
            self.logger.debug("{0} lines to process.".format(lines))

            has_processed_one_line = False
            for i in range(lines):
                line = tbl.find_element_by_xpath('tbody/tr[{0}]/td[2]'.format(i + 1))
                self.logger.info("Start processing {0}".format(line.text))
                status = tbl.find_element_by_xpath('tbody/tr[{0}]/td[5]'.format(i + 1)).text
                if status != '未下达查验指令' and status != '开始细化查验指令':
                    self.logger.info("Status is not 未下达查验指令 or 开始细化查验指令, skipping.")
                    continue
                entry_id = tbl.find_element_by_xpath('tbody/tr[{0}]/td[2]'.format(i + 1)).text
                # if entry_id[-4:] in ("1699",):
                #     continue

                if entry_id in self.skip_list:
                    continue

                # else:
                btn = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="applyList1"]/tbody/tr[{0}]/td[7]/img[@code="edit"]'.format(i + 1))))
                btn.click()
                # tbl.find_element_by_xpath('tbody/tr[{0}]/td[7]/img[@code="edit"]'.format(i + 1)).click()
                self.apply_exam_policy()
                has_processed_one_line = True
                break
            if not has_processed_one_line:
                break
            if self.debug:
                break
        self.logger.debug("No remaining line. Exiting.")



if __name__ == "__main__":
    import logging.config
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default'
            },
            'rotate_file': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': 'automaton.log',
                'encoding': 'utf8',
                'when': 'D',
                'interval': 30
            },
            'errors': {
                'level': 'ERROR',
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'automaton_error.log',
                'encoding': 'utf8',
                'maxBytes': 102400000,
                'backupCount': 30
            }
        },
        'loggers': {
            'RiskExamAutomaton': {
                'level': 'DEBUG'
            },
            '': {
                'level': 'INFO',
                'handlers': ['console', 'rotate_file', 'errors']
            }
        }
    })

    automaton = RiskExamAutomaton(headless=False)
    try:
        automaton.run()
    except Exception as e:
        logging.error(e, exc_info=True)
