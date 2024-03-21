from time import sleep

from aidrop_deposit import process_airdrop_deposit
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
NEW_BLOCK_THRESHOLD = 2

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
                state, counter_box = get_counter_state()
                logger.info("Current State is: %s", state)
                if state == "New Proposal Period":
                    new_proposal_action(counter_box)
                elif state == "Vote Validation Period":
                    validation_action(counter_box)
                elif state == "Counting Period":
                    count_action(counter_box)
                elif state == "Before Counting":
                    initiation_action(
                        counter_box,
                        initiate=False,
                        recipient="0e240008cd03dda8fe44b65ff96eb9dd442e6f10aca93f7351e96f2cbb1862c21a9055bc8b96",
                        proportion=0.06,
                        amount_funded=200000000
                    )
                else:
                    logger.warning("Unknown State")
                logger.info("Beginning secondary operations")
                process_airdrop_deposit()
                process_treasury()


        except KeyboardInterrupt:
            logger.info("Program terminated by user")
        except Exception as e:
            logger.exception("Unexpected error occurred: %s", str(e))
            curr_height -= 1