# Download replay of a specific bot version to a designated folder
import json
import requests

# first read the configuration file
with open('./download_config.json', 'r') as config_file :
    config = json.loads(config_file.read())

    user_id = config["user_id"]
    dest_folder_path = config["dest_folder_path"]

limit = 250
replay_infos = []
current = 0
while (current <= 2000) :
    replay_infos_link = f'https://api.2018.halite.io/v1/api/user/{user_id}/match?order_by=desc,time_played&limit={limit}&offset={current}'
    current += limit
    replay_infos += requests.get(replay_infos_link).json()

print(len(replay_infos))

# find the lastest bot version, the latest gameplay must containt the latest bot version
bot_version = replay_infos[0]["players"][str(user_id)]["version_number"]

replay_ids = []

for replay_info in replay_infos :
    # look for my bot info and then keep only the links that their bot version
    # is equal to the version we wanted, then add it to the list
    should_keep = False
    if replay_info["players"][str(user_id)]["version_number"] == bot_version :
        should_keep = True

    if should_keep :
        replay_ids.append(replay_info["game_id"])
    
for replay_id in replay_ids :
    download_link = 




