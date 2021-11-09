from api import EMPTY_RESPONSE
from core import flask_api, db
import flask
import flask_restful
import models
import schema
from datetime import date, timedelta, datetime
import errors
from utils import general, decorators


@flask_api.resource('/apartment', '/apartment/<int:apartment_id>')
class ApartmentResource(flask_restful.Resource):
    @staticmethod
    @decorators.check_session_role()
    def get(apartment_id=None):
        """
        Get apartment by id or all apartments
        :param apartment_id:
        :return:
        """
        if apartment_id:
            return schema.ApartmentSchema(many=False).dump(models.Apartment.get_by_id(apartment_id))

        validated_data = schema.ApartmentFilterRequestSchema().load(flask.request.args or {})

        apartments = models.Apartment.get_by_filters(
            lamella=validated_data.get('lamella'),
            square_footage=validated_data.get('square_footage'),
            floor=validated_data.get('floor'),
            balconies=validated_data.get('balconies'),
            status=validated_data.get('status'),
            orientation=validated_data.get('orientation'),
            rooms=validated_data.get('rooms'),
            price=validated_data.get('price'),
        )

        return schema.ApartmentSchema(many=True).dump(apartments)

    @staticmethod
    @decorators.check_session_role(models.UserRoleEnum.admin, check_role=True)
    def post():
        """
        Create apartment by given data
        :return:
        """
        validated_data = schema.ApartmentRequestSchema().load(flask.request.json or {})

        # Create apartment
        apartment = models.Apartment.create(**validated_data)

        return schema.ApartmentSchema(many=False).dump(apartment)

    @staticmethod
    @decorators.check_session_role(models.UserRoleEnum.admin, check_role=True)
    def patch(apartment_id):
        """
        Edit apartment for given apartment id
        :param apartment_id:
        :return:
        """
        validated_data = schema.ApartmentFilterRequestSchema().load(flask.request.json or {})

        apartment = general.get_object_by_id(
            obj_id=apartment_id,
            query_model=models.Apartment,
            error=errors.ERR_BAD_APARTMENT_ID
        )

        # Edit apartment
        apartment.edit(**validated_data)

        return schema.ApartmentSchema(many=False).dump(apartment)

    @staticmethod
    @decorators.check_session_role(models.UserRoleEnum.admin, check_role=True)
    def delete(apartment_id):
        """
        Delete apartment for given apartment id
        """
        apartment = general.get_object_by_id(
                obj_id=apartment_id,
                query_model=models.Apartment,
                error=errors.ERR_BAD_APARTMENT_ID
            )

        # Delete apartment
        apartment.edit(deleted=True)

        return EMPTY_RESPONSE


@flask_api.resource('/customer/<int:customer_id>/apartment')
class CustomerApartmentResource(flask_restful.Resource):
    @staticmethod
    @decorators.check_session_role()
    def get(customer_id):
        """
        Get all apartments for customer
        :param customer_id:
        :return:
        """
        validated_data = schema.ContractOptionalRequestSchema().load(flask.request.args or {})

        apartments = models.Contract.get_apartments_by_customer(
            customer_id=customer_id,
            price=validated_data.get('price'),
            contract_number=validated_data.get('contract_number'),
            first_visit=validated_data.get('first_visit')
        )

        return schema.ContractSchema(many=True).dump(apartments)


@flask_api.resource('/apartment/<int:apartment_id>/customer')
class ApartmentCustomerResource(flask_restful.Resource):
    @staticmethod
    @decorators.check_session_role()
    def get(apartment_id):
        """
        Get all customers for apartment
        :param apartment_id:
        :return:
        """
        validated_data = schema.ContractOptionalRequestSchema().load(flask.request.args or {})

        customers = models.Contract.get_customers_by_apartment(
            apartment_id=apartment_id,
            price=validated_data.get('price'),
            contract_number=validated_data.get('contract_number'),
            first_visit=validated_data.get('first_visit')
        )

        return schema.ContractSchema(many=True).dump(customers)
