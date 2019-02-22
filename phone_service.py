from settings import twilio_account_sid, twilio_auth_token
from logger import get_logger

from conditional_imports import get_phone_service

Client = get_phone_service()    # Twilio Client


logger = get_logger()
client = Client(twilio_account_sid, twilio_auth_token)


def make_urgency_call(*args, **kwargs):
    logger.info("making urgency call")
    call = client.calls.create(
        to="+14155337523",
        from_="+15109015152",
        url="https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/urgent-button-from-user-maggy.xml",
        method="GET",
    )

    logger.info(call.sid)
    return call
