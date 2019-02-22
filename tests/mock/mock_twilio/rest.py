from logger import get_logger


class _Dummy:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


class _Calls:
    def __init__(self, sid, token):
        self.twilio_account_sid = sid
        self.twilio_auth_token = token

    def create(self, to, from_, url, method):
        return _Dummy(to=to,
                      from_=from_,
                      url=url,
                      method=method,
                      twilio_account_sid=self.twilio_account_sid,
                      twilio_auth_token=self.twilio_auth_token,
                      sid='12345')


class Client:
    def __init__(self, sid, token):
        self.twilio_account_sid = sid
        self.twilio_auth_token = token

    @property
    def calls(self):
        return _Calls(self.twilio_account_sid, self.twilio_auth_token)
