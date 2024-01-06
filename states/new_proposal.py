from consts import minimum_votes, voteResultDenomination, minimumSupport, votingPeriodicity
from helpers.node_calls import sign_tx, box_id_to_binary
from helpers.platform_functions import get_counter_registers
from helpers.serializer import encode_long


def new_proposal_action(counter_box):
    print("current counter")
    print(counter_box)
    counter_info = get_counter_registers(counter_box)
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
                        "R4": encode_long(counter_info["next_vote_deadline"] + votingPeriodicity),
                        "R5": "590000",
                        "R6": counter_info["R6"],
                        "R7": "0500",
                        "R8": "0500",
                        "R9": counter_info["R9"]
                    }
                }
            ],
            "fee": 1000000,
            "inputsRaw":
                [box_id_to_binary(counter_box["boxId"]), "80ade2040008cd03dda8fe44b65ff96eb9dd442e6f10aca93f7351e96f2cbb1862c21a9055bc8b9689c64700001256156a166e98aeca70229d9081d003021492b1296a80f93641eba8a6d5230700"],
            "dataInputsRaw":
                []
        }
    if is_vote_successful(counter_info["total_votes"], counter_info["proportions"][1]):
        pass
        print("passed")
    else:
        print(counter_tx)
        print(sign_tx(counter_tx))

def is_vote_successful(currentTotalVotes, currentProportionVote):
    print(currentTotalVotes)
    print(currentProportionVote)
    return (currentTotalVotes > minimum_votes and
            currentProportionVote * voteResultDenomination / currentTotalVotes > minimumSupport)