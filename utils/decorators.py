import errors

import flask
import flask_restful
import functools

import models


def _get_user_by_session_id():
    """
    Method is used for checking if session is valid(sessions are valid for one day only)
    :return:
    """
    # If session_id is not send return error
    session_id = flask.request.headers.get('session-id')
    if not session_id:
        flask_restful.abort(404, error=errors.ERR_MISSING_SESSION_ID)

    # Get logged in user
    user_session = models.UserSession.get_by_session_id(session_id=session_id)
    if not user_session:
        flask_restful.abort(404, error=errors.ERR_SESSION_NOT_VALID)

    return user_session.user


def _check_role(role, permissions, exclude=False):
    """
    Check is role in permissions or is it excluded from permissions
    :param role:
    :param permissions:
    :param exclude:
    :return:
    """
    if not exclude and role not in permissions:
        flask_restful.abort(403, error=errors.ERR_BAD_ROLE)
    if exclude and role in permissions:
        flask_restful.abort(403, error=errors.ERR_BAD_ROLE)


def check_session_role(*permissions, exclude=False, check_role=False, return_user=False):
    """
    :param permissions:
    :param exclude:
    :param return_user:
    :param check_role:
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def _decorated(*args, **kwargs):
            # Get current user if session is valid
            current_user = _get_user_by_session_id()

            if check_role:
                # Check if user role is valid for given permissions
                _check_role(role=current_user.role, permissions=permissions, exclude=exclude)

            if return_user:
                response = func(current_user, *args, **kwargs)
            else:
                response = func(*args, **kwargs)

            return response

        return _decorated
    return decorator
