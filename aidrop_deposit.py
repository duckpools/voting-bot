import json
import math

from consts import treasury_proportion_denomination, counter_token, airdrop_proxy_deposit, airdrop_address
from helpers.explorer_calls import get_unspent_boxes_by_address
from helpers.node_calls import tree_to_address, box_id_to_binary, sign_tx, sign_and_get_boxids
from helpers.platform_functions import get_ripe_proposal_box, get_treasury_box
from helpers.serializer import encode_long


def process_airdrop_deposit():
    unspent_proxy_boxes = get_unspent_boxes_by_address(airdrop_proxy_deposit)
    num_unspent_proxy_boxes = len(unspent_proxy_boxes)
    if num_unspent_proxy_boxes == 0:
        return
    airdrop_box = get_unspent_boxes_by_address(airdrop_address)[0]
    for box in unspent_proxy_boxes:
        token_amount = int(box["assets"][0]["amount"])
        user_tree = box["additionalRegisters"]["R4"]["renderedValue"]

        airdrop_assets = []

        for asset in airdrop_box["assets"]:
            airdrop_assets.append({
                "tokenId": asset["tokenId"],
                "amount": asset["amount"]
            })
        airdrop_assets[0]["amount"] = int(airdrop_assets[0]["amount"]) - token_amount
        airdrop_assets[1]["amount"] = int(airdrop_assets[1]["amount"]) + token_amount

        currentTotalQuacks = int(airdrop_box["additionalRegisters"]["R4"]["renderedValue"])


        transaction_to_sign = \
            {
                "requests": [
                    {
                        "address": airdrop_address,
                        "value": airdrop_box["value"],
                        "assets": airdrop_assets,
                        "registers": {
                            "R4": encode_long(currentTotalQuacks + token_amount)
                        }
                    },
                    {
                        "address": tree_to_address(user_tree),
                        "value": 1000000,
                        "assets": [
                            {
                                "tokenId": airdrop_box["assets"][0]["tokenId"],
                                "amount": token_amount
                            }
                        ],
                        "registers": {
                            "R4": "0500",
                            "R5": "0400",
                            "R6": "0400",
                            "R7": "0e20" + box["boxId"]
                        }
                    }
                ],
                "fee": 1000000,
                "inputsRaw":
                    [box_id_to_binary(airdrop_box["boxId"]), box_id_to_binary(box["boxId"])],
                "dataInputsRaw":
                    []
            }

        tx_id = sign_and_get_boxids(transaction_to_sign)


        if tx_id["status"] == "success":
            print("Successfully submitted transaction with ID: %s", tx_id)
            airdrop_box = {
                "boxId": tx_id["boxIds"][0],
                "value": airdrop_box["value"],
                "assets": airdrop_assets,
                "additionalRegisters": {
                    "R4": {
                        "renderedValue": currentTotalQuacks + token_amount
                    }
                }
            }
        else:
            transaction_to_sign = \
                {
                    "requests": [
                        {
                            "address": tree_to_address(user_tree),
                            "value": box["value"] - 1000000,
                            "assets": [
                                {
                                    "tokenId": box["assets"][0]["tokenId"],
                                    "amount": box["assets"][0]["amount"]
                                }
                            ],
                            "registers": {
                                "R4": "0e20" + box["boxId"]
                            }
                        }
                    ],
                    "fee": 1000000,
                    "inputsRaw":
                        [box_id_to_binary(box["boxId"])],
                    "dataInputsRaw":
                        []
                }
            tx_id = sign_tx(transaction_to_sign)
            if tx_id != -1:
                print("Successfully submitted refund transaction with ID: %s",  tx_id)
            else:
                print("Failed to process or refund transaction object: %s Failed Refund txID quoted as: %s",
                               json.dumps(transaction_to_sign), tx_id)
