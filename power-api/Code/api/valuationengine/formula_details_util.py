from . import config
from . import connect_api_util as connect_util
from . import constants as const


def _get_formula_detail(headers, formula_expression):
    formula_ids = [formula_expression]
    body = connect_util.form_filter_criteria(
        "_id", formula_ids, excludes=const.FORMULA_EXCLUDES)
    response = connect_util._get(
        config.FORMULA_DETAILS_URL, headers, body=body)
    return response


def get_formula_details(headers, formula_ids):
    """Get formula details from connect db for formula ids"""
    body = connect_util.form_filter_criteria(
        "_id", formula_ids, excludes=const.FORMULA_EXCLUDES)
    response = connect_util._get(
        config.FORMULA_DETAILS_URL, headers, body=body)

    return response


def get_formula_details_all(headers):
    response = connect_util._get(
        config.FORMULA_DETAILS_URL, headers)
    return response
