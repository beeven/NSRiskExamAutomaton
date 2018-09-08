

class ExamPolicy(object):
    def __init__(self):
        pass

    def evaluate(self, inputs: dict):
        return {
            '核对数量', '核对新旧', '核对唛头',
            'B',
        }