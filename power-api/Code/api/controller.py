from flask import Flask, request, jsonify, Response
from .valuationengine import trade_details_util as trade_util
from .valuationengine import constants as const
from .valuationengine import formula_details_util as formula_util
from .valuationengine import valuate
from .valuationengine import pricing_api_util
from .valuationengine import config
from .valuationengine import live_price_processor
from .uiAPIs.shape_config_api import shapeConfigApi
import json
import logging

def startApp():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    stream_handler =  logging.StreamHandler()
    app.logger.addHandler(stream_handler)

    app.register_blueprint(shapeConfigApi)

    if __name__ != '__main__':
        gunicorn_error_handlers = logging.getLogger('gunicorn.error').handlers
        app.logger.handlers.extend(gunicorn_error_handlers)
        app.logger.info('extended gunicorn error log - test log')
    
    @app.route('/')
    def default_route():
        """Default route"""
        app.logger.debug('this is a DEBUG message')
        app.logger.info('this is an INFO message')
        app.logger.warning('this is a WARNING message')
        app.logger.error('this is an ERROR message')
        app.logger.critical('this is a CRITICAL message')
        return jsonify('hello world')

    @app.route("/testHeader")
    def testHeader():
        app.logger.info('in main controller - testHeader api - json dumps')
        test = json.dumps({'working': 'API is working with json dumps'})
        r = Response(response=test, status=200, mimetype='application/json')
        r.headers["Content-Type"] = "application/json"
        return r

    @shapeConfigApi.route('/testHeader2', methods=['POST'])
    def testJsonDumps():
        app.logger.info('in testHeader2 - json dumps')
        test = json.dumps({'working': 'testing with Response and headers app/json'})
        r = Response(response=test, status=200, mimetype='application/json')
        r.headers["Content-Type"] = "application/json"
        return r

    @app.route("/testHeader3", methods=["POST"])
    def testHeader3():
        app.logger.info('in testHeader3 - returning jsonify response')
        test = {'working': 'API is working with json dumps jsonify'}
        return jsonify(test)

    @app.route("/contract/general", methods=["POST"])
    def get_contract_general_details():
        """Get contract general details"""
        headers = request.headers

        contract_ref_no = __get_property_from_request(
            request, const.K_CONTRACT_NO)
        response = trade_util._get_contract(
            headers, contract_ref_no)

        return jsonify(response)

    @app.route("/contract/general/filter", methods=["POST"])
    def get_contract_general_details_filter():
        """Get contract general details"""
        headers = request.headers

        contract_ref_nos = __get_property_from_request(
            request, const.K_CONTRACT_NOS)
        response = trade_util._get_contracts(
            headers, contract_ref_nos)

        return jsonify(response)

    @app.route("/contract/general/all", methods=["POST"])
    def get_contract_general_details_all():
        """Get all contract general details"""
        headers = request.headers

        response = trade_util._get_contract_all(
            headers)

        return jsonify(response)

    @app.route("/contract/item", methods=["POST"])
    def get_contract_item():
        """Get contract item details"""
        headers = request.headers

        contract_ref_no = __get_property_from_request(
            request, const.K_CONTRACT_NO)
        response = trade_util._get_contract_item(
            headers, contract_ref_no)

        return jsonify(response)

    @app.route("/contract/items", methods=["POST"])
    def get_contract_items():
        """Get contract item details"""
        headers = request.headers

        contract_ref_nos = __get_property_from_request(request,
                                                       const.K_CONTRACT_NOS)
        response = trade_util._get_contract_items(
            headers, contract_ref_nos)

        return jsonify(response)

    @app.route("/contract/item/all", methods=["POST"])
    def get_contract_item_all():
        """Get contract item details"""
        headers = request.headers

        response = trade_util._get_contract_item_all(
            headers)

        return jsonify(response)

    @app.route("/formula", methods=["POST"])
    def get_formula_details():
        """Get formula details"""
        headers = request.headers

        formula_ids = __get_property_from_request(request, const.K_FORMULA_IDS)
        response = formula_util.get_formula_details(headers, formula_ids)

        return jsonify(response)

    @app.route("/formula/all", methods=["POST"])
    def get_formula_details_all():
        """Get formula details"""
        headers = request.headers

        response = formula_util.get_formula_details_all(headers)

        return jsonify(response)

    @app.route("/valuation/run", methods=["POST"])
    def run_valuation():
        """Get formula details"""
        headers = request.headers
        valuation_date = __get_property_from_request(
            request, const.K_VALUATION_RUN_DATE)
        response = valuate.run_valuation(headers, valuation_date)

        return jsonify(response)

    @app.route("/valuation/items", methods=["POST"])
    def get_valuation_delivery_items():
        """Get formula details"""
        headers = request.headers

        response = valuate.get_delivery_items_for_valuation(headers, None)

        return jsonify(response)

    @app.route("/deliveryunit/price/lambda", methods=["POST"])
    def get_deliveryunit_price():
        """Get price for delivery unit"""

        delivery_unit = request.get_json()
        # print(delivery_unit)
        # print(config.PRICING_API_URL)

        response = pricing_api_util._post(
            config.VALUATION_API_URL, body=delivery_unit)

        return jsonify(response)

    @app.route("/item/liveprice", methods=["POST"])
    def get_live_price():
        """Get live price for contract item on create & update operation"""
        headers = request.headers
        item_versions = request.get_json()
        item_return = live_price_processor.process_item_price(
            headers, item_versions)
        return jsonify(item_return)

    def __get_property_from_request(request, property):
        request_data = request.get_json()
        property_value = None
        if property in request_data:
            property_value = request_data[property]
        return property_value

    # if __name__ == "__main__":
    #     app.run(host='0.0.0.0', port=8080, debug=True)
    return app
