import models
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

    @classmethod
    def get_by_filters(cls, user_id, role):
        users = cls.query.filter(~cls.deleted)

        if user_id:
            users = users.filter(cls.id == user_id)
        if role:
            users = users.filter(cls.role == role)

        return users.order_by(cls.date_of_creation.desc()).all()


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

        return apartments.order_by(cls.date_of_creation.desc()).all()

    ##################
    # REPORT METHODS #
    ##################
    @classmethod
    def get_by_status_and_date_period(cls, start_date, end_date):
        apartments = cls.query.filter(~cls.deleted)

        if start_date:
            apartments = apartments.filter(cls.date_of_creation >= start_date)
        if end_date:
            apartments = apartments.filter(cls.date_of_creation <= end_date)

        return apartments.filter(cls.status == 'reserved').all(), \
               apartments.filter(cls.status == 'sold').all(), \
               apartments.filter(cls.status == 'available').all()

    @classmethod
    def get_potential_apartments_by_customer(cls, customer_id):
        return cls.query.join(models.Contract, models.Contract.apartment_id == cls.id)\
            .filter(
                cls.status == 'available',
                models.Contract.customer_id == customer_id,
                models.Contract.status == 'potential',
                ~cls.deleted,
                ~models.Contract.deleted
            )


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

    @classmethod
    def get_by_filters(cls, customer_id, customer_type):
        customers = cls.query.filter(~cls.deleted)

        if customer_id:
            customers = customers.filter(cls.id == customer_id)
        if customer_type:
            customers = customers.filter(cls.type == customer_type)

        return customers.order_by(cls.date_of_creation.desc()).all()


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
    def get_apartments_by_customer(cls, customer_id, price, contract_number, first_visit):
        apartments = cls.query.filter(cls.customer_id == customer_id, ~cls.deleted)

        if price:
            apartments = apartments.filter(cls.price == price)
        if contract_number:
            apartments = apartments.filter(cls.contract_number == contract_number)
        if first_visit:
            apartments = apartments.filter(cls.first_visit == first_visit)

        return apartments.order_by(cls.date_of_creation.desc()).all()

    @classmethod
    def get_customers_by_apartment(cls, apartment_id, price, contract_number, first_visit):
        customers = cls.query.filter(cls.apartment_id == apartment_id, ~cls.deleted)

        if price:
            customers = customers.filter(cls.price == price)
        if contract_number:
            customers = customers.filter(cls.contract_number == contract_number)
        if first_visit:
            customers = customers.filter(cls.first_visit == first_visit)

        return customers.order_by(cls.date_of_creation.desc()).all()

    @classmethod
    def get_by_customer_and_apartment(cls, customer_id, apartment_id):
        return cls.query.filter(cls.customer_id == customer_id, cls.apartment_id == apartment_id, ~cls.deleted).first()

    @classmethod
    def get_issued_by_apartment(cls, apartment_id):
        return cls.query.filter(cls.apartment_id == apartment_id, cls.status != 'potential', ~cls.deleted).all()

    @classmethod
    def get_all_non_customer_by_apartment(cls, apartment_id, customer_id):
        return cls.query.filter(cls.apartment_id == apartment_id, cls.customer_id != customer_id, ~cls.deleted).all()

    ##################
    # REPORT METHODS #
    ##################

    @classmethod
    def get_purchased_apartments(cls, start_date, end_date):
        apartments = cls.query.join(models.Apartment, models.Apartment.id == cls.apartment_id)\
            .filter(cls.status == 'purchased', ~cls.deleted)

        if start_date:
            apartments = apartments.filter(cls.date_of_update >= start_date)
        if end_date:
            apartments = apartments.filter(cls.date_of_update <= end_date)

        return apartments.all()

    @classmethod
    def get_purchases_by_customer(cls, customer_id, start_date, end_date):
        contracts = cls.query.filter(
            cls.status == 'purchased',
            ~cls.deleted
        )

        if customer_id:
            contracts = contracts.filter(cls.customer_id == customer_id)
        if start_date:
            contracts = contracts.filter(cls.date_of_update >= start_date)
        if end_date:
            contracts = contracts.filter(cls.date_of_update <= end_date)

        return contracts.all()
