def read_replay_for_halite(jsonpath) :
    # read a json replay assuming that there is only one player playing.
    # we use this to measure the most efficient way to collect halite.
    # since we assume that there is only one player actively trying to
    # collect halite. we can just return the grater halite.

    # return { "players":, "mapsize":, "production_density":, "halite":}
    
    with open(jsonpath, 'r') as jsonfile :
        jsondata = jsonfile.read()
        game = json.loads(jsondata)
        
        players = game["number_of_players"]
        mapsize = game["production_map"]["width"]
        density = production_density(game)

        max_production = 0
        for player_stat in game["game_statistics"]["player_statistics"] :
            if player_stat["final_production"] > max_production :
                max_production = player_stat["final_production"]

        return {
            "players": players,
            "mapsize": mapsize,
            "production_density": density,
            "halite": max_production
        }