#!/usr/bin/env python3
"""
Gets all race records from ql.leeto.fi with ranks recalculated/fixed.
"""

import json
import operator
import os
import requests

base_path = "oldtop"
os.makedirs(base_path, exist_ok=True)

data = requests.get("http://ql.leeto.fi/api/race").json()
maps = sorted([x["MAP"] for x in data["data"]["maps"]])
print("Found {} maps".format(len(maps)))

maps_path = os.path.normpath("{}/maps.json".format(base_path))
with open(maps_path, "w") as maps_file:
    data = {"maps": maps}
    json.dump(data, maps_file)
    print("wrote {}".format(maps_path))

mode_params = [{}, {"weapons": "off"}, {"ruleset": "vql", "weapons": "on"},
               {"ruleset": "vql", "weapons": "off"}]

for map_name in maps:
    print("Getting data for {}".format(map_name))
    map_path = os.path.normpath("{}/{}".format(base_path, map_name))
    os.makedirs(map_path, exist_ok=True)

    for mode in range(4):
        params = mode_params[mode]
        data = requests.get("http://ql.leeto.fi/api/race/maps/{}".format(map_name), params=params).json()
        records = data["data"]["scores"]
        records.sort(key=operator.itemgetter("GAME_TIMESTAMP"))
        records.sort(key=operator.itemgetter("SCORE"))

        prev_time = 0
        prev_rank = 0
        for index, record in enumerate(records, start=1):
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
                rank = index
            record["rank"] = rank

            prev_time = record["time"]
            prev_rank = rank

        records_path = os.path.normpath("{}/{}.json".format(map_path, mode))
        with open(records_path, "w") as records_file:
            data = {"records": records}
            json.dump(data, records_file)
            print("Wrote {}".format(records_path))
