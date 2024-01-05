from time import sleep

from helpers.node_calls import unlock_wallet, current_height
from helpers.platform_functions import get_counter_state
from logger import set_logger
from states.counting import count_action
from states.initiation import initiation_action
from states.new_proposal import new_proposal_action
from states.validation import validation_action

logger = set_logger(__name__)
if __name__ == "__main__":
    logger.info("Beginning Off-Chain Bot")

    SLEEP_TIME = 30
    last_checked_block = -1
    unlock_wallet()

    while not sleep(SLEEP_TIME):
        try:
            current_block = current_height()
            if current_block >= last_checked_block + 5:
                last_checked_block = current_block
                unlock_wallet()
                logger.debug("Block %d found", current_block)
                curr_height = current_block
                state = get_counter_state()
                if state == "New Proposal Period":
                    new_proposal_action()
                elif state == "Vote Validation Period":
                    validation_action()
                elif state == "Counting Period":
                    count_action()
                elif state == "Before Counting":
                    initiation_action()
                else:
                    print("Unknown state")

        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception("Exception")
            curr_height -= 1