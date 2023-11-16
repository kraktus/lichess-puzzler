
lichess puzzler (WC version)
----------------------------

This is a fork of the [lichess puzzle generator](https://github.com/ornicar/lichess-puzzler) (also know as puzzles v2) that allow to generate puzzles from unanalysed PGN for your own usage. See [the generator's README for detailed instructions.](https://github.com/kraktus/lichess-puzzler/tree/WC/generator#readme)

Why not use the official generator?
-----------------------------------

The official generator makes several decisions that only make sense at lichess' scale, for example skipping all games from lower rated players, and games that have no computer analysis in their PGN, and only creating one puzzle per game at most.

By contrast, this fork intentionally will try to extract the maximum of puzzles from the provided PGN (while using the same heuristics to retain quality), for example by analysing games as needed.

Why is it named WC (World Championship) version?
------------------------------------------------

Because I first developped it when I wanted to extract puzzles from 2021's WC games so we could include them in Lichess blogs.
