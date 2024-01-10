import json
import time

import requests

from client_consts import node_url, node_pass, headers
from consts import DOUBLE_SPENDING_ATTEMPT, HTTP_OK, ERROR
from helpers.generic_calls import logger, get_request


def unlock_wallet():
    response = requests.post(f"{node_url}/wallet/unlock", json={"pass": node_pass}, headers=headers)
    logger.debug(f"Unlock wallet response status code: {response.status_code}")
    return response.status_code

def current_height():
    return json.loads(get_request(node_url + "/blocks/lastHeaders/1").text)[0]['height']

def sign_tx(tx):
    """
    Signs a transaction by sending it to the node, then logs and returns the response.

    This function makes a POST request to the "/wallet/transaction/send" endpoint of the node with
    the given transaction. It logs the full text of the response and its status code, and then prints them.
    If the response text contains "Double spending attempt", it returns a predefined error code for that.
    If the status code is not 200, it returns a generic error code.
    If the status code is 200, it attempts to parse the response text as JSON and return it.

    If a requests exception occurs during the POST request, it is logged and a generic error code is returned.
    If a JSON decoding error occurs when parsing the response, it is logged and a generic error code is returned.

    :param tx: The transaction to be signed and sent.
    :return: The parsed JSON response if successful, or an error code if not.
    :raises: Does not raise any exceptions, but logs errors and returns error codes.
    """
    try:
        res = requests.post(node_url + "/wallet/transaction/send", json=tx, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.error("Request error: %s", e)
        return ERROR

    logger.debug("Request Response: %s", res.text)
    print(res.text)
    print(res.status_code)

    if "Double spending attempt" in res.text:
        return DOUBLE_SPENDING_ATTEMPT
    elif res.status_code != HTTP_OK:
        return ERROR

    try:
        return json.loads(res.text)
    except json.JSONDecodeError as e:
        logger.error("Failed to decode JSON: %s", e)
        return ERROR

def box_id_to_binary(box_id):
    return json.loads(get_request(node_url + "/utxo/withPool/byIdBinary/" + box_id).text)["bytes"]

def tree_to_address(addr):
    return json.loads(get_request(node_url + "/utils/ergoTreeToAddress/" + addr).text)["address"]

def box_id_to_contents(box_id):
    return json.loads(get_request(node_url + "/utxo/withPool/byId/" + box_id).text)

def sign_and_get_boxids(tx_object):
    sign_response = sign_tx(tx_object)
    if sign_response['status'] != 'success':
        return {"status": "failed", "reason": "Failed to sign the transaction"}

    txId = sign_response['txId']
    time.sleep(5)
    response = requests.get(f"{node_url}/transactions/unconfirmed/byTransactionId/{txId}")
    if response.status_code != 200:
        return {"status": "failed", "reason": "Failed to retrieve the transaction"}

    # Extract boxIds from the outputs of the transaction
    transaction = response.json()
    boxIds = [output['boxId'] for output in transaction['outputs']]

    return {"status": "success", "transaction": transaction, "boxIds": boxIds}
