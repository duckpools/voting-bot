from consts import user_vote_address, counter_address
from helpers.node_calls import box_id_to_binary, sign_tx, tree_to_address
from helpers.platform_functions import get_boxes_above_r8_threshold, node_get_counter_box, get_voter_votes, \
    get_counter_registers
from helpers.serializer import encode_long


def count_action(counter_box, raw_counter_box=None, height_thresold=0):
    vote_boxes = (get_boxes_above_r8_threshold(user_vote_address, height_thresold))
    print(vote_boxes)
    counter_box, raw_counter_box = node_get_counter_box(counter_box)

    votesInFavour, totalVotes, validationVotesInFavour = get_voter_votes(vote_boxes, counter_box)
    print(votesInFavour)
    print(totalVotes)

    counter_tx = \
        {
            "requests": [
                {
                    "address": counter_address,
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
                    "tokenId": "0b9af8712fe8c01aef5a2634a436ffcae8f99b30139975812e07719ea8993c10",
                    "amount": len(vote_boxes)
                }
            ]
        }
    )
    counter_info = get_counter_registers(counter_box, request_explorer=True)
    counter_tx["requests"][0]["registers"]["R5"] = counter_info["R5"][:-2] + encode_long(votesInFavour)[2:]
    counter_tx["requests"][0]["registers"]["R7"] = encode_long(totalVotes)
    counter_tx["requests"][0]["registers"]["R9"] = encode_long(validationVotesInFavour) + "00"
    counter_tx["fee"] += (len(vote_boxes) - 1) * 1000000
    print(counter_tx)
    print(sign_tx(counter_tx))
