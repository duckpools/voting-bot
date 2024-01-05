from helpers.explorer_calls import get_unspent_boxes_by_address

from consts import counter_address, counter_token
from helpers.generic_calls import logger
from helpers.node_calls import current_height


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
        print(determine_counter_state(current_deadline, current_height()))

