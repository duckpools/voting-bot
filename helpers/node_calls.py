import json
import time

import requests

from client_consts import node_url, node_pass, headers
from helpers.generic_calls import get_request
from logger import set_logger

logger = set_logger(__name__)


def unlock_wallet():
    response = requests.post(f"{node_url}/wallet/unlock", json={"pass": node_pass}, headers=headers)
    logger.debug(f"Unlock wallet response status code: {response.status_code}")
    return response.status_code

def current_height():
    return json.loads(get_request(node_url + "/blocks/lastHeaders/1").text)[0]['height']

def sign_tx(tx):
    response = requests.post(node_url + "/wallet/transaction/send", json=tx, headers=headers)
    logger.info("Signing tx: %s", json.dumps(tx))

    # Check if the response is successful
    if response.status_code == 200:
        # Remove quotes from the response text and return txId
        txId = response.text.strip('"')
        return {"status": "success", "txId": txId}
    else:
        # Return an error message
        return {"status": "failed", "reason": response.text}


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
