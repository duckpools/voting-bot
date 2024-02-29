import json

from client_consts import node_address
from helpers.explorer_calls import get_unspent_boxes_by_address
from helpers.node_calls import sign_tx, box_id_to_binary
from helpers.platform_functions import generate_initiation_address
from logger import set_logger

logger = set_logger(__name__)


def find_boxes(dummy_address, limit=50):
    logger.info("Finding UTXOs to Collect")

    all_unspent_boxes = []
    offset = 0

    while True:
        # Fetch a chunk of unspent boxes
        unspent_boxes = get_unspent_boxes_by_address(dummy_address, limit=limit, offset=offset)

        # If no unspent boxes are returned, break out of the loop
        if not unspent_boxes:
            break

        # Add the fetched boxes to the list
        all_unspent_boxes.extend(unspent_boxes)

        # Log the current progress
        logger.info(f"Found {len(all_unspent_boxes)} UTXOs so far.")

        # Update the offset for the next API call
        offset += limit

    logger.info(f"Total UTXOs found: {len(all_unspent_boxes)}")

    return all_unspent_boxes

def genereate_binaries(boxes):
    print(boxes)
    logger.info("Getting UTXO Binaries")
    resp = []
    for box in boxes:
        resp.append(box_id_to_binary(box["boxId"]))
    return resp

def collect(binaries):
    # Sends assets to change address
    logger.info("Beginning Collection")
    transaction_to_sign = \
        {
            "requests": [
                {
                    "address": node_address,
                    "value": 1000000 * len(binaries) - 2000000,
                    "assets": [
                    ],
                    "registers": {
                    }
                }
            ],
            "fee": 1000000,
            "inputsRaw":
                binaries,
            "dataInputsRaw":
                []
        }
    logger.debug("Signing Transaction: %s", json.dumps(transaction_to_sign))
    tx_id = sign_tx(transaction_to_sign)
    if tx_id != -1:
        logger.info("Successfully submitted transaction with ID: %s", tx_id)
    else:
        logger.error("Failed to submit transaction")


dummy_script = generate_initiation_address(node_address)
boxes = find_boxes(dummy_script)
binaries = genereate_binaries(boxes)
collect(binaries)