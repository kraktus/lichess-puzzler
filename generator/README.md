Generate puzzles from a PGN file! It will look at all games, and analyse them if needed.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 generator.py --help
python3 generator.py -t 6 -v -f my_file.pgn # If stockfish installed globally, otherwise use `--engine PATH_TO_YOUR_UCI_ENGINE`
```

BOT games are also looked at if any. The ouput file will be a csv with the same name as your input PGN file, and the following headers `white,black,game_id,fen,ply,moves,cp,generator_version`.

Important! If something does not work, make sure you version matches [this one](https://github.com/kraktus/lichess-puzzler/blob/730329a24e0a402f760b1392320bdaaada052ce2/generator/generator.py#L22). if you don't see `WC` in the version, you have probably not chosen the right branch.
