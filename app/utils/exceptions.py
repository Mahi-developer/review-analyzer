
class Exceptions(Exception):

    def __init__(self, e: Exception, msg: str):
        self.e = e
        self.msg = msg

    def __str__(self):
        return self.e.__str__() + ' ' + self.msg


class PredictionException(Exceptions):
    def __init__(self, e, msg):
        pass


class AnalyzerException(Exceptions):
    def __init__(self, e, msg):
        pass


class GenerateResponseException(Exceptions):
    def __init__(self, e, msg):
        pass


class FirebaseException(Exceptions):
    def __init__(self, e, msg):
        pass


exceptions = {
    'prediction': PredictionException,
    'analyzer': AnalyzerException,
    'generate_response': GenerateResponseException,
    'firebase': FirebaseException
}
