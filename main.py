from time import sleep

from aidrop_deposit import process_airdrop_deposit
from consts import counter_token, counter_token_params, counter_address, counter_address_params, process_treasury_bool, \
    process_airdrops_bool
from helpers.node_calls import unlock_wallet, current_height
from helpers.platform_functions import get_counter_state
from logger import set_logger
from states.counting import count_action
from states.initiation import initiation_action
from states.new_proposal import new_proposal_action
from states.validation import validation_action
from treasury import process_treasury

# Main Loop Settings
SLEEP_TIME = 2
INITIAL_LAST_CHECKED_BLOCK = -1
NEW_BLOCK_THRESHOLD = 5


def handle_state(state, counter_token, counter_box, counter_address, isInitiate):
    actions = {
        "New Proposal Period": new_proposal_action,
        "Vote Validation Period": validation_action,
        "Counting Period": count_action,
        "Before Counting": lambda token, box, address: initiation_action(
            token,
            box,
            address,
            initiate=isInitiate,
            recipient="0e2e100208cd03f0dbaa5d7b67fac2130f5cb7166bcf4b19bee4ba88567830935d242b972fef300101ea027300d17301",
            proportion=0.0001,
            amount_funded=200000000
        )
    }
    action = actions.get(state)
    if action:
        action(counter_token, counter_box, counter_address)
    else:
        logger.warning("Unknown State: %s", state)

logger = set_logger(__name__)
if __name__ == "__main__":
    logger.info("Beginning Off-Chain Bot")
    last_checked_block = INITIAL_LAST_CHECKED_BLOCK
    unlock_wallet()
    while not sleep(SLEEP_TIME):
        try:
            current_block = current_height()
            if current_block >= last_checked_block + NEW_BLOCK_THRESHOLD:
                last_checked_block = current_block
                unlock_wallet()
                logger.debug("Block %d found", current_block)
                curr_height = current_block
                state, counter_box = get_counter_state(counter_token, counter_address)
                p_state, p_counter_box = get_counter_state(counter_token_params, counter_address_params, 10, 30, 30)
                logger.info("Treasury State is: %s", state)
                logger.info("Params State is: %s", p_state)
                logger.info("Begin work on Treasury...")
                handle_state(state, counter_token, counter_box, counter_address, False)
                logger.info("Begin work on params...")
                handle_state(p_state, counter_token_params, p_counter_box, counter_address_params, True)
                if (process_treasury_bool):
                    logger.info("Beginning secondary operations (Treasury)...")
                    process_treasury()
                elif (process_airdrops_bool):
                    logger.info("Beginning secondary operations (Aidrop)...")
                    process_airdrop_deposit()

        except KeyboardInterrupt:
            logger.info("Program terminated by user")
        except Exception as e:
            logger.exception("Unexpected error occurred: %s", str(e))
            curr_height -= 1