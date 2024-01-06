from consts import minimum_votes, voteResultDenomination, minimumSupport
from helpers.platform_functions import get_counter_registers


def new_proposal_action(counter_box):
    print("current counter")
    counter_info = get_counter_registers(counter_box)

    is_vote_successful(counter_info["total_votes"])
    counter_tx = \
        {
            "requests": [
                {
                    "address": counter_address,
                    "value": counter_box["value"],
                    "assets": [
                        counter_box["assets"][0]
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
    counter_tx["requests"][0]["registers"]["R5"] = "59809bee02" + encodeLong(votesInFavour)[2:]
    counter_tx["requests"][0]["registers"]["R7"] = encodeLong(totalVotes)
    counter_tx["requests"][0]["registers"]["R9"] = encodeLong(validationVotesInFavour) + "00"
    counter_tx["fee"] += (len(vote_boxes) - 1) * 1000000
    print(counter_tx)
    print(sign_tx(counter_tx))
    return

def is_vote_successful(currentTotalVotes, currentProportionVote):
    return (currentTotalVotes > minimum_votes and
            currentProportionVote[1] * voteResultDenomination / currentTotalVotes > minimumSupport)