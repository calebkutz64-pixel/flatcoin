from typing import Optional, List

import time

from flatcoin.block import Block
from flatcoin.consensus import validate_block
from flatcoin.params import VALIDATOR_STAKE, VALIDATOR_SLASH_STAGES
from flatcoin.reading import human
from flatcoin.utils import open_or_init_wallet
from flatcoin.wallet import Wallet


class InvalidBlockError(Exception):
    pass


class Validator:

    def __init__(
        self,
        wallet: Wallet,
        current_strike_stage: Optional[int],
        work: int, # this is the number of blocks they have validated
        strikes: int,
        stake: int,
    ):
        self.wallet = wallet
        self.current_strike_stage = current_strike_stage
        self.public_key: bytes = next(iter(wallet.keypair))
        self.work = work
        self.strikes = strikes
        self.stake = stake

        if not self.stake >= VALIDATOR_STAKE:
            raise ValueError("Stake value < 32 FLA")

    @classmethod
    def with_stake(cls, stake_value: int) -> "Validator":
        wallet = open_or_init_wallet()
        current_strike_stage = None
        work = 0
        strikes = 0

        if stake_value < VALIDATOR_STAKE:
            print(f"Failed to create validator with stake value {stake_value}")

        stake = stake_value

        return cls(
            wallet=wallet,
            current_strike_stage=current_strike_stage,
            work=work,
            strikes=strikes,
            stake=stake
        )

    def slash_stake(self, slash_stage: int) -> None:
        if not self.stake:
            return

        match slash_stage:
            case 0x01:
                self.stake = VALIDATOR_SLASH_STAGES[0x01] # 32 / 2 = 16
                self.current_strike_stage = 0x01
            case 0x02:
                self.stake = VALIDATOR_SLASH_STAGES[0x02] # 16 / 2 = 8
                self.current_strike_stage = 0x02
            case 0x03:
                self.stake = VALIDATOR_SLASH_STAGES[0x03] # 8 - 8, this is the last stage...so 0
                self.current_strike_stage = 0x01
            case _:
                raise ValueError("Invalid slash stage")

    def validate_single(self, block: Block, current_timestamp: int) -> bool:
        valid_block = validate_block(block, current_timestamp)
        if not valid_block:
            raise InvalidBlockError(f"Validator {human(self.public_key)[:20]} tried to validate invalid block")
        return True

    def validate_multiple(self, blocks: List[Block]) -> None:
        start_time = int(time.time())

        print(f"Validator {human(self.public_key)[:20]} validating multiple blocks")
        print("Start:", start_time)

        for block in blocks:
            valid_block = validate_block(block, int(time.time()))
            if not valid_block:
                break
            print(f"Validator {human(self.public_key)[:20]} validated block")

        end_time = int(time.time())
        print(f"End:", end_time)

    def _sanity_check(self) -> bool:
        pass



