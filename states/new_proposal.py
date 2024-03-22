from logger import set_logger
from consts import voteResultDenomination, minimumSupport, votingPeriodicity, proposal_address, \
    default_box_value, minimumVotesPrelim
from helpers.node_calls import sign_tx, box_id_to_binary
from helpers.platform_functions import get_counter_registers, request_funds
from helpers.serializer import encode_long

logger = set_logger(__name__)
def new_proposal_action(counter_box):
    counter_info = get_counter_registers(counter_box)
    resp = request_funds(1000000)
    if resp is not None:
        sign_new_proposal_tx(counter_box, counter_info, resp)


def sign_new_proposal_tx(counter_box, counter_info, resp):
    # resp is the response from request_funds(
    change_box, binaries = resp
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
                        "R9": "0500"
                    }
                },
                change_box
            ],
            "fee": 1000000,
            "inputsRaw":
                [box_id_to_binary(counter_box["boxId"])] + binaries,
            "dataInputsRaw":
                []
        }
    if is_vote_successful(counter_info["total_votes"], counter_info["proportions"][1]):
        resp = request_funds(2000000)
        change_box, binaries = resp
        proposal_box = (
            {
                "address": proposal_address,
                "value": default_box_value,
                "assets": [
                    {
                        "tokenId": counter_tx["requests"][0]["assets"][0]["tokenId"],
                        "amount": 1
                    }
                ],
                "registers": {
                    "R4": encode_long(counter_info["proportions"][0]),
                    "R5": counter_info["R6"],
                    "R6": encode_long(int(counter_tx["requests"][0]["assets"][0]["amount"]) - 1),
                    "R7": encode_long(counter_info["next_vote_deadline"])
                }
            }
        )
        counter_tx["requests"][0]["assets"][0]["amount"] -= 1
        counter_tx["requests"][1] = proposal_box
        counter_tx["requests"].append(change_box)
        counter_tx["inputsRaw"] = [counter_tx["inputsRaw"][0]] + binaries
    logger.info(f"Signing Transaction: {counter_tx}")
    tx_result = sign_tx(counter_tx)
    logger.info(f"Transaction Result: {tx_result}")


def is_vote_successful(currentTotalVotes, currentProportionVote):
    return (currentTotalVotes > minimumVotesPrelim and
            currentProportionVote * voteResultDenomination / currentTotalVotes > minimumSupport)