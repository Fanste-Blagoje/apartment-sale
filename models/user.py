from core import db
from datetime import datetime, date, timedelta
from models.base_model import BaseModel
import enum
from sqlalchemy.ext.declarative import declared_attr


class UserRoleEnum(enum.Enum):
    admin = 'admin'
    salesman = 'salesman'
    finance = 'finance'


class ApartmentOrientationEnum(enum.Enum):
    north = 'north'
    south = 'south'
    west = 'west'
    east = 'east'


class ApartmentStatusEnum(enum.Enum):
    available = 'available'
    reserved = 'reserved'
    sold = 'sold'


class CustomerTypeEnum(enum.Enum):
    individual = 'individual'
    legal_entity = 'legal_entity'


class CustomerApartmentStatusEnum(enum.Enum):
    potential = 'potential'
    reserved = 'reserved'
    purchased = 'purchased'


class PaymentMethodEnum(enum.Enum):
    cash = 'cash'
    credit = 'credit'
    on_installment = 'on_installment'
    participation = 'participation'


class User(db.Model, BaseModel):
    """User model"""
    __tablename__ = 'tbl_user'

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.deferred(db.Column(db.Text))
    role = db.Column(db.Enum(UserRoleEnum), default=UserRoleEnum.salesman, nullable=False)

    # contracts = db.relationship('Contract', back_populates='user')

    @classmethod
    def get_by_username_and_password(cls, username, password):
        return cls.query.filter(cls.username == username, cls.password == password, ~cls.deleted).first()

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter(cls.username == username, ~cls.deleted).first()


class UserSession(db.Model, BaseModel):
    """
    Model for User session
    """
    __tablename__ = 'tbl_user_session'

    user_id = db.Column(db.Integer, db.ForeignKey('tbl_user.id'), nullable=False)
    session_id = db.Column(db.String(150), nullable=False)
    session_date = db.Column(db.Date, default=date.today())

    user = db.relationship('User')

    @classmethod
    def get_by_session_id(cls, session_id):
        return cls.query.filter(
            cls.session_id == session_id,
            db.cast(cls.date_of_creation, db.Date) == date.today(),
            ~cls.deleted
        ).first()


class Apartment(db.Model, BaseModel):
    """Model for apartment"""
    __tablename__ = 'tbl_apartment'

    lamella = db.Column(db.String(20), nullable=False)
    square_footage = db.Column(db.Integer, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    orientation = db.Column(db.Enum(ApartmentOrientationEnum), default=ApartmentOrientationEnum.north, nullable=False)
    balconies = db.Column(db.Integer, default=0, server_default='0')
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(ApartmentStatusEnum), default=ApartmentStatusEnum.available, nullable=False)
    photo = db.Column(db.Text)

    contracts = db.relationship('Contract', back_populates='apartment')

    @classmethod
    def get_by_filters(cls, lamella, square_footage, floor, rooms, orientation, balconies, price, status):
        apartments = cls.query.filter(~cls.deleted)

        if lamella:
            apartments = apartments.filter(cls.lamella == lamella)

        if square_footage:
            apartments = apartments.filter(cls.square_footage == square_footage)

        if floor:
            apartments = apartments.filter(cls.floor == floor)

        if orientation:
            apartments = apartments.filter(cls.orientation == orientation)

        if rooms:
            apartments = apartments.filter(cls.rooms == rooms)

        if balconies:
            apartments = apartments.filter(cls.balconies == balconies)

        if price:
            apartments = apartments.filter(cls.price >= price)

        if status:
            apartments = apartments.filter(cls.status == status)

        return apartments.all()


class Customer(db.Model, BaseModel):
    """Model for customer"""
    __tablename__ = 'tbl_customer'

    type = db.Column(db.Enum(CustomerTypeEnum), default=CustomerTypeEnum, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True)
    pib_jmbg = db.Column(db.String(14), unique=True)
    address = db.Column(db.String(50))

    contracts = db.relationship('Contract', back_populates='customer')


class Contract(db.Model, BaseModel):
    """Model for apartment customers contract"""
    __tablename__ = 'tbl_contract'

    apartment_id = db.Column(db.Integer, db.ForeignKey('tbl_apartment.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('tbl_customer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('tbl_user.id'))
    first_visit = db.Column(db.Date, default=date.today())
    status = db.Column(db.Enum(CustomerApartmentStatusEnum), default=CustomerApartmentStatusEnum.potential, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('tbl_user.id'))
    approved = db.Column(db.Boolean, default=False, server_default=db.false(), nullable=False)
    contract_number = db.Column(db.String(30), unique=True, nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethodEnum), default=PaymentMethodEnum.cash, nullable=False)
    signed = db.Column(db.Boolean, default=False, server_default=db.false(), nullable=False)

    approval = db.relationship('User', foreign_keys=[approved_by])
    user = db.relationship('User', foreign_keys=[user_id])
    apartment = db.relationship('Apartment', back_populates='contracts')
    customer = db.relationship('Customer', back_populates='contracts')

    @classmethod
    def get_by_customer_and_apartment_with_contract(cls, customer_id, apartment_id, contract_id):
        return cls.query.filter(
            cls.customer_id == customer_id,
            cls.apartment_id == apartment_id,
            cls.id == contract_id,
            ~cls.deleted
        ).first()

    @classmethod
    def get_by_contract_number(cls, contract_number):
        return cls.query.filter(cls.contract_number == contract_number, ~cls.deleted).first()

    @classmethod
    def get_apartments_by_customer(cls, customer_id):
        return cls.query.filter(cls.customer_id == customer_id, ~cls.deleted).all()

    @classmethod
    def get_customers_by_apartment(cls, apartment_id):
        return cls.query.filter(cls.apartment_id == apartment_id, ~cls.deleted).all()
