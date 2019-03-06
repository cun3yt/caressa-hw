from settings import twilio_account_sid, twilio_auth_token
from logger import get_logger

from conditional_imports import get_phone_service

Client = get_phone_service()    # Twilio Client


logger = get_logger()
client = Client(twilio_account_sid, twilio_auth_token)


def make_urgency_call(*args, **kwargs):
    logger.info("making urgency call")

    to = "+14155337523"
    from_ = "+15109015152"
    url = "https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/urgent-button-from-user-maggy.xml"

    call = client.calls.create(
        to=to,
        from_=from_,
        url=url,
        method="GET",
    )

    logger.info(call.sid)
    logger.info("twilio call from: {from_} to: {to} url: {url}".format(from_=from_, to=to, url=url))

    return {'command': 'twilio.call', 'from': from_, 'to': to, 'url': url}
