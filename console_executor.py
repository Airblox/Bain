import json


with open("item_database.json") as file:
    data = json.load(file)

for k, v in data.items():
    if v["valid"]:
        v["image_link"] = ""

with open("item_database.json", "w") as file:
    json.dump(data, file)
