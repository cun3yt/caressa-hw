from twilio.rest import Client
from settings import twilio_account_sid, twilio_auth_token

client = Client(twilio_account_sid, twilio_auth_token)


def make_urgency_call(*args, **kwargs):
    call = client.calls.create(
        to="+14155337523",
        from_="+15109015152",
        url="https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/urgent-button-from-user-maggy.xml",
        method="GET",
    )

    print(call.sid)
