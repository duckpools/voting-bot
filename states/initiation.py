from client_consts import node_address
from consts import quacks_id, treasury_proportion_denomination
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
                                "tokenId": quacks_id,
                                "amount": amount_funded
                            }
                        ],
                        "registers": {
                            "R4": encode_long(int(proportion * treasury_proportion_denomination)),
                            "R5": recipient,
                            "R6": "0ea203466f726d616c2054726561737572792050726f706f73616c2023303030310a0a507572706f73653a20546869732070726f706f73616c20736572766573206173206120746573742e2055706f6e20617070726f76616c2c2061206e6f6d696e616c207472616e73616374696f6e2077696c6c20626520636f6e6475637465642c207265616c6c6f636174696e6720302e303125206f662074686520746f74616c2074726561737572792066756e6473206261636b20746f2074686520747265617375727920697473656c662e0a0a496d706c69636174696f6e733a2054686973207472616e73616374696f6e2069732064657369676e656420736f6c656c7920666f722074657374696e6720707572706f7365732e20436f6e73657175656e746c792c20746865206f7574636f6d6573206f66207468697320766f746520686f6c64206e6f207369676e69666963616e742062656172696e67206f6e207468652074726561737572792e20596f752063616e20766f746520796573206f72206e6f2069742077696c6c206e6f7420696d70616374207468652074726561737572792e"
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