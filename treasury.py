import math

from collection import logger
from consts import treasury_proportion_denomination, counter_token
from helpers.node_calls import tree_to_address, box_id_to_binary, sign_tx
from helpers.platform_functions import get_ripe_proposal_box, get_treasury_box


def process_treasury():
    proposal_box = get_ripe_proposal_box()
    logger.info(f"Found proposal box: {proposal_box}")
    if not proposal_box:
        return
    treasury_box = get_treasury_box()
    proposal_recipient = proposal_box["additionalRegisters"]["R5"]["renderedValue"]
    proposal_proportion = int(proposal_box["additionalRegisters"]["R4"]["renderedValue"]) / treasury_proportion_denomination
    logger.info(f"Attempting to send {proposal_proportion} % of treasury to {proposal_recipient}")
    treasury_final_assets = [{
        "tokenId": treasury_box["assets"][0]["tokenId"],
        "amount": treasury_box["assets"][0]["amount"]
    }]
    recipient_assets = []
    for asset in treasury_box["assets"][1:]:
        value_awarded = math.floor(int(asset["amount"]) * proposal_proportion)
        treasury_final_assets.append({
            "tokenId": asset["tokenId"],
            "amount": asset["amount"] - value_awarded
        })
        if value_awarded > 0:
            recipient_assets.append({
                "tokenId": asset["tokenId"],
                "amount": value_awarded
            })
    value_awarded = math.floor(int(treasury_box["value"]) * proposal_proportion)

    treasury_tx = \
        {
            "requests": [
                {
                    "address": treasury_box["address"],
                    "value": int(treasury_box["value"]) - value_awarded,
                    "assets": treasury_final_assets,
                    "registers": {

                    }
                },
                {
                    "address": tree_to_address(proposal_recipient),
                    "value": value_awarded,
                    "assets": recipient_assets,
                    "registers": {
                        "R4": "0502",
                        "R5": "0e010a"
                    }
                },
    {
      "assetsToBurn": [
        {
          "tokenId": counter_token,
          "amount": 2
        }
      ]
    }
            ],
            "fee": 1000000,
            "inputsRaw":
                [box_id_to_binary(proposal_box["boxId"]), box_id_to_binary(treasury_box["boxId"])],
            "dataInputsRaw":
                []
        }
    logger.info(f"Signing Transaction: {treasury_tx}")
    tx_result = sign_tx(treasury_tx)
    logger.info(f"Transaction Result: {tx_result}")
