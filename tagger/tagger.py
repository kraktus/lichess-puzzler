import argparse
import chess.engine
import cook
import csv
import logging
import pathlib

from chess import Move, Board
from chess.engine import SimpleEngine, Mate, Cp
from chess.pgn import Game, GameNode
from datetime import datetime
from model import Puzzle, TagKind
from typing import List, Tuple, Dict, Any
from zugzwang import zugzwang

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', datefmt='%m/%d %H:%M')
logger.setLevel(logging.INFO)

HOME = pathlib.Path.home()

def read(dic: dict[str, any]) -> Puzzle:
    board = Board(dic["FEN"])
    node: GameNode = Game.from_board(board)
    for uci in dic["Moves"].split():
        move = Move.from_uci(uci)
        node = node.add_main_variation(move)
    return Puzzle(dic["PuzzleId"], node.game(), 999999999)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='tagger.py', description='automatically tags lichess puzzles')
    parser.add_argument("--dry", "-d", help="dry run", action="store_true")
    args = parser.parse_args()
    threads = int(args.threads)

    total = 0
    computed = 0
    updated = 0
    with open(f'{HOME}/Github/lichess-puzzler/mate_untagged.csv', 'r') as f:
        with open(f'{HOME}/Github/lichess-puzzler/puzzle_new_tags.csv', 'w') as output:
            puzzles = csv.DictReader(f)
            writer = csv.DictWriter(output, fieldnames=['PuzzleId', 'NewTags'])
            writer.writeheader()
            for i, puz_dic in enumerate(puzzles):
                if i % 1000 == 0:
                    print('\r ', f'{i} puzzles processed', end='')
                tags = set(cook.cook(read(puz_dic)))
                existing = set(puz_dic["Themes"].split())
                new_tags = [tag for tag in tags if tag not in existing]
                # write to a csv id, new_tags
                if new_tags and not args.dry:
                    updated += 1
                    writer.writerow({'PuzzleId': puz_dic["PuzzleId"], 'NewTags': ' '.join(new_tags)})

