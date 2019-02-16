def deep_get(dict_, key, default_value=None):
    try:
        keys = key.split('.')
        iterative_dict = dict_
        for k in keys:
            iterative_dict = iterative_dict[k]
        return iterative_dict
    except (KeyError, AttributeError, TypeError, ):
        return default_value


def ui(_o):     # pragma: no cover
    print("\n".join([ind for ind in dir(_o) if ind[0] != '_']))
