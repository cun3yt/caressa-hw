from settings import USER_ACTIVITY_LOG


def button_action(user_action, callback_fn, client, user_activity_log_url=USER_ACTIVITY_LOG):
    """
    This is a wrapper for actual button callback function

    :param user_action: Definition of the action done on the button, e.g. 'press.volume'
    :param callback_fn: Callback function of the button that does the actual work
    :param client: AudioClient to make actual HTTP POST request
    :param user_activity_log_url: End point for logging
    :return:
    """
    
    def _action():
        result = callback_fn()    # json
        client.post_button_action(user_activity_log_url, method='POST',
                                  body={'activity': user_action, 'data': result})

    return _action
