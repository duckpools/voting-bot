from client_consts import node_address
from consts import test_quacks_id, treasury_proportion_denomination
from helpers.node_calls import sign_and_get_boxids
from helpers.platform_functions import generate_initiation_address
from helpers.serializer import encode_long


def initiation_action(counter_box, initiate=False, recipient="", proportion=0.1, amount_funded=0, funded_boxId=None):
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
                            "R5": recipient
                        }
                    }
                ],
                "fee": 1000000,
                "inputsRaw": [],
                "dataInputsRaw": []
            }
        resp = sign_and_get_boxids(fund_initiation_tx)
        resp["boxIds"][0]
        print(resp)
    return