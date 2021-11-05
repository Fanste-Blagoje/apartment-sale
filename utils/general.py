from datetime import datetime

import flask

import flask_restful

import hashlib


def get_object_by_id(obj_id, query_model, error):
    """
    This method is getting photo by id.
    :param obj_id: Id of object
    :param query_model: model which need to be queried example(model.User, model.UserGallery)
    :param error: which error will be returned if object is not found
    :return:ERR_BAD_{model name}_ID: If photo does not exist for given photo_id
            object: for given photo_id
    """
    # Return object if exist otherwise return error
    return query_model.get_by_id(obj_id) or flask_restful.abort(400, error=error)


def generate_session_id(user):
    """

    :param user:
    :return:
    """
    # Generate session id from user_id and utc time
    return hashlib.sha512("{}/{}".format(user.id, datetime.utcnow()).encode("UTF-8")).hexdigest()


def generate_token(user, token_length=20):
    """

    :param user:
    :param token_length:
    :return:
    """
    return hashlib.sha512("{}/{}/{}".format(user.first_name, user.last_name, datetime.utcnow())
                          .encode("UTF-8")).hexdigest()[:token_length]


def generate_and_update_user_session_key(user):
    import hashlib

    user_session_key = hashlib.sha512("{}/{}".format(user.id, datetime.utcnow()).encode("UTF-8")).hexdigest()

    session_key = "{}:{}:{}".format("sess", user.id, user_session_key)

    return session_key


def generate_password(user):
    """

    :param user:
    :return:
    """
    return hashlib.sha512("{}".format(user.password).encode('UTF-8')).hexdigest()