from .cache import cached


class CacheFakeRequest:
    method = 'PUT'


class CacheFake:
    def __init__(self, uri: str):
        self.request = CacheFakeRequest()
        self.request.uri = uri

    @staticmethod
    def get_status():
        return 201

    @cached
    def refresh(self):
        pass
