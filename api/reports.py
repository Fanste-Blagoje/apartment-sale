from flask import current_app

import schema
from core import flask_api
from datetime import datetime, date, timedelta
import flask
import flask_restful

import models
from utils import decorators


@flask_api.resource('/report/apartments_number/statuses')
class ApartmentsNumberStatuses(flask_restful.Resource):
    """Get report of apartments number for given status in given date"""
    @staticmethod
    @decorators.check_session_role()
    def get():
        validated_data = schema.StartEndDateRequestSchema().load(flask.request.args or {})

        response = list()

        # Get apartments by statuses at given date period
        reserved, sold, available = models.Apartment.get_by_status_and_date_period(
            start_date=validated_data.get('start_date', date.today() - timedelta(days=30)),
            end_date=validated_data.get('end_date', date.today() + timedelta(days=1))
        )

        response.append({
            'reserved': len(reserved),
            'sold': len(sold),
            'available': len(available)
        })

        return response


@flask_api.resource('/report/sold_apartments/price_difference')
class SoldApartmentsPrice(flask_restful.Resource):
    """Get report of sold apartments and difference price for given date period"""
    @staticmethod
    @decorators.check_session_role()
    def get():
        validated_data = schema.StartEndDateRequestSchema().load(flask.request.args or {})

        response = list()

        # Get purchased apartments
        apartments = models.Contract.get_purchased_apartments(
            start_date=validated_data.get('start_date', date.today() - timedelta(days=30)),
            end_date=validated_data.get('end_date', date.today() + timedelta(days=1))
        )

        purchased_apartments = []
        for apartment in apartments:
            purchased_apartments.append({
                'price_difference': apartment.apartment.price - apartment.price
            })

        sold_sum = sum(key['price_difference'] for key in purchased_apartments)

        response.append({
            'number_of_sold': len(apartments),
            'price_difference': sold_sum
        })

        return response


@flask_api.resource('/report/customer/potential_apartments')
class CustomerPotentialApartments(flask_restful.Resource):
    """Get report for all customers potential apartments"""
    @staticmethod
    @decorators.check_session_role()
    def get():
        validated_data = schema.ContractOptionalRequestSchema().load(flask.request.args or {})

        apartments = models.Apartment.get_potential_apartments_by_customer(
            customer_id=validated_data.get('customer_id')
        )

        return schema.ApartmentSchema(many=True).dump(apartments)


@flask_api.resource('/report/realized_purchases')
class RealizedPurchases(flask_restful.Resource):
    """Get report for realized purchases of given customer"""
    @staticmethod
    @decorators.check_session_role()
    def get():
        validated_data = schema.ContractOptionalRequestSchema().load(flask.request.args or {})

        contracts = models.Contract.get_purchases_by_customer(
            customer_id=validated_data.get('customer_id'),
            start_date=validated_data.get('start_date', date.today() - timedelta(days=30)),
            end_date=validated_data.get('end_date', date.today() + timedelta(days=1))
        )

        return schema.ContractSchema(many=True).dump(contracts)

