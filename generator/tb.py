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
    allowed_methods=["GET"]
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRAT)

class TbChecker:

    def __init__(self, log: logging.Logger) -> None:
        self.session = requests.Session()
        self.session.mount("http://", ADAPTER)
        self.session.mount("https://", ADAPTER)
        self.log = log

    def is_valid(self, node: GameNode, pair: NextMovePair, looking_for_mate: bool) -> Optional[bool]:
        """
        Returns `None` if the check is not applicable:
            - The position has more than 7 pieces.
            - The puzzle is a mate puzzle. DTZ does not garantee the fastest mate. Also a mate in N puzzle
                  can be correct even if there also exists a N+1 mate.
            - There is an error processing the API result, or if the API is unreachable.
        """
        if looking_for_mate:
            return None
        board = node.board()
        if len(chess.SquareSet(board.occupied)) > 7:
            return None

        fen = board.fen()
        expected_move = pair.best.move.uci()
        try:
            rep = self.session.get(TB_API.format(fen)).json()
        except requests.exceptions.RequestException as e:
            self.log.warning(f"req error while checking move pair for {fen}: {e}")
            return None
        # DEBUG
        import json
        print("rep", json.dumps(rep, indent=2))
        # DEBUG
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



    # def check_winning(self: PuzzleChecker, fen: str, expected_move: str, rep: Dict[str, Any]) -> Set[Error]:
    #     res = set()
    #     if rep["category"] != "win":
    #         log.error(f"position {fen} can't be won by side to move, category: " + "{}".format(rep["category"]))
    #         res.add(Error.Wrong)
    #     for move in rep["moves"]:
    #         # move["category"] is from the opponent's point of vue
    #         if move["uci"] == expected_move and move["category"] != "loss":
    #             log.error(f"in position {fen}," + " {}({}) is not winning, opponent's category: {}".format(move["uci"], move["san"], move["category"]))
    #             res.add(Error.Wrong)
    #         elif move["category"] == "loss" and move["uci"] != expected_move: # a winning move which is not `expected_move`, puzzle is wrong 
    #             log.error(f"in position {fen}," + " {}({}) is also winning".format(move["uci"], move["san"]))
    #             res.add(Error.Multiple)
    #     return res

    # def check_drawing(self: PuzzleChecker, fen: str, expected_move: str, rep: Dict[str, Any]) -> Set[Error]:
    #     res = set()
    #     if not is_draw(rep):
    #         log.error(f"position {fen} is not draw, category: " + "{}".format(rep["category"] ))
    #         res.add(Error.Wrong)
    #     for move in rep["moves"]:
    #         # move["category"] is from the opponent's point of vue
    #         if move["uci"] == expected_move and not is_draw(move):
    #             log.error(f"in position {fen}," + " {}({}) is not drawing, opponent's category: {}".format(move["uci"], move["san"], move["category"]))
    #             res.add(Error.Wrong)
    #         elif is_draw(move) and move["uci"] != expected_move: # a drawing move which is not `expected_move`, puzzle is wrong 
    #             log.error(f"in position {fen}," + " {}({}) is also drawing".format(move["uci"], move["san"]))
    #             res.add(Error.Multiple)
    #     return res

    # def check_mate(self: PuzzleChecker, fen: str, expected_move: str, rep: Dict[str, Any], mate_in: int) -> Set[Error]:
    #     res = set()
    #     if rep["category"] != "win":
    #         log.error(f"position {fen} can't be won by side to move, category: " + "{}".format(rep["category"]))
    #         res.add(Error.Wrong)
    #     if rep["dtm"] is not None and rep["dtm"] != mate_in:
    #         log.error("position {} is not mate in {}, but {}.".format(fen, mate_in, rep["dtm"]))
    #         res.add(Error.Wrong)
    #     for move in rep["moves"]:
    #         # move["category"] is from the opponent's point of vue
    #         if move["checkmate"]: # Always good
    #             continue
    #         if move["uci"] == expected_move:
    #             if move["category"] != "loss":
    #                 log.error(f"in position {fen}," + " {}({}) is not winning, opponent's category: {}".format(move["uci"], move["san"], move["category"]))
    #                 res.add(Error.Wrong)
    #         elif move["dtm"] is not None:
    #             # Another move that result in a mate in the same number of moves
    #             if move["category"] == "loss" and -move["dtm"] == (mate_in - 1) : # DTM is negative since from the opponent point of view
    #                 log.error("position {} after {} is not mate in {}, but {}.".format(fen, move["uci"], mate_in - 1, -move["dtm"]))
    #                 res.add(Error.Multiple)
    #         # Not checking puzzles without DTM because it is not possible to reliably convert DTZ to DTM.