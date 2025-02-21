import logging

import chess
import requests

from typing import Optional

from chess.pgn import GameNode
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from model import NextMovePair

TB_API = "http://tablebase.lichess.ovh/standard?fen={}"

RETRY_STRAT = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    # in future versions `method_whitelist` is removed and replaced by `allowed_methods`
    method_whitelist=["GET"]
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRAT)

class TbChecker:

    def __init__(self, log: logging.Logger) -> None:
        self.session = requests.Session()
        self.session.mount("http://", ADAPTER)
        self.session.mount("https://", ADAPTER)
        self.log = log

    # `*` is used to force kwarg only for `looking_for_mate`
    def is_valid(self, pair: NextMovePair, *,looking_for_mate: bool) -> Optional[bool]:
        """
        Returns `None` if the check is not applicable:
            - The position has more than 7 pieces.
            - The puzzle is a mate puzzle. DTZ does not garantee the fastest mate. Also a mate in N puzzle
                  can be correct even if there also exists a N+1 mate.
            - There is an error processing the API result, or if the API is unreachable.
        """
        if looking_for_mate:
            return None
        board = pair.node.board()
        if len(chess.SquareSet(board.occupied)) > 7:
            return None

        fen = board.fen()
        expected_move = pair.best.move.uci()
        try:
            rep = self.session.get(TB_API.format(fen)).json()
        except requests.exceptions.RequestException as e:
            self.log.warning(f"req error while checking move pair for {fen}: {e}")
            return None
        is_valid = True
        if rep["category"] != "win":
            is_valid = False
        for move in rep["moves"]:
            # move["category"] is from the opponent's point of vue
            if move["uci"] == expected_move and move["category"] != "loss":
                self.log.debug(f"in position {fen}, {move['uci']}({move['san']}) is not winning, opponent's category: {move['category']}")
                is_valid = False
            elif move["category"] == "loss" and move["uci"] != expected_move: # a winning move which is not `expected_move`, puzzle is wrong 
                self.log.debug(f"in position {fen}, {move['uci']}({move['san']}) is not winning, opponent's category: {move['category']}")
                is_valid = False
        return is_valid