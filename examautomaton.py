import json
import logging
import logging.config
import logging.handlers
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import selenium.webdriver.chrome.options

import dummyexampolicy
import exampolicy

class RiskExamAutomaton(object):
    """Perform automatic operations on RiskExam website according to predefined policies"""

    HOME_PAGE = "http://10.225.4.20/RiskExam/Default.aspx"

    def __init__(self, headless=False):
        self.logger = logging.getLogger("RiskExamAutomation")
        options = selenium.webdriver.chrome.options.Options()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--window-size=1024,768")
            options.add_argument("--disable-gpu")
        self.is_headless = headless
        self.driver = webdriver.Remote("http://10.3.1.181:9515", desired_capabilities=options.to_capabilities())
        self.policy = exampolicy.ExamPolicy()

    def __del__(self):
        #self.driver.quit()
        pass

    def sign_in(self):
        """Sign in with username and password"""
        self.logger.debug("Signing in ...")
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

    def accept_alert(self):
        try:
            self.logger.debug("Detecting alert.")
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            alert = self.driver.switch_to.alert
            self.logger.debug("Alert present: {0}".format(alert.text))
            alert.accept()
        except selenium.common.exceptions.TimeoutException:
            self.logger.debug("No alert is present.")

    def apply_exam_policy(self):
        self.logger.debug("Applying exam policies.")
        self.driver.switch_to.window(self.driver.window_handles[-1])

        self.accept_alert()

        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.ID, 'IDP_plugin_iform_overlaydiv')))

        #开始细化
        self.driver.find_element_by_xpath('//*[@id="btnstartCommand"]').click()
        self.accept_alert()

        info = self.extract_info()
        self.logger.debug(info)
        outputs = self.policy.evaluate(info)
        self.logger.debug(outputs)
        self.fill_form(outputs, info)

        # 下达查验指令
        self.driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()

    def extract_info(self):
        info = {
            '布控理由':self.driver.find_element_by_xpath('//*[@id="iform3"]/table/tbody/tr[4]/td[2]/span').text,
            '布控要求': self.driver.find_element_by_xpath('//*[@id="iform3"]/table/tbody/tr[5]/td[2]/span').text,
            '备注': self.driver.find_element_by_xpath('//*[@id="iform3"]/table/tbody/tr[7]/td[2]/span').text
        }
        entry_link = self.driver.find_element_by_xpath('//*[@id="entryDetail"]/a')
        entry_link.click()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        WebDriverWait(self.driver, 3).until(
            EC.invisibility_of_element_located((By.ID, 'IDP_plugin_iform_overlaydiv')))

        info['报关单号'] = self.driver.find_element_by_xpath('//*[@id="iform"]/tbody/tr[1]/td/table/tbody/tr[1]/td[3]/span').text
        info['进出口岸'] = self.driver.find_element_by_xpath('//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/span').text
        info['运输方式'] = self.driver.find_element_by_xpath('//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[2]/td[6]/span').text
        info['标记唛码及备注'] = self.driver.find_element_by_xpath('//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[8]/td[2]/span').text
        info['集装箱号'] = self.driver.find_element_by_xpath('//*[@id="iform"]/tbody/tr[2]/td/table/tbody/tr[9]/td[2]/span').text
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
        for key in forms['ExamModeCodes']:
            v = exampolicy.ExamModeCodes[key]
            checkbox = self.driver.find_element_by_xpath('//*[@id="examModeCodes"]//input[@value="{0}"]'.format(v))
            if not checkbox.is_selected():
                checkbox.click()

        flag_hasalert = False
        for key in forms.get('ExamMethod', {}):
            if key == 'B':
                self.driver.find_element_by_xpath('//*[@id="radioB"]').click()
                self.accept_alert()

            elif key == "B1":
                if not flag_hasalert:
                    self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B1"]').click()
                self.driver.find_element_by_xpath('//*[@id="openR"]').click()
                self.driver.find_element_by_xpath('//*[@id="openRate"]').send_keys('3')
            elif key == "B2":
                if not flag_hasalert:
                    self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B2"]').click()
                self.driver.find_element_by_xpath('//*[@id="openR"]').click()
                self.driver.find_element_by_xpath('//*[@id="openRate"]').send_keys('10')
            elif key == "B3":
                if not flag_hasalert:
                    self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B3"]').click()
                self.driver.find_element_by_xpath('//*[@id="openR"]').click()
                self.driver.find_element_by_xpath('//*[@id="openRate"]').send_keys('10')
            else:
                self.driver.find_element_by_xpath('//*[@id="iform4"]//input[@name="manChk" and @value="{0}"]'.format(key)).click()

        for key in forms['LocalModeCodes']:
            v = exampolicy.LocalModeCodes[key]
            if flag_hasalert and v in ("16", "17", "18"):
                continue
            checkbox = self.driver.find_element_by_xpath('//*[@id="localModeCodes"]//input[@value="{0}"]'.format(v))
            if not checkbox.is_selected():
                checkbox.click()

        # 系统自动判断
        if flag_hasalert:
            # 简易查验
            if self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B1"]').is_selected():
                cb = self.driver.find_element_by_xpath('//*[@id="localModeCodes"]//input[@value="16"]')
                if not cb.is_selected():
                    cb.click()
            elif self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B2"]').is_selected():
                cb = self.driver.find_element_by_xpath('//*[@id="localModeCodes"]//input[@value="17"]')
                if not cb.is_selected():
                    cb.click()
            elif self.driver.find_element_by_xpath('//*[@id="chkTd"]/input[@value="B3"]').is_selected():
                cb = self.driver.find_element_by_xpath('//*[@id="localModeCodes"]//input[@value="18"]')
                if not cb.is_selected():
                    cb.click()

        extras = forms.get('Extra', {})
        if 'NoRandomContainer' in extras:
            cbs = self.driver.find_elements_by_xpath('//*[@id="selectedContainer"]//input[@type="checkbox"]')
            for cb in cbs:
                cb.click()
        else:
            self.driver.find_element_by_xpath('//*[@id="randomConta"]').click()
            self.accept_alert()

        self.driver.find_element_by_xpath('//*[@id="NoteS"]').send_keys(info['布控要求'])
        self.driver.find_elements_by_xpath('//*[@id="SecurityInfo"]').send_keys(info['布控理由'])
        self.driver.find_element_by_xpath('//*[@id="OtherRequire"]').send_keys(info['备注'])

    def run(self):
        self.logger.debug("Opening homepage")
        self.driver.get(RiskExamAutomaton.HOME_PAGE)

        if self.load_cookies():
            self.driver.refresh()

        if not self.driver.current_url.startswith(RiskExamAutomaton.HOME_PAGE[:20]):
            self.sign_in()
            self.save_cookies()
            # self.browser.get(HOME_PAGE)

        if self.is_headless:
            self.driver.find_element_by_link_text("选择查验").click()
            self.driver.find_element_by_link_text("选择查验").click()
        else:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "选择查验"))).click()
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.LINK_TEXT, "查验指令下达"))).click()

        frame = self.driver.find_element_by_id("fcontent")
        self.driver.switch_to.frame(frame)
        WebDriverWait(self.driver, 3).until(EC.invisibility_of_element_located((By.ID, 'IDP_plugin_listgrid_loadingdiv')))
        tbl = self.driver.find_element_by_id("applyList1")
        lines = len(tbl.find_elements_by_css_selector('tbody tr'))
        self.logger.debug("{0} lines to process.".format(lines))

        for i in range(lines):
            line = tbl.find_element_by_xpath('tbody/tr[{0}]/td[5]'.format(i + 1))
            if line.text != '未下达查验指令':
                continue

            else:
                tbl.find_element_by_xpath('tbody/tr[{0}]/td[7]/img[1]'.format(i + 1)).click()
                self.apply_exam_policy()
                break
