from helpers.node_calls import box_id_to_binary, sign_tx
from helpers.platform_functions import get_proposal_box, get_counter_registers, request_funds


def validation_action(counter_box):
    proposal_box = get_proposal_box()
    counter_info = get_counter_registers(counter_box)
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
                        "R5": "590000",
                        "R6": counter_info["R6"],
                        "R7": "0500",
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
    print(validation_tx)
    print(sign_tx(validation_tx))
    return