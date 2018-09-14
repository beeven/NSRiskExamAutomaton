# -*- coding: utf-8 -*-

import re
import random
import logging
from abc import abstractmethod

EXAM_GOODS_CODE_MATCH_LENGTH = 4

ExamCondition = ['报关单号', '进出口岸', '运输方式', '提单号', '标记唛码及备注', '集装箱号', '商品编码', '布控要求', '布控理由', '备注']

ExamModeCodes = {
    '核对品名': '01', '核对规格': '02', '核对数量': '03', '核对重量': '04', '核对件数': '05', '核对唛头': '06', '是否侵权': '07',
    '核产终地': '08', '核对归类': '09', '核对新旧': '10', '核对价格': '11', '取样送检': '12', '检查车体': '13', '检查箱体': '14', '是否夹藏': '15'}

LocalModeCodes = {'简易抽查': '16', '常规抽查': '17', '重点抽查': '18', '机动查验': '19', '复验': '20', 'X光机检查': '21', '三个一': '22',
                  '核对品牌': '23', 'H986': '24', 'FS6000': '25', '核对体积': '26'}

ExamMethod = {'A': 'A', 'B': 'B', 'B1': 'B1', 'B2': 'B2', 'B3': 'B3', 'C': 'C', 'J': 'J', 'X': 'X'}

MachineExamCode = {'84159090', '841510', '841810', '841820', '841830', '841840', '841850', '852871', '852872', '851420',
                   '851821', '851822', '851829', '851410', '851420', '732111', '732112', '732119', '732181', '853922',
                   '853950', '940510', '940520', '940530', '940540', '401110', '401120', '401140', '401180', '401190',
                   '08039000', '08043000', '08105000', '08106000', '08054000', '08061000', '02064900', '02032900',
                   '02071421', '02071422', '470710', '470720', '470730'}


def is_starts_within(set_A, set_B):
    for a in set_A:
        found = False
        for b in set_B:
            if a.startswith(b):
                found = True
                break
        if not found:
            return False
    return True


class Classifier(object):
    @abstractmethod
    def classify(self, inputs):
        pass


class IOPortClassifier(Classifier):
    def __init__(self):
        self.name = '进出口岸'

    def classify(self, inputs: dict):
        if inputs['进出口岸'] == '南沙海关南沙港区监管点':
            if not inputs['集装箱号']:
                return '3'
            if inputs['标记唛码及备注'].find("散货码头") != -1:
                return '2'
            else:
                return '1'
        else:
            return '3'


class RequirementClassifier(Classifier):
    def __init__(self):
        self.name = '布控指令类型'

    def classify(self, inputs: dict):
        if inputs['布控要求'] == '查验单货是否相符':
            return '2'
        else:
            return '1'


class GoodsClassifier(Classifier):
    def __init__(self):
        self.name = '商品编码'

    def classify(self, inputs: dict):
        goods = frozenset(map(lambda a: a[:EXAM_GOODS_CODE_MATCH_LENGTH], inputs['商品编码']))
        if len(goods) == 1 and '4707' in goods:  # 废纸
                return '4'

        if inputs['标记唛码及备注'].find('危') != -1 or is_starts_within(goods, {
                '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '0810', '0813'
                }) or is_starts_within(goods, {'02', '03', '04', '05'}):  # 危险品 or 冻品 or 水果
            return '3'
        elif inputs['标记唛码及备注'].find('拼柜') != -1 or len(goods) > 3:
            return '2'
        elif len(goods) <= 3 and inputs['标记唛码及备注'].find('拼柜') == -1:
            return '1'
        else:
            return '0'


class GoodsClassifier2(Classifier):
    def __init__(self):
        self.name = '机检直放列表'

    def classify(self, inputs: dict):
        goods = inputs['商品编码']
        if is_starts_within(goods, MachineExamCode):
            return '1'
        else:
            return '0'


class CommandClassifier(Classifier):
    def __init__(self):
        self.name = '指令类型'

    def classify(self, inputs: dict):
        reqs = frozenset(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", inputs['布控要求']))))

        if reqs.isdisjoint({'检查箱体', '核对重量', '是否夹藏'}):
            return '2'
        else:
            return '1'


class ExamPolicy(object):

    def __init__(self):
        self.classifiers = [IOPortClassifier(), RequirementClassifier(), GoodsClassifier(), CommandClassifier(),
                            GoodsClassifier2()]
        self.logger = logging.getLogger("ExamPolicy")

    def dense_layer(self, conditions, classification):
        reqs = set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))).difference({'查验单货是否相符'})

        if classification.startswith('1111'):
            self.logger.info("判断结果: 5166, 具体布控要求, 商品编码3项或以下，不拼柜，不含3项指令 | 机检")
            ret = {
                'ExamModeCodes': reqs,
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif classification.startswith('1112'):
            self.logger.info("判断结果: 5166, 具体布控要求, 商品编码3项或以下，不拼柜，含3项指令之一 | 人工抽查")
            ret = {
                'ExamModeCodes': reqs,
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B', 'B2'}
            }

        elif classification.startswith('112'):
            self.logger.info("判断结果: 5166, 具体布控要求, 商品编码3项以上，或拼柜，含3项指令之一 | 人工抽查")
            ret = {
                'ExamModeCodes': reqs,
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B', 'B2'}
            }

        elif classification.startswith('113'):  # 危险品 冻品 水果
            self.logger.info("判断结果: 5166, 具体布控要求, 危险品冻品水果 | 机检")
            ret = {
                'ExamModeCodes': reqs,
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif classification.startswith('114'):  # 废纸
            self.logger.info("判断结果: 5166, 具体布控要求, 废纸 | 机检，非随机选箱")
            ret = {
                'ExamModeCodes': reqs.union({'核对品名'}),
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'},
                'Extra': {'NoRandomContainer'}
            }

        elif re.fullmatch('121.1', classification) is not None:
            self.logger.info("判断结果: 5166, 无具体指令, 商品编码3项或以下，不拼柜，直放列表内 | 机检，核对品名、核对重量、核对箱体、是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '核对品名', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif re.fullmatch('121.0', classification) is not None:
            self.logger.info("判断结果: 5166, 无具体指令, 商品编码3项或以下，不拼柜，非直放列表内 | 机检，核对重量、核对箱体、是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif classification.startswith('122'):
            self.logger.info("判断结果: 5166, 无具体指令, 商品编码3项以上，或拼柜，非直放列表内 | 人工抽查，核对品名、核对重量、是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '核对品名'},
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B', 'B2'}
            }

        elif re.fullmatch('123.1', classification) is not None:  # 属于机检直放目录
            self.logger.info("判断结果: 5166, 无具体指令, 危险品水果冻品，直放列表内 | 机检，核对品名、核对重量、检查箱体、是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '核对品名', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif re.fullmatch('123.0', classification) is not None:
            self.logger.info("判断结果: 5166, 无具体指令, 危险品水果冻品，非直放列表内 | 机检，核对重量、检查箱体、是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif re.fullmatch('124.1', classification) is not None:  # 属于机检直放目录
            self.logger.info("判断结果: 5166, 无具体指令, 废纸, 直放列表内 | 机检，核对品名、核对重量、检查箱体、是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '核对品名', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'},
                'Extra': {'NoRandomContainer'}
            }

        elif re.fullmatch('124.0', classification) is not None:
            self.logger.info("判断结果: 5166, 无具体指令, 废纸，非直放列表内 | 机检，核对重量、检查箱体、是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'},
                'Extra': {'NoRandomContainer'}
            }

        elif classification.startswith('21'):
            self.logger.info("判断结果: 5166散货码头, 具体布控要求 | 人工抽查")
            ret = {
                'ExamModeCodes': reqs,
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B', 'B2'}
            }

        elif classification.startswith('22'):
            self.logger.info("判断结果: 5166散货码头, 无具体指令 | 人工抽查，核对重量, 核对品名, 核对规格")
            ret = {
                'ExamModeCodes': {'核对重量', '核对品名', '核对规格'},
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B', 'B2'}
            }

        elif classification.startswith('31'):
            self.logger.info("判断结果: 5165, 具体布控要求 | 人工抽查")
            ret = {
                'ExamModeCodes': reqs,
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B', 'B2'}
            }

        elif classification.startswith('32'):
            self.logger.info("判断结果: 5165, 无具体指令 | 人工抽查，核对重量, 核对品名, 是否夹藏")
            ret = {
                'ExamModeCodes': {'核对重量', '核对品名', '是否夹藏'},
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B', 'B2'}
            }

        else:
            self.logger.info("判断结果: 无法判断")
            ret = {
                'ExamModeCodes': set(),
                'LocalModeCodes': set(),
                'ExamMethod': set()
            }

        if conditions['备注'].find('重量') != -1:
            ret['ExamModeCodes'].add('核对重量')

        if conditions['布控理由'].find('不少于三项') != -1:
            remaining = ['核对箱体', '核对重量', '是否夹藏']
            random.shuffle(remaining)

            while len(ret['ExamModeCodes']) < 3:
                cmd = remaining.pop()
                ret['ExamModeCodes'].add(cmd)

        if (len(reqs) > 5 and 'B' in ret['ExamMethod']) or conditions['布控理由'].find("失信") != -1:
            ret['ExamMethod'].discard('B2')
            ret['ExamMethod'].add('B3')
            ret['LocalModeCodes'].discard('常规抽查')
            ret['LocalModeCodes'].add('重点抽查')

        return ret

    def evaluate(self, inputs):
        classification = ''.join([c.classify(inputs) for c in self.classifiers])
        self.logger.debug("Classified result: {0}".format(classification))
        outputs = self.dense_layer(inputs, classification)
        return outputs
