from core import db
from datetime import datetime, date
from dateutil import parser

import flask_restful
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declared_attr


class NotSQLAlchemyObjectError(Exception):
    pass


def edit_sqlalchemy_object(obj, set_nulls=False, **kwargs):
    """
    :param obj:
    :param set_nulls:
    :param kwargs:
    :return:
    """
    if not hasattr(obj, '__table__'):
        raise NotSQLAlchemyObjectError('object must have __table__ property')
    try:
        for arg in kwargs:
            if hasattr(obj, arg) and (set_nulls or kwargs.get(arg) is not None) and arg in obj.__table__.c:
                if kwargs.get(arg) in ['true', 'false', 'True', 'False']:
                    setattr(obj, arg, kwargs.get(arg) in ['true', 'True'])
                elif obj.__table__.c[arg].type.python_type in [datetime, date]:
                    if type(kwargs.get(arg)) == str:
                        setattr(obj, arg, parser.parse(kwargs.get(arg)))
                    elif type(kwargs.get(arg) in [date, datetime]):
                        setattr(obj, arg, kwargs.get(arg))
                    elif set_nulls and kwargs.get(arg) is None:
                        setattr(obj, arg, kwargs.get(arg))
                    else:
                        pass
                elif type(kwargs.get(arg)) == list and type(obj.__table__.c[arg].type) == db.JSON:
                    setattr(obj, arg, kwargs.get(arg))
                else:
                    if kwargs.get(arg) is None:
                        if set_nulls:
                            setattr(obj, arg, None)
                    else:
                        setattr(obj, arg, obj.__table__.c[arg].type.python_type(kwargs.get(arg)))

        db.session.add(obj)

        # If object is creating add date
        if not obj.date_of_creation:
            obj.date_of_creation = datetime.today()

        # Update date_of_update field
        if hasattr(obj, 'date_of_update'):
            setattr(obj, 'date_of_update', datetime.today())

        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        print('IntegrityError EDIT METHOD - ', err)
        flask_restful.abort(400, error=get_error(error_obj=err))


class BaseModel(object):
    """
    Base object model
    """
    # FIELDS #
    @declared_attr
    def id(self):
        return db.Column(db.Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def date_of_creation(self):
        return db.deferred(db.Column(db.DateTime, nullable=False, server_default=func.now()))

    @declared_attr
    def date_of_update(self):
        return db.deferred(
            db.Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now()))

    @declared_attr
    def deleted(self):
        return db.deferred(db.Column(db.Boolean, server_default=db.false(), default=False))

    # EDIT AND CREATE METHODS #
    def edit(self, set_nulls=False, **kwargs):
        if isinstance(self, db.Model):
            edit_sqlalchemy_object(self, set_nulls, **kwargs)

    @classmethod
    def create(cls, **kwargs):
        create_obj = cls()
        edit_sqlalchemy_object(create_obj, **kwargs)
        # create_obj.date_of_creation = datetime.utcnow()
        return create_obj

    @classmethod
    def get_by_id(cls, _id):
        if hasattr(cls, "query"):
            return cls.query.get(_id)

    @classmethod
    def get_all(cls):
        if hasattr(cls, "query"):
            return cls.query.filter(~cls.deleted).order_by(cls.date_of_creation.desc()).all()


def get_error(error_obj):
    """
    Method used for getting db IntegrityError, try to get duplicated key (ERR_DUPLICATED_EMAIL, ...) error or return
    general error ERR_DUPLICATED_ENTRY
    :param error_obj:
    :return:
    """
    try:
        str_error = str(error_obj.__dict__.get('orig')).split('\'')[-2].split('.')[1]
        return 'ERR_DUPLICATED_{}'.format(str_error.upper())
    except:
        return 'ERR_DUPLICATED_ENTRY'

