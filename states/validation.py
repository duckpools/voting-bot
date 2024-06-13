from consts import proposal_address_params, proposal_address, counter_address_params
from logger import set_logger
from helpers.node_calls import box_id_to_binary, sign_tx
from helpers.platform_functions import get_proposal_box, get_counter_registers, request_funds

logger = set_logger(__name__)
def validation_action(token, counter_box, address):
    isParams = counter_address_params == address
    if isParams:
        proposal_box = get_proposal_box(counter_box, token, proposal_address_params)
    else:
        proposal_box = get_proposal_box(counter_box, token, proposal_address)
    logger.info(f"Found proposal box: {proposal_box}")
    if not proposal_box:
        return
    counter_info = get_counter_registers(token, counter_box, address)
    resp = request_funds(1000000)
    change_box, binaries = resp
    validation_tx = \
        {
            "requests": [
                {
                    "address": counter_box["address"],
                    "value": counter_box["value"],
                    "assets": [
                        {"tokenId": asset["tokenId"], "amount": asset["amount"]} for asset in counter_box["assets"]
                    ],
                    "registers": {
                        "R4": counter_info["R4"],
                        "R5": counter_info["R5"],
                        "R6": counter_info["R6"],
                        "R7": counter_info["R7"],
                        "R8": "0500",
                        "R9": "0500"
                    }
                },
                {
                    "address": proposal_box["address"],
                    "value": proposal_box["value"],
                    "assets": [
                        {"tokenId": proposal_box["assets"][0]["tokenId"], "amount": 2}
                    ],
                    "registers": {
                        "R4": proposal_box["additionalRegisters"]["R4"]["serializedValue"],
                        "R5": proposal_box["additionalRegisters"]["R5"]["serializedValue"],
                    }
                },
                change_box
            ],
            "fee": 1000000,
            "inputsRaw":
                [box_id_to_binary(counter_box["boxId"]), box_id_to_binary(proposal_box["boxId"])] + binaries,
            "dataInputsRaw":
                []
        }
    validation_tx["requests"][0]["assets"][0]["amount"] -= 1
    logger.info(f"Signing Transaction: {validation_tx}")
    tx_result = sign_tx(validation_tx)
    logger.info(f"Transaction Result: {tx_result}")