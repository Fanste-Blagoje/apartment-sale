from marshmallow import validate
from core import ma
import marshmallow
import models
from marshmallow_enum import EnumField


####################
# REQUEST SCHEMAS #
####################
class UserLoginRequestSchema(ma.Schema):
    username = marshmallow.fields.Str(required=True)
    password = marshmallow.fields.Str(required=True)
    location = marshmallow.fields.Str()


class UserPasswordConfirmSchema(UserLoginRequestSchema):
    password_confirm = marshmallow.fields.Str(required=True)
    first_name = marshmallow.fields.Str(required=True)
    last_name = marshmallow.fields.Str(required=True)


class UserRequiredRequestSchema(UserLoginRequestSchema):
    first_name = marshmallow.fields.Str(required=True)
    last_name = marshmallow.fields.Str(required=True)
    role = marshmallow.fields.Str(required=True)


class UserEditRequestSchema(ma.Schema):
    username = marshmallow.fields.Str()
    password = marshmallow.fields.Str()
    first_name = marshmallow.fields.Str()
    last_name = marshmallow.fields.Str()
    role = marshmallow.fields.Str()


class CustomerRequestSchema(ma.Schema):
    name = marshmallow.fields.Str(required=True)
    type = marshmallow.fields.Str(required=True)
    email = marshmallow.fields.Str(required=True)
    phone = marshmallow.fields.Str()
    pib_jmbg = marshmallow.fields.Str()
    address = marshmallow.fields.Str()


class CustomerEditRequestSchema(ma.Schema):
    name = marshmallow.fields.Str()
    type = marshmallow.fields.Str()
    email = marshmallow.fields.Str()
    phone = marshmallow.fields.Str()
    pib_jmbg = marshmallow.fields.Str()
    address = marshmallow.fields.Str()


class ApartmentRequestSchema(ma.Schema):
    lamella = marshmallow.fields.Str(required=True)
    square_footage = marshmallow.fields.Int(required=True)
    floor = marshmallow.fields.Int(required=True)
    rooms = marshmallow.fields.Int(required=True)
    price = marshmallow.fields.Int(required=True)
    orientation = marshmallow.fields.Str()
    balconies = marshmallow.fields.Int()
    status = marshmallow.fields.Str()


class ApartmentFilterRequestSchema(ma.Schema):
    lamella = marshmallow.fields.Str()
    square_footage = marshmallow.fields.Int()
    floor = marshmallow.fields.Int()
    rooms = marshmallow.fields.Int()
    orientation = marshmallow.fields.Str()
    balconies = marshmallow.fields.Int()
    price = marshmallow.fields.Int()
    status = marshmallow.fields.Str()


class ContractOptionalRequestSchema(ma.Schema):
    apartment_id = marshmallow.fields.Int()
    user_id = marshmallow.fields.Int()
    customer_id = marshmallow.fields.Int()
    payment_method = marshmallow.fields.Str()
    first_visit = marshmallow.fields.Date()
    status = marshmallow.fields.Str()
    approved_by = marshmallow.fields.Int()
    approved = marshmallow.fields.Bool()
    signed = marshmallow.fields.Bool()
    note = marshmallow.fields.Str()


class ContractEditRequestSchema(ContractOptionalRequestSchema):
    contract_number = marshmallow.fields.Str()
    price = marshmallow.fields.Int()


class ContractRequiredRequestSchema(ContractOptionalRequestSchema):
    contract_number = marshmallow.fields.Str(required=True)
    price = marshmallow.fields.Int(required=True)


####################
# RESPONSE SCHEMAS #
####################
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.User

    role = EnumField(models.user.UserRoleEnum)


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Customer

    type = EnumField(models.user.CustomerTypeEnum)


class ApartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Apartment

    status = EnumField(models.user.ApartmentStatusEnum)
    orientation = EnumField(models.user.ApartmentOrientationEnum)


class ContractSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Contract

    user = ma.Nested(UserSchema)
    customer = ma.Nested(CustomerSchema)
    payment_method = EnumField(models.user.PaymentMethodEnum)
    status = EnumField(models.user.CustomerApartmentStatusEnum)