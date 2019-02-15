import pysher
from os import getenv

ENV = getenv('ENV')

possible_envs = ['test', 'dev', 'stage', 'prod', ]

if ENV not in possible_envs:
    raise Exception("ENV environment variable must be set. "
                    "Possible values: {}".format(', '.join(possible_envs)))

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

SUBDOMAIN = getenv('WEB_SUBDOMAIN')
