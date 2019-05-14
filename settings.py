import os
import json


ENV = os.getenv('ENV')

possible_envs = ['test', 'dev', 'stage', 'prod', ]

assert ENV in possible_envs, (
    "ENV environment variable must be set. "
    "Possible values: {}".format(', '.join(possible_envs))
)

config_filename = 'config.{}.json'.format(ENV)

assert os.path.isfile(config_filename), (
    "The config file is supposed to exists. {} does not exist!".format(config_filename)
)

with open(config_filename) as json_file:
    conf = json.load(json_file)

API_URL = conf['api']['url']
API_CLIENT_ID = conf['api']['client_id']
API_CLIENT_SECRET = conf['api']['client_secret']

USER_ID = conf['user']['id']
USER_HASH = conf['user']['hash']

PUSHER_KEY_ID = conf['pusher']['key_id']
PUSHER_SECRET = conf['pusher']['secret']
PUSHER_CLUSTER = conf['pusher']['cluster']

SENTRY_DSN = conf['sentry']['dsn']

USER_ACTIVITY_LOG = "{api_url}/api/user-activity-log/".format(api_url=API_URL)

DATETIME_TZ_FORMAT = '%Y-%m-%d %H:%M:%S%z'
# todo: Decide on asserting being non-null existence or full operation of some of the services here.
# todo Should we unify all time related variables to epoch?
