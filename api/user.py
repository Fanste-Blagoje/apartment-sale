from api import EMPTY_RESPONSE
from core import flask_api, db
import flask
import flask_restful
import models
import schema
import base64
import json
from datetime import date, timedelta, datetime
import errors
from utils import general, decorators


@flask_api.resource('/user/import')
class UserImportLogin(flask_restful.Resource):
    @staticmethod
    def get():

        for i in ('Elena Lemonis', 'Stefan Blagojevic', 'Zivota Djokic', 'Nebojsa Ilic', 'Milic Vojinovic', 'Uros Varicak'):
            user = models.User.create(
                **{
                    'first_name': i.split(' ')[0],
                    'last_name': i.split(' ')[1],
                    'username': '{}.factoryww'.format(i.replace(' ', '.').lower()),
                    'password': 'password'
                }
            )
            db.session.add(user)
        db.session.commit()


@flask_api.resource('/user/register')
class UserRegisterResource(flask_restful.Resource):
    @staticmethod
    def post():
        validated_data = schema.UserPasswordConfirmSchema().load(flask.request.json or {})

        user = models.User.get_by_username(username=validated_data.get('username'))

        if user:
            flask_restful.abort(400, error=errors.ERR_USERNAME_ALREADY_EXISTS)

        if validated_data['password'] != validated_data['password_confirm']:
            flask_restful.abort(400, error=errors.ERR_BAD_PASSWORD_CONFIRMATION)

        user = models.User.create(**validated_data)

        user.edit(password=general.generate_password(user=user))

        return schema.UserSchema(many=False).dump(user)


@flask_api.resource('/user/login')
class UserLoginResource(flask_restful.Resource):
    @staticmethod
    def post():
        validated_data = schema.UserLoginRequestSchema().load(flask.request.json or {})

        user = models.User.get_by_username_and_password(
            username=validated_data.get('username'),
            password=validated_data.get('password')
        )

        if not user:
            flask_restful.abort(400, error=errors.ERR_BAD_CREDENTIALS)

        if user:
            try:
                # Decode location object
                location = json.loads(base64.b64decode(validated_data.get('location')).decode('latin1'))

                # Check timeStamp validity, need to be between current time + 1 and -1
                start_timestamp = datetime.timestamp(datetime.today() - timedelta(minutes=1))
                end_timestamp = datetime.timestamp(datetime.today() + timedelta(minutes=1))
                location_timestamp = location.get('timeStamp')

                if start_timestamp < location_timestamp or location_timestamp < end_timestamp:
                    flask_restful.abort(400, error=errors.ERR_TOKEN_EXPIRED)
            except Exception as e:
                print('ERROR', e)

        user_schema = schema.UserSchema(many=False).dump(user)

        # Generate session-id and save into db
        user_schema['session-id'] = general.generate_and_update_user_session_key(user=user)
        models.user.UserSession.create(**{'user_id': user.id, 'session_id': user_schema['session-id']})

        # Set time stamp at the end of day when it expires
        user_schema['session_expire'] = datetime.timestamp(datetime.today().replace(hour=23, minute=59) +
                                                           timedelta(hours=3))

        return user_schema


@flask_api.resource('/user/logout')
class UserLogoutResource(flask_restful.Resource):
    @staticmethod
    def post():
        """
        Logout user
        :param:
        :return:
        """

        session = models.UserSession.get_by_session_id(session_id=flask.request.headers.get('session_id'))

        if session:
            session.edit(deleted=True)

        return EMPTY_RESPONSE


@flask_api.resource('/user/session')
class StaffUserSessionResource(flask_restful.Resource):
    @staticmethod
    def get():
        session_id = flask.request.headers.get('session-id')
        user_session = models.UserSession \
            .get_by_session_id(session_id=session_id)
        if user_session:
            user_schema = schema.UserSchema(many=False).dump(user_session.user)
            user_schema['session-id'] = session_id

            return user_schema

        flask_restful.abort(400, error=errors.ERR_BAD_SESSION_ID)


@flask_api.resource('/user', '/user/<int:user_id>')
class UserResource(flask_restful.Resource):
    @staticmethod
    @decorators.check_session_role()
    def get(user_id=None):
        """
        Get user by id or all users
        :param user_id:
        :return:
        """
        if user_id:
            return schema.UserSchema(many=False).dump(models.User.get_by_id(user_id))

        return schema.UserSchema(many=True).dump(models.User.get_all())

    @staticmethod
    @decorators.check_session_role(models.UserRoleEnum.admin, check_role=True)
    def post():
        """
        Create user by given data
        :return:
        """
        validated_data = schema.UserRequiredRequestSchema().load(flask.request.json or {})

        # Create user
        user = models.User.create(**validated_data)

        return schema.UserSchema(many=False).dump(user)

    @staticmethod
    @decorators.check_session_role(models.UserRoleEnum.admin,
                                   models.UserRoleEnum.salesman,
                                   models.UserRoleEnum.finance,
                                   check_role=True,
                                   return_user=True)
    def patch(current_user, user_id):
        """
        Edit user for given user_id
        :params user_id, current_user:
        :return:
        """
        validated_data = schema.UserEditRequestSchema().load(flask.request.json or {})

        user = general.get_object_by_id(
            obj_id=user_id,
            query_model=models.User,
            error=errors.ERR_BAD_USER_ID
        )

        user_roles = models.UserRoleEnum

        if current_user.role in [user_roles.finance, user_roles.salesman] and current_user.id != user_id:
            flask_restful.abort(400, error=errors.ERR_USER_CANT_EDIT)

        user.edit(**validated_data)

        return schema.UserSchema(many=False).dump(user)

    @staticmethod
    @decorators.check_session_role(models.UserRoleEnum.admin, check_role=True)
    def delete(user_id):
        """
        Delete user for given user id
        """
        user = general.get_object_by_id(
                obj_id=user_id,
                query_model=models.User,
                error=errors.ERR_BAD_USER_ID
            )

        user.edit(deleted=True)

        return EMPTY_RESPONSE
