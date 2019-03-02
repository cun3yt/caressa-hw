import requests

from settings import USER_ACTIVITY_LOG


def button_action(user_action, callback_fn, user_activity_log_url=USER_ACTIVITY_LOG):
    """
    This is a wrapper for actual button callback function

    :param user_action: Definition of the action done on the button, e.g. 'press.volume'
    :param callback_fn: Callback function of the button that does the actual work
    :param user_activity_log_url: End point for logging
    :return:
    """
    
    def _action_follow_up(result):
        requests.post(user_activity_log_url, json={'activity': user_action, 'data': result})

    def _action():
        result = callback_fn()    # json
        _action_follow_up(result)

    return _action
