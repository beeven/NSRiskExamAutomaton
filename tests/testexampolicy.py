import unittest

import exampolicy


class TestGoodsClassifier2(unittest.TestCase):
    def setUp(self):
        self.target = exampolicy.GoodsClassifier2()

    def test_allInMachineCode(self):
        inputs = {'商品编码': ['08039000', '08105000']}

        actual = self.target.classify(inputs)
        self.assertEqual('1', actual)

    def test_prefixInMachineCode(self):
        inputs = {'商品编码': ['40111033', '85392233']}
        actual = self.target.classify(inputs)
        self.assertEqual('1', actual)

    def test_partialInMachineCode(self):
        inputs = {'商品编码': ['40111033', '11111111']}
        actual = self.target.classify(inputs)
        self.assertEqual('0', actual)

    def test_notInMachineCode(self):
        inputs = {'商品编码': ['11111111', '22222222']}
        actual = self.target.classify(inputs)
        self.assertEqual('0', actual)


class TestGoodsClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = exampolicy.GoodsClassifier()

    def test_lessThan3AndNotCombined(self):
        inputs = {'商品编码': ['85141000', '85142000', '02032900'],
                  '标记唛码及备注': '<总担保HH201852000001>港口区二期，欧废A5，签约日期：2018年7月21日'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('1', actual)

    def test_lessThan3AndCombined(self):
        inputs = {'商品编码': ['85141000', '85142000', '02032900'],
                  '标记唛码及备注': '拼柜, <总担保HH201852000001>港口区二期，欧废A5，签约日期：2018年7月21日'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('2', actual)

    def test_moreThan3AndNotCombined(self):
        inputs = {'商品编码': ['85141000', '85142000', '02032900', '73211100', '123456'],
                  '标记唛码及备注': '<总担保HH201852000001>港口区二期，欧废A5，签约日期：2018年7月21日'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('2', actual)

    def test_moreThan3AndCombined(self):
        inputs = {'商品编码': ['85141000', '85142000', '02032900', '73211100', '12345'],
                  '标记唛码及备注': '拼柜, <总担保HH201852000001>港口区二期，欧废A5，签约日期：2018年7月21日'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('2', actual)

    def test_dangerGoods(self):
        inputs = {'商品编码': ['1234567', '2323123'],
                  '标记唛码及备注': '危险品；拼柜；'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('3', actual)

    def test_Fruit(self):
        inputs = {'商品编码': ['08105000', '08043000'],
                  '标记唛码及备注': '拼柜；'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('3', actual)

    def test_allFruitOrPaper2(self):
        inputs = {'商品编码': ['470710000', '470720000', '470730999'],
                  '标记唛码及备注': '拼柜；'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('4', actual)

    def test_wastePaper(self):
        inputs = {'商品编码': ['4707300000'], '标记唛码及备注':'港口区二期，美废NO.8，签约日期：2017年12月26日'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('4', actual)


class TestIOPortClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = exampolicy.IOPortClassifier()

    def test_5166Port(self):
        inputs = {'报关单号': '516620181668030045', '进出口岸': '南沙海关南沙港区监管点', '运输方式': '水路运输',
                  '标记唛码及备注': '港口区三期，签约日期：2018年08月14日，原产地证书号：E2018-0154281', '集装箱号':'123123;123123'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('1', actual)

    def test_5166Port2(self):
        inputs = {'报关单号': '516620181668029976', '进出口岸': '南沙海关南沙港区监管点', '运输方式': '水路运输', '标记唛码及备注': '南沙港二期码头', '集装箱号':'123123;123123'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('1', actual)

    def test_5165(self):
        inputs = {'报关单号':'516520181658028895', '进出口岸': '南沙海关保税港区监管点', '运输方式': '水路运输', '标记唛码及备注': '加工区 跨境电子商务试点 入区 账册号：51652358932', '集装箱号':'123123;123123'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('3', actual)

    def test_5166PortSpecial(self):
        inputs = {'报关单号': '513120180318430642', '进出口岸': '南沙海关南沙港区监管点',  '标记唛码及备注':'散货码头' ,'集装箱号':'123123;123123'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('2', actual)



class TestRequirementClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = exampolicy.RequirementClassifier()

    def test_specificRequirement(self):
        inputs = {'布控要求': '核对品名，是否侵权，是否夹藏'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('1', actual)

    def test_generalRequirement(self):
        inputs = {'布控要求': '查验单货是否相符'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('2', actual)

    def test_generalAndSpecificRequirement(self):
        inputs = {'布控要求': '查验单货是否相符，核对品名，是否侵权，是否夹藏'}
        actual = self.classifier.classify(inputs)
        self.assertEqual('1', actual)


class TestFunctions(unittest.TestCase):
    def test_is_starts_within(self):
        set_A = {'12345', '23456'}
        set_B = {'123', '23'}
        actual = exampolicy.is_starts_within(set_A, set_B)
        self.assertTrue(actual)

    def test_is_starts_within2(self):
        set_A = {'12345', '23456'}
        set_B = {'123'}
        actual = exampolicy.is_starts_within(set_A, set_B)
        self.assertFalse(actual)


if __name__ == "__main__":
    unittest.main()
