import requests
import json

from client_consts import node_url, node_pass, headers
from helpers.generic_calls import logger, get_request

def unlock_wallet():
    response = requests.post(f"{node_url}/wallet/unlock", json={"pass": node_pass}, headers=headers)
    logger.debug(f"Unlock wallet response status code: {response.status_code}")
    return response.status_code

def current_height():
    return json.loads(get_request(node_url + "/blocks/lastHeaders/1").text)[0]['height']
