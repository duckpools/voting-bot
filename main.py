from time import sleep

from helpers.node_calls import unlock_wallet, current_height
from helpers.platform_functions import get_counter_state
from logger import set_logger
from states.counting import count_action
from states.initiation import initiation_action
from states.new_proposal import new_proposal_action
from states.validation import validation_action
from treasury import process_treasury

logger = set_logger(__name__)
if __name__ == "__main__":
    logger.info("Beginning Off-Chain Bot")

    SLEEP_TIME = 2
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
                state, counter_box = get_counter_state()
                print(state)
                if state == "New Proposal Period":
                    new_proposal_action(counter_box)
                elif state == "Vote Validation Period":
                    validation_action(counter_box)
                elif state == "Counting Period":
                    count_action(counter_box)
                elif state == "Before Counting":
                    initiation_action(
                        counter_box,
                        initiate=True,
                        recipient="0e240008cd03dda8fe44b65ff96eb9dd442e6f10aca93f7351e96f2cbb1862c21a9055bc8b96",
                        proportion=0.2,
                        amount_funded=120000000
                    )
                else:
                    print("Unknown state")
                print("Beginning Treasury Payout")
                process_treasury()


        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception("Exception")
            curr_height -= 1