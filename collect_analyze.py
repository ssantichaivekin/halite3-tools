# We compare different bots running using the same map
# The different bots are displayed using different colors.
import json
import os
import matplotlib.pyplot as plt

def production_density(game) :
    game_map = game["production_map"]
    game_grid = game_map["grid"]

    count_cell = 0
    total_production = 0

    for row in game_grid :
        for cell in row :
            cell_energy = cell["energy"]
            count_cell += 1
            total_production += cell_energy

    density = total_production / count_cell
    return density

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

def filter_num_players(num_players, replay_list) :
    return [replay for replay in replay_list if replay["players"] == num_players]

def filter_map_size(map_size, replay_list) :
    return [replay for replay in replay_list if replay["mapsize"] == map_size]

def filter_map_sizes(map_sizes, replay_list) :
    return [replay for replay in replay_list if replay["mapsize"] in map_sizes]

def jsons_in_folder(folderpath) :
    jsonpaths = []
    filenames = os.listdir(folderpath)
    for filename in filenames :
        if filename.endswith(".json") and "temp" not in filename :
            jsonpaths.append(os.path.join(folderpath, filename))
    return jsonpaths

if __name__ == '__main__' :
    # read the folders and then plot each of the folder

    with open('./collect_analyze_config.json', 'r') as config_file :
        config = json.loads(config_file.read())

    # map sizes and x axis display mode are the same across
    # different folder group.

    n_players = config["n_players"]
    if not (n_players == 2 or n_players == 4) :
        raise Exception("Wrong number of players: n_players = %d" % n_players)

    map_sizes = config["map_sizes"]
    if not map_sizes :
        raise Exception("Empty map_sizes")

    x_axis_display = config["x_axis_display"]
    if not (x_axis_display == 'mapsize' or x_axis_display == 'density') :
        raise Exception("Invalid x_axis_display value (should be 'mapsize' or 'density'): %s" % x_axis_display)

    folderpaths = config["folder_paths"]

    plt.title("Average halite -- higher is better")

    for i, folderpath in zip(range(len(folderpaths)), folderpaths) :

        # for each of the folder in folder paths,
        # we create a plot (scatter plot) for it with
        # a specific color and some transparancy setting.

        temppath = os.path.join(folderpath, "collect_analyze_temp.json")
        try :
            with open(temppath, 'r') as tempfile :
                replay_infos = json.loads(tempfile.read())
        except :
            # else create one also
            jsonpaths = jsons_in_folder(folderpath)
            replay_infos = [read_replay_for_halite(json_path) for json_path in jsonpaths]
            # create a tempfile
            with open(temppath, 'w') as tempfile :
                tempfile.write(json.dumps(replay_infos))
        
        if (x_axis_display == 'mapsize') :
            x = map_sizes
            y = []
            for map_size in map_sizes :
                # compute the average halite for that map size
                filtered_infos = filter_num_players(n_players, replay_infos)
                filtered_infos = filter_map_size(map_size, filtered_infos)

                total_halite = 0
                n = len(filtered_infos)

                for replay_info in filtered_infos :
                    total_halite += replay_info["halite"]

                average_halite = total_halite / n
                y.append(average_halite)
            plt.plot(x, y, 'o')
        else : # x_axis_display == 'density'
            filtered_infos = filter_num_players(n_players, replay_infos)
            filtered_infos = filter_map_sizes(map_sizes, filtered_infos)

            # sort by production density
            filtered_infos.sort(key = lambda replay_info: replay_info["production_density"])

            # x = average production densities
            # y = average endgame halite
            if i == 0 :
                x = []
                y = []

                # we have a histogram of ten items
                # the replays are divided (sometimes unevenly) into ten chunks.
                # the last chunk can contain extra chunks.

                if len(filtered_infos) < 10 :
                    raise Exception("Too little data to plot")
                
                chunksize = len(filtered_infos) // 10

                for chunk_i in range(10) :
                    begin_i = chunk_i * chunksize
                    end_i = begin_i + chunksize
                    # note the special end for last chunk
                    if chunk_i == 9 :
                        end_i = len(filtered_infos) - 1

                    n = end_i - begin_i
                    total_production_density = 0
                    total_halite = 0

                    for replay_info in filtered_infos[begin_i: end_i] :
                        total_production_density += replay_info["production_density"]
                        total_halite += replay_info["halite"]

                    # round to make it easy to look at
                    average_production_density = round(total_production_density / n, 1)
                    average_halite = total_halite / n

                    x.append(average_production_density)
                    y.append(average_halite)
                
                a = list(range(10))

                # TODO: wait... actually it doesn't work this way.
                # I guess we will have to refer to the first folder to plots/
                # subplots splitting for reference. This is not that hard to do.
                # First create 10 buckets in the first pass of the loop.
                # Then, in the next pasts, refer to that bucket. A replay goes
                # into a bucket that its halite average is the closest to.
                # That is, its distance is lowest.

                plt.plot(a, y, 'o', alpha = 0.3)
                plt.xticks(a, x)

            else :
                # We already have x. We are only calculating y.
                replay_buckets = [ [] for _ in range(10)]
                for replay_info in filtered_infos :
                    destination_bucket = -1
                    min_dist = 9999999
                    for i_bucket, x_halite in zip(range(10), x) :
                        dist = abs(x_halite - replay_info["production_density"])
                        if dist < min_dist :
                            destination_bucket = i_bucket
                            min_dist = dist
                    replay_buckets[destination_bucket].append(replay_info)
                
                y = []
                print(replay_buckets)
                for replay_list in replay_buckets :
                    halite_list = [ replay_info["halite"] for replay_info in replay_list]
                    if halite_list == [] :
                        average_halite = None
                    else :
                        average_halite = sum(halite_list) / len(halite_list)
                    y.append(average_halite)
                
                plt.plot(a, y, 'o', alpha = 0.3)
                




    
    plt.show()


