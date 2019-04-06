from settings import USER_ACTIVITY_LOG

from logger import get_logger

from conditional_imports import get_button_dependencies

Thread = get_button_dependencies()

logger = get_logger()


def _post_user_action(client, user_activity_log_url, data: dict):   # pragma: no cover
    client.post_button_action(user_activity_log_url, method='POST', body=data)


def button_action(user_action, callback_fn, client, user_activity_log_url=USER_ACTIVITY_LOG):
    """
    This is a wrapper for actual button callback function

    :param user_action: Definition of the action done on the button, e.g. 'press.volume'
    :param callback_fn: Callback function of the button that does the actual work
    :param client: AudioClient to make actual HTTP POST request
    :param user_activity_log_url: End point for logging
    :return:
    """

    def action():
        try:
            result = callback_fn()    # json
        except Exception as ex:
            error_message = "Unexpected Error: {}".format(ex)
            logger.error(error_message)
            data = {'activity': user_action, 'error': error_message}
            Thread(target=_post_user_action, args=(client, user_activity_log_url, data, )).start()
        else:
            data = {'activity': user_action, 'data': result}
            Thread(target=_post_user_action, args=(client, user_activity_log_url, data, )).start()

    return action
