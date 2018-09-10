# -*- coding: utf-8 -*-

import re
from abc import abstractmethod

EXAM_GOODS_CODE_MATCH_LENGTH = 4

ExamCondition = ['报关单号', '进出口岸', '运输方式', '提单号', '标记唛码及备注', '集装箱号', '商品编码', '布控要求', '布控理由']

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


class Classifier(object):
    @abstractmethod
    def classify(self, inputs):
        pass


class IOPortClassifier(Classifier):
    def __init__(self):
        self.name = '进出口岸'

    def classify(self, inputs: dict):
        if inputs['进出口岸'] == '南沙海关南沙港区监管点':
            if inputs['标记唛码及备注'].find("散货码头") != -1:
                return '2'
            else:
                return '1'
        elif inputs['进出口岸'] == '南沙海关保税港区监管点':
            return '3'
        return '0'


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
        if not frozenset({'470710', '470720', '470703'}).isdisjoint(
                    frozenset(map(lambda a: a[:6], inputs['商品编码']))):
            return '4'
        if inputs['标记唛码及备注'].find('危险品') != -1 or \
                not frozenset({'08039000', '08043000', '08105000', '08106000', '08054000', '08061000'}).isdisjoint(
                    frozenset(map(lambda a: a[:8], inputs['商品编码']))):

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
        for i, g in enumerate(goods):
            found = False
            for c in MachineExamCode:
                if g.startswith(c):
                    found = True
                    break
            if not found:
                return '0'
        return '1'


class CommandClassifier(Classifier):
    def __init__(self):
        self.name = '指令类型'

    def classify(self, inputs: dict):
        reqs = frozenset(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", inputs['布控要求']))))

        if reqs.isdisjoint(frozenset(['检查箱体', '核对品名', '核对重量', '是否夹藏'])):
            return '2'
        else:
            return '1'


class ExamPolicy(object):

    def __init__(self):
        self.classifiers = [IOPortClassifier(), RequirementClassifier(), GoodsClassifier(), CommandClassifier(),
                            GoodsClassifier2()]

    def dense_layer(self, conditions, classification):
        if classification.startswith('1111'):
            ret = {
                'ExamModeCodes': set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))),
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }
            ret['ExamModeCodes'].discard('查验单货是否相符')

        elif classification.startswith('1112'):
            ret = {
                'ExamModeCodes': set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))),
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B'}
            }
            ret['ExamModeCodes'].discard('查验单货是否相符')

        elif classification.startswith('112'):
            ret = {
                'ExamModeCodes': set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))),
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B'}
            }
            ret['ExamModeCodes'].discard('查验单货是否相符')

        elif classification.startswith('113'):
            ret = {
                'ExamModeCodes': set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))),
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }
            ret['ExamModeCodes'].discard('查验单货是否相符')

        elif classification.startswith('114'):
            ret = {
                'ExamModeCodes': set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))),
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'},
                'Extra': {'NoRandomContainer'}
            }

        elif re.fullmatch('121.1', classification) is not None:
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '核对品名'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif re.fullmatch('121.0', classification) is not None:
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif classification.startswith('122'):
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '核对品名'},
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B'}
            }

        elif re.fullmatch('123.1', conditions) is not None:
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '核对品名', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif re.fullmatch('123.0', conditions) is not None:
            ret = {
                'ExamModeCodes': {'核对重量', '是否夹藏', '检查箱体'},
                'LocalModeCodes': {'FS6000'},
                'ExamMethod': {'J'}
            }

        elif classification.startswith('21'):
            ret = {
                'ExamModeCodes': set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))),
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B'}
            }
            ret['ExamModeCodes'].discard('查验单货是否相符')

        elif classification.startswith('22'):
            ret = {
                'ExamModeCodes': {'核对重量', '核对品名', '核对规格'},
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B'}
            }

        elif classification.startswith('31'):
            ret = {
                'ExamModeCodes': set(filter(None, map(lambda a: a.strip(), re.split(r"[,，]", conditions['布控要求'])))),
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B'}
            }
            ret['ExamModeCodes'].discard('查验单货是否相符')

        elif classification.startswith('32'):
            ret = {
                'ExamModeCodes': {'核对重量', '核对品名', '核对规格'},
                'LocalModeCodes': {'常规抽查'},
                'ExamMethod': {'B'}
            }

        else:
            ret = {
                'ExamModeCodes': set(),
                'LocalModeCodes': set(),
                'ExamMethod': set()
            }

        return ret

    def evaluate(self, inputs):
        classification = ''.join([c.classify(inputs) for c in self.classifiers])
        outputs = self.dense_layer(inputs, classification)
        return outputs
