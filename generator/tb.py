import logging

import chess
import requests

from typing import Optional, Literal, Dict, Any

from chess import Color
from chess.pgn import GameNode
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from model import NextMovePair, TbPair, EngineMove

TB_API = "http://tablebase.lichess.ovh/standard?fen={}"


WDL = Literal["win", "draw", "loss", "unknown", "maybe-win", "blessed-loss", "maybe-loss", "cursed-win"]

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


    # `*` is used to force kwarg only for `looking_for_mate`
    def get_only_winning_move(self, node: GameNode, winner: Color, *,looking_for_mate: bool) -> Optional[TbPair]:
        """
        Returns `None` if the check is not applicable:
            - The position has more than 7 pieces.
            - The puzzle is a mate puzzle. DTZ does not garantee the fastest mate. Also a mate in N puzzle
                  can be correct even if there also exists a N+1 mate.
            - It's not `winner`'s turn.
            - There is no legal moves
            - There is an error processing the API result, or if the API is unreachable.
        """
        if looking_for_mate:
            return None
        board = node.board()
        if len(chess.SquareSet(board.occupied)) > 7 or board.turn != winner:
            return None
        fen = board.fen()
        try:
            rep = self.session.get(TB_API.format(fen)).json()
        except requests.exceptions.RequestException as e:
            self.log.warning(f"req error while checking tb for fen {fen}: {e}")
            return None
        if rep["category"] != "win":
            self.log.debug(f"TB position {fen} is not winning")
            return TbResult(None)
        # Normally the API return results in descending order 
        # So only checking for the first two moves should be enough to know 
        # if there are more than one winning move. Conservatively still check all of them.
        only_winning_move = None
        for move in rep["moves"]:
            # move["category"] is from the opponent's point of vue
            if move["category"] == "loss":
                if only_winning_move is None:
                    only_winning_move = EngineMove(chess.Move.from_uci(move["uci"]), chess.engine.Cp(999999998))
                else:
                    self.log.debug(f"in position {fen}, {only_winning_move} and {move['uci']}({move['san']}) are winning, opponent's category: {move['category']}")
                    return TbResult(None)
        return TbResult(only_winning_move)

def sorted_by_wdl(moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]
    wdl_to_int_dict: Dict[WDL: int] = {
        "win": 7,
        "maybe-win": 6,
        "draw": 5,
        "blessed-loss": 4,
        "maybe-loss": 3,
        "loss": 2,
        "unknown": 1
    }
    return sorted(moves, key = lambda move: wdl_to_int_dict[move["category"]], reverse = True)

def to_engine_move(move: Dict[str, Any], *,turn: Color, winner: Color) -> EngineMove:
    return EngineMove(chess.Move.from_uci(move["uci"]), chess.engine.Cp(move["cp"]))


# conservative, because considering maybe-win as a draw, and maybe-loss as a loss
def wdl_to_cp(wdl: WDL) -> chess.engine.Cp:
    if wdl == "win":
        return chess.engine.Cp(999999998)
    elif wdl in ["maybe-win", "cursed-win", "draw", "blessed-loss"]:
        return chess.engine.Cp(0)
    elif wdl in ["unknown", "maybe-loss", "loss"]:
        return chess.engine.Cp(-999999998)



