"""Readable business errors for a future CLI/UI boundary."""
class BusinessError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


class ParseError(BusinessError):
    pass


class AnalysisError(BusinessError):
    pass
