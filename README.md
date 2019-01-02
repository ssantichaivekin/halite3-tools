Helpful tools for halite analysis.

Each file, although shares some similar functions, does not depend on each other.
Most of the files use json config file. I believe this makes it easier to come back
and understand the file long after it has been written.

- zstd_to_json.py
  Convert zstandard (.hlt) files to json.

- replays_analyze.py
  Analyze replays downloaded from halite client.

- collect_analyze.py
  Analyze the halite collection of one bot in the map. We believe that it is just good enough
  to analyze the halite collection in a normal maps and compare them.

- run_halite_games.py
  Run halite games using the json config file.




