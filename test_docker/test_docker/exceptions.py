# TODO:TDockerError
class TDockerError(Exception):
    def __init__(self, msg=None, detail=None, payload=None):
        self.msg = msg
        self.detail = detail
        self.payload = payload
        super().__init__(msg)

    # 添加detail信息
    def __str__(self):
        msg = self.msg
        if self.detail:
            msg += f' ({self.msg})'
        return msg


class InvaildConfiguration(TDockerError):
    pass


class InvalidRepo(TDockerError):
    pass
