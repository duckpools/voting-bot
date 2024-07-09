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
NEW_BLOCK_THRESHOLD = 3


def handle_state(state, counter_token, counter_box, counter_address, isInitiate, isParams):
    actions = {
        "New Proposal Period": new_proposal_action,
        "Vote Validation Period": validation_action,
        "Counting Period": count_action,
        "Before Counting": lambda token, box, address, isParams: initiation_action(
            token,
            box,
            address,
            isParams,
            byteData=["7a51950e5f548549ec1aa63ffdc38279505b11e7e803d01bcf8347e0123c88b0",
                      "47a811c68e49f6bfa6629602037ee65f8d175ddbc7b64bdb65ad40599b812fd0",
                      "31a931328954c535821fc3ae07d6f33266adb9a6db3c7b576b9f4da2b4018234",
                      "0ec2e22aa9a854d418578c7c7b7ce0fe6afc44760007c6ee321f41d93c23d1d8",
                      "0ec2e22aa9a854d418578c7c7b7ce0fe6afc44760007c6ee321f41d93c23d1d8",
                      "0ec2e22aa9a854d418578c7c7b7ce0fe6afc44760007c6ee321f41d93c23d1d8"],
            initiate=isInitiate,
            recipient="0e2e100208cd03f0dbaa5d7b67fac2130f5cb7166bcf4b19bee4ba88567830935d242b972fef300101ea027300d17301",
            params=[0, 300, 1700, 300, 1500, 300, 1500],
            proportion=0.0001,
            amount_funded=120000000,
        )
    }
    action = actions.get(state)
    if action:
        action(counter_token, counter_box, counter_address, isParams)
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
                p_state, p_counter_box = get_counter_state(counter_token_params, counter_address_params, 1, 13, 8)
                logger.info("Treasury State is: %s", state)
                logger.info("Params State is: %s", p_state)
                logger.info("Begin work on Treasury...")
                handle_state(state, counter_token, counter_box, counter_address, False, False)
                logger.info("Begin work on params...")
                handle_state(p_state, counter_token_params, p_counter_box, counter_address_params, False, True)
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