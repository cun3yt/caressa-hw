from os import getenv

import pysher

twilio_account_sid = getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = getenv('TWILIO_AUTH_TOKEN')

pusher_app_id = getenv('PUSHER_APP_ID')
pusher_key_id = getenv('PUSHER_KEY_ID')
pusher_secret = getenv('PUSHER_SECRET')
pusher_cluster = getenv('PUSHER_CLUSTER')

pusher = pysher.Pusher(key=pusher_key_id,
                       cluster=pusher_cluster,
                       secure=True,
                       secret=pusher_secret)

SUBDOMAIN = 'https://65273eb7.ngrok.io'
