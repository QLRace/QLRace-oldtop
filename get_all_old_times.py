import requests
import os
import json

data = requests.get("http://ql.leeto.fi/api/race").json()
maps = sorted([x["MAP"] for x in data["data"]["maps"]])
print("Found {} maps".format(len(maps)))

os.makedirs("oldtop", exist_ok=True)
maps_path = "oldtop/maps.json"
with open(maps_path, "w") as maps_file:
    data = {"maps": maps}
    json.dump(data, maps_file)
    print("wrote {}".format(maps_path))

mode_params = [{}, {"weapons": "off"}, {"ruleset": "vql", "weapons": "on"},
               {"ruleset": "vql", "weapons": "off"}]

for map_name in maps:
    print("Getting data for {}".format(map_name))
    os.makedirs("oldtop/{}".format(map_name), exist_ok=True)

    for mode in range(4):
        params = mode_params[mode]
        data = requests.get("http://ql.leeto.fi/api/race/maps/{}".format(map_name), params=params).json()
        records = data["data"]["scores"]

        prev_time = 0
        prev_rank = 0
        i = 1
        for record in records:
            record.pop("MAP")
            record.pop("PLAYER_NICK")
            record.pop("PUBLIC_ID")
            record.pop("RANK")
            record.pop("COUNTRY")
            record["name"] = record.pop("PLAYER")
            record["time"] = record.pop("SCORE")
            record["date"] = record.pop("GAME_TIMESTAMP")

            if prev_time == record["time"]:
                rank = prev_rank
            else:
                rank = i
            record["rank"] = rank

            prev_time = record["time"]
            prev_rank = rank
            i += 1

        json_path = "oldtop/{}/{}.json".format(map_name, mode)
        with open(json_path, "w") as json_file:
            data = {"records": records}
            json.dump(data, json_file)
            print("Wrote {}".format(json_path))
