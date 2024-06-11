from client_consts import node_address
from consts import quacks_id, treasury_proportion_denomination
from helpers.node_calls import sign_and_get_boxids, box_id_to_binary, sign_tx
from helpers.platform_functions import generate_initiation_address, get_counter_registers, generate_paying_address
from helpers.serializer import encode_long, encode_long_tuple


def initiation_action(token, counter_box, address, initiate=False, recipient="", proportion=0.1, amount_funded=0, funded_boxId=None, paying_boxId=None):
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
                            "R6": "0e9d02466f726d616c2054726561737572792050726f706f73616c2023303030320a0a50726f706f73616c3a20546f2073656e6420392e3525206f662074686520747265617375727920746f206475636b44726f702c2074686520515541434b532061697264726f7020616464726573732e2049662070617373656420392e3525206f662074726561737572792066756e64732077696c6c2062652073656e7420746f20746865206475636b44726f702061697264726f7020616464726573732c207769746820616e2061697264726f7020626c6f636b20686569676874206f6620313237323535312e205468652061697264726f702077696c6c20626520636f6e647563746564206f6e2061697264726f702e6475636b706f6f6c732e696f"
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
        counter_info = get_counter_registers(token, counter_box, address)
        isParams = True
        r5 = "59" + encode_long(int(proportion * treasury_proportion_denomination))[2:] + "00"
        if isParams:
            r5 = encode_long_tuple([0, int(proportion * treasury_proportion_denomination)])
        print(r5)
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
                            "R5": r5,
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