import json

from client_consts import explorer_url
from helpers.generic_calls import get_request


def get_unspent_boxes_by_address(addr, limit=50, offset=0):
    return json.loads(get_request(f"{explorer_url}/boxes/unspent/byAddress/{addr}?limit={limit}&offset={offset}").text)['items']
