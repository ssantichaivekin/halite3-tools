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

def read_replay_for_rank(jsonpath) :
    # read a json replay in file path and return
    # { "players":, "mapsize":, "production_density":, "my_rank":}

    # write print to indicate progress

    with open(jsonpath, 'r') as jsonfile :
        jsondata = jsonfile.read()

        try :
            game = json.loads(jsondata)
        except :
            raise Exception("Invalid Data: %s" % jsonpath)
        
        players = game["number_of_players"]
        mapsize = game["production_map"]["width"]
        density = production_density(game)

        pid = None
        for i, player in zip(range(4), game["players"]) :
            if "ssantichaivekin" in player["name"] :
                pid = i
        
        if pid == None :
            raise Exception("Cannot find player ssantichaivekin.")

        my_rank = game["game_statistics"]["player_statistics"][pid]["rank"]

        return {
            "players": players,
            "mapsize": mapsize,
            "production_density": density,
            "my_rank": my_rank
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
    # read in a folderpath, then analyze that folder path as follows:
    # select filter (1) two players, four players
    # select filter (2) map size 32, 40, 48, 56, 64 : can choose multiple map size
    #                                                 split by space
    # asks whether to display winrate vs mapsize or winrate vs halite density
    # uses matplotlib to plot

    print("Please input folder path")
    folderpath = input().strip()
    jsonpaths = jsons_in_folder(folderpath)
    # we will process all the replays in that folder.

    print("Enter the number of players you want to take the sample")
    n_players = int(input().strip())
    if not (n_players == 2 or n_players == 4) :
        raise Exception("Wrong number of players: n_players = %d" % n_players)
    
    print("Select the map sizes you want to display seperated by space (eg '32 40 48')")
    map_sizes = list(map(int, input().split()))
    if not map_sizes :
        raise Exception("Empty map_sizes")

    print("Select your x-axis : can either be 'mapsize' or 'density'")
    x_axis = input().strip()
    if not (x_axis == 'mapsize' or x_axis == 'density') :
        raise Exception("Invalid x_axis value : %s' x_axis")


    # read the tempfile if exist :
    temppath = os.path.join(folderpath, "analyze_temp.json")
    try :
        with open(temppath, 'r') as tempfile :
            replay_infos = json.loads(tempfile.read())
    except :
        # else create one also
        replay_infos = [read_replay_for_rank(json_path) for json_path in jsonpaths]
        # create a tempfile
        with open(temppath, 'w') as tempfile :
            tempfile.write(json.dumps(replay_infos))

    if (x_axis == 'mapsize') :
        x = map_sizes
        y = []
        for map_size in map_sizes :
            # compute the average rank for that map size
            this_infos = filter_num_players(n_players, replay_infos)
            this_infos = filter_map_size(map_size, this_infos)

            total_rank = 0
            n = len(this_infos)

            for replay_info in this_infos :
                total_rank += replay_info["my_rank"]

            average_rank = total_rank / n
            y.append(average_rank)
        plt.plot(x, y, 'o')
        plt.show()
 
    else : # x_axis == 'density'
        # then we have to create a histogram
        # we first split the replays in to ten sections
        # then, for each section, find the average rank
        filtered_infos = filter_num_players(n_players, replay_infos)
        filtered_infos = filter_map_sizes(map_sizes, filtered_infos)

        # sort by production density (average halite in map)
        filtered_infos.sort(key=lambda replay_info: replay_info["production_density"])

        # x = average production densities
        # y = average rank
        x = []
        y = []

        # the remainder is pushed into the last chunk.

        if len(filtered_infos) < 10 :
            raise Exception("Too little data to plot")
        
        chunksize = len(filtered_infos) // 10
        
        for chunk_i in range(10) :
            begin_i = chunk_i * chunksize
            end_i = begin_i + chunksize
            # note the special end for the last chunk.
            if chunk_i == 9:
                end_i = len(filtered_infos) - 1
            
            n = end_i - begin_i
            total_production_density = 0
            total_rank = 0

            for replay_info in filtered_infos[begin_i: end_i] :
                total_production_density += replay_info["production_density"]
                total_rank += replay_info["my_rank"]
            
            # round to make it easy to look at
            average_production_density = round(total_production_density / n, 2)
            average_rank = total_rank / n

            x.append(average_production_density)
            y.append(average_rank)
        
        a = list(range(10))

        fig, ax = plt.subplots()

        fig.canvas.draw()

        plt.plot(a, y)
        plt.xticks(a, x)
        plt.show()


            

            

