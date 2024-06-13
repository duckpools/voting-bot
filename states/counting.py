import json

from consts import user_vote_address, counter_address, vote_token, user_vote_address_params, vote_token_params
from helpers.explorer_calls import get_box_by_id
from helpers.node_calls import box_id_to_binary, sign_tx, tree_to_address
from helpers.platform_functions import get_boxes_above_r8_threshold, node_get_counter_box, get_voter_votes, \
    get_counter_registers
from helpers.serializer import encode_long, encode_long_tuple


def count_action(token, counter_box, address, raw_counter_box=None, height_thresold=0):
    isParams = True
    if isParams:
        user_vote_address = user_vote_address_params
        vote_token = vote_token_params
    vote_boxes = (get_boxes_above_r8_threshold(user_vote_address, height_thresold))
    print(len(vote_boxes))
    counter_box, raw_counter_box = node_get_counter_box(token, address, counter_box )

    votesInFavour, totalVotes, validationVotesInFavour = get_voter_votes(vote_boxes, counter_box, isParams)
    print("start")
    print(votesInFavour)
    print(totalVotes)
    print(validationVotesInFavour)

    counter_tx = \
        {
            "requests": [
                {
                    "address": address,
                    "value": counter_box["value"],
                    "assets": [
                        {
                            "tokenId": counter_box["assets"][0]["tokenId"],
                            "amount": counter_box["assets"][0]["amount"],
                        }

                    ],
                    "registers":
                        counter_box["additionalRegisters"]
                }
            ],
            "fee": 1000000,
            "inputsRaw":
                [],
            "dataInputsRaw":
                []
        }
    binaries = [raw_counter_box]
    for box in vote_boxes:
        binaries.append(box_id_to_binary(box["boxId"]))
        counter_tx["requests"].append(
            {
                "address": tree_to_address(box["additionalRegisters"]["R7"]["renderedValue"]),
                "value": box["value"] - 1000000,
                "assets": [
                    {
                        "tokenId": box["assets"][1]["tokenId"],
                        "amount": box["assets"][1]["amount"]
                    }
                ],
                "registers":
                    {
                    "R4": "0e20" + box["boxId"]
                    }
            }
        )
    counter_tx["inputsRaw"] = binaries
    counter_tx["requests"].append(
        {
            "assetsToBurn": [
                {
                    "tokenId": vote_token,
                    "amount": len(vote_boxes)
                }
            ]
        }
    )
    print(validationVotesInFavour)
    counter_info = get_counter_registers(token, counter_box, address, request_explorer=True)
    # WARNING THIS WILL NOT WORK FOR MULTIPLE RUNS OF COUNTS
    isParams = True
    r5 = counter_info["R5"][:-2] + encode_long(votesInFavour)[2:]
    if isParams:
        explorer_counter_box = get_box_by_id(counter_box["boxId"])
        r5_array = [votesInFavour] + json.loads(explorer_counter_box["additionalRegisters"]["R5"]["renderedValue"])[1:]
        r5 = encode_long_tuple(r5_array)
    counter_tx["requests"][0]["registers"]["R5"] = r5
    counter_tx["requests"][0]["registers"]["R7"] = encode_long(totalVotes)
    counter_tx["requests"][0]["registers"]["R9"] = encode_long(validationVotesInFavour)
    counter_tx["fee"] += (len(vote_boxes) - 1) * 1000000
    print(counter_tx)
    print(sign_tx(counter_tx))
