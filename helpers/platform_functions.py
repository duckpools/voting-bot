import requests

from client_consts import node_address, node_url, headers
from helpers.explorer_calls import get_unspent_boxes_by_address

from consts import counter_address, counter_token, fund_address, proposal_address, treasury_address, treasury_nft
from helpers.generic_calls import logger
from helpers.node_calls import current_height, box_id_to_binary, box_id_to_contents

import json


def get_counter_box():
    """
    Find and return the Ergo pool box in the unspent boxes associated with the specified address.

    Returns:
        dict: The Ergo pool box if found.
        None: If the Ergo pool box is not found.
    """
    potential_boxes = get_unspent_boxes_by_address(counter_address)
    for box in potential_boxes:
        if len(box["assets"]) > 0 and box["assets"][0]["tokenId"] == counter_token:
            return box
    logger.warning("Could not find pool box")
    return None


def determine_counter_state(next_vote_deadline, HEIGHT, no_new_proposal_period=100):
    logger.info("Current Height: %d", HEIGHT)
    logger.info("Current Deadline: %d", next_vote_deadline)
    pass_proposal_deadline = next_vote_deadline + 20
    new_proposal_deadline = pass_proposal_deadline + 20

    is_before_counting = HEIGHT < next_vote_deadline - no_new_proposal_period
    is_counting_period = next_vote_deadline < HEIGHT < pass_proposal_deadline
    is_vote_validation_period = pass_proposal_deadline < HEIGHT < new_proposal_deadline
    is_new_proposal_period = HEIGHT > new_proposal_deadline

    if is_before_counting:
        return "Before Counting"
    elif is_counting_period:
        return "Counting Period"
    elif is_vote_validation_period:
        return "Vote Validation Period"
    elif is_new_proposal_period:
        return "New Proposal Period"
    else:
        return "Unknown State"


def get_counter_state():
    counter_box = get_counter_box()
    if counter_box:
        current_deadline = int(counter_box["additionalRegisters"]["R4"]["renderedValue"])
        return determine_counter_state(current_deadline, current_height()), counter_box


def get_counter_registers(counter_box, request_explorer=False):
    if request_explorer:
        counter_box = get_counter_box()
    return {
        "R4": counter_box["additionalRegisters"]["R4"]["serializedValue"],
        "next_vote_deadline": int(counter_box["additionalRegisters"]["R4"]["renderedValue"]),

        "R5": (counter_box["additionalRegisters"]["R5"]["serializedValue"]),
        "proportions": json.loads(counter_box["additionalRegisters"]["R5"]["renderedValue"]),

        "R6": counter_box["additionalRegisters"]["R6"]["serializedValue"],
        "recipient_tree": counter_box["additionalRegisters"]["R6"]["renderedValue"],

        "R7": counter_box["additionalRegisters"]["R7"]["serializedValue"],
        "total_votes": int(counter_box["additionalRegisters"]["R7"]["renderedValue"]),

        "R8": counter_box["additionalRegisters"]["R8"]["serializedValue"],
        "initiation_amount": int(counter_box["additionalRegisters"]["R8"]["renderedValue"]),

        "R9": counter_box["additionalRegisters"]["R9"]["serializedValue"],
        "validation_votes": int(counter_box["additionalRegisters"]["R9"]["renderedValue"]),
    }


def get_boxes_above_r8_threshold(address, threshold):
    """
    Fetches all unspent boxes for a given address where the Long value in R4 is above a specified threshold.

    :param address: The address to fetch boxes for.
    :param threshold: The threshold for the Long value in R4.
    :return: A list of boxes meeting the criteria.
    """
    url = f"https://api.ergoplatform.com/api/v1/boxes/unspent/byAddress/{address}"
    try:
        response = requests.get(url)
        response.raise_for_status()

        boxes = response.json().get('items', [])
        filtered_boxes = []

        for box in boxes:
            R8_value = box.get('additionalRegisters', {}).get('R8', {}).get('renderedValue')

            if R8_value:
                # Convert the rendered value to a long integer
                long_value = int(R8_value)

                if long_value > threshold:
                    filtered_boxes.append(box)

        return filtered_boxes

    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return []


def node_get_counter_box(box=None):
    if not box:
        box = get_counter_box()
    raw_box = box_id_to_binary(box["boxId"])
    box_contents = box_id_to_contents(box["boxId"])
    return box_contents, raw_box


def get_voter_votes(vote_boxes, counter_box):
    currentProportionVote = "05" + counter_box["additionalRegisters"]["R5"][2:-2]
    currentRecipientVote = counter_box["additionalRegisters"]["R6"]
    votesInFavour = 0
    totalVotes = 0
    validationVotesInFavour = 0

    for box in vote_boxes:
        # Update totalVotes
        totalVotes += box['assets'][1]["amount"]

        # Check for votesInFavour
        if 'R4' in box['additionalRegisters'] and box['additionalRegisters']['R4'][
            'serializedValue'] == currentProportionVote and \
                'R5' in box['additionalRegisters'] and box['additionalRegisters']['R5'][
            'serializedValue'] == currentRecipientVote:
            votesInFavour += box['assets'][1]["amount"]

        # Check for validationVotesInFavour
        if 'R9' in box['additionalRegisters'] and int(box['additionalRegisters']['R9']['renderedValue']) == 1:
            validationVotesInFavour += box['assets'][1]["amount"]

    return votesInFavour, totalVotes, validationVotesInFavour


def generate_fund_address(address):
    script_payload = {
        "source": f"PK(\"{address}\") && HEIGHT >= -101"
    }
    try:
        # Making the POST request
        response = requests.post(f"{node_url}/script/p2sAddress", json=script_payload, headers=headers)

        # Checking if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            parsed_response = json.loads(response.text)
            return parsed_response["address"]

        else:
            logger.error(f"Error: Received status code {response.status_code}")
            logger.error(f"Message: {response.text}")
            return None

    except requests.RequestException as e:
        logger.error(f"An error occurred while making the request: {e}")
        return None


def generate_paying_address(address):
    script_payload = {
        "source": f"PK(\"{address}\") && HEIGHT >= -301"
    }
    try:
        # Making the POST request
        response = requests.post(f"{node_url}/script/p2sAddress", json=script_payload, headers=headers)

        # Checking if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            parsed_response = json.loads(response.text)
            return parsed_response["address"]

        else:
            logger.error(f"Error: Received status code {response.status_code}")
            logger.error(f"Message: {response.text}")
            return None

    except requests.RequestException as e:
        logger.error(f"An error occurred while making the request: {e}")
        return None


def generate_initiation_address(address):
    script_payload = {
        "source": f"PK(\"{address}\") && HEIGHT >= -201"
    }
    try:
        # Making the POST request
        response = requests.post(f"{node_url}/script/p2sAddress", json=script_payload, headers=headers)

        # Checking if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            parsed_response = json.loads(response.text)
            return parsed_response["address"]

        else:
            logger.error(f"Error: Received status code {response.status_code}")
            logger.error(f"Message: {response.text}")
            return None

    except requests.RequestException as e:
        logger.error(f"An error occurred while making the request: {e}")
        return None


def request_funds(amount):
    if (generate_fund_address(node_address) == fund_address):
        boxes_under_address = get_unspent_boxes_by_address(fund_address)
        binaries = []
        total_value = 0
        for box in boxes_under_address:
            total_value += box["value"]
            binaries.append(box_id_to_binary(box["boxId"]))

        change_box = {
            "address": fund_address,
            "value": total_value - amount,
            "assets": [
            ],
            "registers": {}
        }
        return change_box, binaries
    return


def get_proposal_box(counter_box):
    potential_boxes = get_unspent_boxes_by_address(proposal_address)
    logger.info(f"Potential proposal Boxes: {potential_boxes}")
    for box in potential_boxes:
        if len(box["assets"]) > 0 and box["assets"][0]["tokenId"] == counter_token and \
                "R6" in box["additionalRegisters"] and \
                int(box["additionalRegisters"]["R6"]["renderedValue"]) == int(counter_box["assets"][0]["amount"]):
            return box
    logger.warning("Could not find pool box")
    return None


def get_ripe_proposal_box():
    potential_boxes = get_unspent_boxes_by_address(proposal_address)
    logger.info(f"Potential proposal Boxes: {potential_boxes}")
    for box in potential_boxes:
        if len(box["assets"]) > 0 and box["assets"][0]["tokenId"] == counter_token and \
                box["assets"][0]["amount"] == 2:
            return box
    logger.warning("Could not find pool box")
    return None


def get_treasury_box():
    potential_boxes = get_unspent_boxes_by_address(treasury_address)
    logger.info(f"Potential treasury Boxes: {potential_boxes}")
    for box in potential_boxes:
        if len(box["assets"]) > 0 and box["assets"][0]["tokenId"] == treasury_nft:
            return box
    logger.warning("Could not find pool box")
    return None