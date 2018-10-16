# todo OSS this
# todo study `collections` package
import collections
from datetime import timedelta


def sec_to_hours(sec):
    return str(timedelta(seconds=sec))


def deep_get(dict_, key, default_value=None):
    try:
        keys = key.split('.')
        iterative_dict = dict_
        for k in keys:
            iterative_dict = iterative_dict[k]
        return iterative_dict
    except KeyError:
        return default_value
    except AttributeError:
        return default_value


def deep_set(dict_, key, val):
    to_merge = {}
    iterative_dict = to_merge
    keys = key.split('.')
    n = len(keys)

    for k in keys[:(n - 1)]:
        iterative_dict[k] = {}
        iterative_dict = iterative_dict[k]

    last_key = keys[-1]
    iterative_dict[last_key] = val
    return dict_merge(dict_, to_merge)


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def ui(_o):
    print("\n".join([ind for ind in dir(_o) if ind[0] != '_']))
