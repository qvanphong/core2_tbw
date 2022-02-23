from flask import Flask, jsonify, request
from flask_cors import CORS

import math
from util import json
from config.config import Config
from network.network import Network
from util.sql import SnekDB
from util.util import Util

app = Flask(__name__)
CORS(app)


@app.route("/voters", methods=["GET"])
def get_voters():
    req_page = request.args.get('page')
    try:
        _validate_page_param(req_page)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    skip = _get_skip(req_page)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    # Get voters by page and map it to dict for compatible json format
    voters = map(json.voter_to_json, snekdb.voters(limit, skip).fetchall())
    total_voter = snekdb.countVoter().fetchone()[0]
    total_page = int(math.ceil(total_voter / limit))

    result = {
        "total_page": total_page,
        "total": total_voter,
        "result": list(voters)
    }

    return jsonify(result)


@app.route("/voter", methods=["GET"])
def get_voter():
    req_page = request.args.get('page')
    try:
        _validate_page_param(req_page)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    req_address = request.args.get('address')
    if req_address is None:
        return jsonify({"error": "No specific 'address' in parameter."}), 400

    skip = _get_skip(req_page)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)

    # Get voter by address and parse it to dict if result is not None
    voters_by_address = map(json.voter_to_json, snekdb.findVoter(req_address, limit, skip).fetchall())
    total = snekdb.countFindVoter(address=req_address).fetchone()[0]
    total_page = int(math.ceil(total / limit))

    result = {
        "total_page": total_page,
        "total": total,
        "result": list(voters_by_address)
    }

    return jsonify(result), 200


@app.route("/payments", methods=["GET"])
def get_payments():
    req_page = request.args.get('page')
    try:
        _validate_page_param(req_page)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    skip = _get_skip(req_page)

    payments = map(json.payment_to_json, snekdb.groupedPayment(limit, skip).fetchall())
    total = snekdb.countGroupedPayment().fetchone()[0]
    total_page = int(math.ceil(total / limit))

    result = {
        "total_page": total_page,
        "total": total,
        "result": list(payments)
    }

    return jsonify(result), 200


@app.route("/payment", methods=["GET"])
def get_payment():
    req_page = request.args.get('page')
    try:
        _validate_page_param(req_page)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    req_address = request.args.get('address')
    if req_address is None:
        return jsonify({"error": "No specific 'address' in parameter."}), 400

    skip = _get_skip(req_page)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)

    # Get voter by address and parse it to dict if result is not None
    payments_by_address = map(json.voter_to_json, snekdb.findGroupedPayment(req_address, limit, skip).fetchall())
    total = snekdb.countFindGroupedPayment(address=req_address).fetchone()[0]
    total_page = int(math.ceil(total / limit))

    result = {
        "total_page": total_page,
        "total": total,
        "result": list(payments_by_address)
    }

    return jsonify(result), 200


@app.route("/info", methods=["GET"])
def get_delegate_info():
    dstats = client.delegates.get(data.public_key)
    voter_count = client.delegates.voters(data.delegate)

    info = {}

    info['delegate_name'] = data.delegate
    info['voter_share'] = data.voter_share * 100
    info['payout_interval'] = data.interval
    info['payout_time'] = data.interval * 8 * 53
    info['forged'] = dstats['data']['blocks']['produced']
    info['rank'] = dstats['data']['rank']
    info['votes'] = dstats['data']['votes']
    info['total_voters'] = voter_count['meta']['totalCount']

    if data.network in ['ark_mainnet', 'ark_devnet']:
        info['forging'] = info['rank'] <= 51
        info['total_delegate'] = 51

    if data.network in ['solar_devnet']:
        info['forging'] = info['rank'] <= 53
        info['total_delegate'] = 53

    return jsonify(info)


def _validate_page_param(req_page):
    if req_page is None:
        raise Exception("No specific 'page' in parameter.")

    if not req_page.isnumeric() or int(req_page) < 1:
        raise Exception("Incorrect 'page' parameter.")


def _get_skip(req_page):
    skip = (int(req_page) - 1) * limit

    return skip


if __name__ == '__main__':
    limit = 20

    data = Config()
    network = Network(data.network)
    u = Util(data.network)
    client = u.get_client(network.api_port, "194.233.86.213")

    app.run()
