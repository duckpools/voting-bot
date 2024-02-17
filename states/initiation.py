from client_consts import node_address
from consts import test_quacks_id, treasury_proportion_denomination
from helpers.node_calls import sign_and_get_boxids, box_id_to_binary, sign_tx
from helpers.platform_functions import generate_initiation_address, get_counter_registers, generate_paying_address
from helpers.serializer import encode_long


def initiation_action(counter_box, initiate=False, recipient="", proportion=0.1, amount_funded=0, funded_boxId=None, paying_boxId=None):
    if initiate:
        if not funded_boxId:
            fund_initiation_address = generate_initiation_address(node_address)
            fund_initiation_tx = {
                "requests": [
                    {
                        "address": fund_initiation_address,
                        "value": 1000000,
                        "assets": [
                            {
                                "tokenId": test_quacks_id,
                                "amount": amount_funded
                            }
                        ],
                        "registers": {
                            "R4": encode_long(int(proportion * treasury_proportion_denomination)),
                            "R5": recipient,
                            "R6": "0e1d54657374207465737420746573742e2054657374696e6720746573742e"
                        }
                    }
                ],
                "fee": 1000000,
                "inputsRaw": [],
                "dataInputsRaw": []
            }
            resp = sign_and_get_boxids(fund_initiation_tx)
            print(resp)
            funded_boxId = resp["boxIds"][0]
        if not paying_boxId:
            paying_address = generate_paying_address(node_address)
            fund_initiation_tx = {
                "requests": [
                    {
                        "address": paying_address,
                        "value": 2000000,
                        "assets": [
                        ],
                        "registers": {
                        }
                    }
                ],
                "fee": 1000000,
                "inputsRaw": [],
                "dataInputsRaw": []
            }
            resp = sign_and_get_boxids(fund_initiation_tx)
            print(resp)
            paying_boxId = resp["boxIds"][0]
        counter_info = get_counter_registers(counter_box)
        print(counter_info)
        counter_tx = \
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
                            "R5": "59" + encode_long(int(proportion * treasury_proportion_denomination))[2:] + "00",
                            "R6": recipient,
                            "R7": "0500",
                            "R8": encode_long(amount_funded),
                            "R9": "0500"
                        }
                    }
                ],
                "fee": 2000000,
                "inputsRaw":
                    [box_id_to_binary(counter_box["boxId"]), box_id_to_binary(paying_boxId)],
                "dataInputsRaw":
                    [box_id_to_binary(funded_boxId)]
            }
        print(counter_tx)
        print(sign_tx(counter_tx))
    return