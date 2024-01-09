import requests

from helpers.explorer_calls import get_unspent_boxes_by_address

from consts import counter_address, counter_token
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


def determine_counter_state(next_vote_deadline, HEIGHT, no_new_proposal_period=10):
    pass_proposal_deadline = next_vote_deadline + 50
    new_proposal_deadline = pass_proposal_deadline + 50

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


def get_counter_registers(counter_box):
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


def get_boxes_above_r4_threshold(address, threshold):
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
            R4_value = box.get('additionalRegisters', {}).get('R4', {}).get('renderedValue')

            if R4_value:
                # Convert the rendered value to a long integer
                long_value = int(R4_value)

                if long_value > threshold:
                    filtered_boxes.append(box)

        return filtered_boxes

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def node_get_counter_box(box):
    raw_box = box_id_to_binary(box["boxId"])
    box_contents = box_id_to_contents(box["boxId"])
    return box_contents, raw_box

def get_voter_votes(vote_boxes, counter_box):
    currentProportionVote = "05"+counter_box["additionalRegisters"]["R5"][2:-2]
    currentRecipientVote = counter_box["additionalRegisters"]["R6"]
    votesInFavour = 0
    totalVotes = 0
    validationVotesInFavour = 0

    for box in vote_boxes:
        # Update totalVotes
        totalVotes += box['assets'][1]["amount"]

        # Check for votesInFavour
        if 'R4' in box['additionalRegisters'] and box['additionalRegisters']['R4']['serializedValue'] == currentProportionVote and \
           'R5' in box['additionalRegisters'] and box['additionalRegisters']['R5']['serializedValue'] == currentRecipientVote:
            votesInFavour += box['assets'][1]["amount"]

        # Check for validationVotesInFavour
        if 'R9' in box['additionalRegisters'] and int(box['additionalRegisters']['R9']['renderedValue']) == 1:
            validationVotesInFavour += box['assets'][1]["amount"]

    return votesInFavour, totalVotes, validationVotesInFavour

