from httpx import Response


class TelegraphException(Exception):
    pass


class ResponseNotOk(TelegraphException):
    def __init__(self, response: Response):
        self.response = response
        super().__init__(f'The response is not OK. Status Code:- {response.status_code}')


class RetryAfterError(TelegraphException):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f'Flood control exceeded. Retry in {retry_after} seconds')


class ParsingException(Exception):
    pass


class NotAllowedTag(ParsingException):
    pass


class InvalidHTML(ParsingException):
    pass
