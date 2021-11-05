from datetime import datetime

from core import db


def add_filters_to_query(cls_model, search_query, like=False, allow_none=False, **kwargs):
    """
    This method add filters for all kwargs parameters if they exist in cls_model
    :param cls_model:
    :param search_query:
    :param like: used for string exact search. For front_desk and gym_manager role
    :param allow_none:
    :param kwargs:
    :return:
    """
    # Add filters to search
    for attr, value in kwargs.items():
        if getattr(cls_model, attr, None) and (value is not None or allow_none):
            if 'date_of_creation' == attr:
                search_query = search_query.filter(db.cast(getattr(cls_model, attr), db.Date) == value)
            elif attr in ['id', 'role'] or '_id' in attr or isinstance(value, bool) or not like:
                search_query = search_query.filter(getattr(cls_model, attr) == value)
            else:
                search_query = search_query.filter(getattr(cls_model, attr).like("%{}%".format(value)))
    return search_query
