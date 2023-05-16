import json
import sys

def parse(lines, next_pos, element):
    if element == "{":
        value, next_pos = parse_list(lines, next_pos)
        if value and value[0] == "\"" and value[-1] == "\"":
            value = value[1:-1]
        return value, next_pos
    else:
        if element[0] == "\"" and element[-1] == "\"":
            element = element[1:-1]
        return element, next_pos

def parse_list(lines, pos):
    ret = []
    while 1:
        if pos == len(lines):
            return ret, pos
        line = lines[pos].strip()
        pos += 1
        if not line:
            continue

        if len(line) > 1 and line[-1] == "}":
            lines.insert(pos, "}")
            line = line[:-1].strip()
        
        if "=" not in line and len(line) > 1 and line[-1] == "{":
            line = line[:-1] + "=" + line[-1]

        if "{" in line and line[-1] != "{":
            lines.insert(pos, line.split("{")[1])
            line = line.split("{")[0] + "{"
        
        if line == "}":
            return ret, pos
        
        if line.count("=") == 1:
            key, value = line.split("=")
            value, pos = parse(lines, pos, value)
            ret.append((key, value))
        else:
            value, pos = parse(lines, pos, line)
            ret.append(value)
        
# Used for debugging
def get_unique_keys(data):
    ret = []
    for element in data:
        if not isinstance(element, tuple):
            print("get_unique_keys got a non-tuple:", element)
        elif not element[0] in ret:
            ret.append(element[0])
    return ret

# Used for debugging
def search_for_key(data, path, key):
    ret = []
    for element in data:
        if isinstance(element, tuple):
            if element[0] == key:
                ret.append(path + "/" + element[0])
            sub_ret = search_for_key(element[1], path + "/" + element[0], key)
            if sub_ret:
                ret.append(sub_ret)
        else:
            if element == key:
                ret.append(path + "/" + element[0])
    return ret

def get_first(data, key):
    for element in data:
        if isinstance(element, tuple) and element[0] == key:
            return element[1]
    return None

def get_countries_coast_dev(provinces, coast_provinces):
    countries_coast_dev = {}
    for province_id in coast_provinces:
        province = get_first(provinces, "-" + str(province_id))
        owner = get_first(province, "owner")
        cores = get_first(province, "cores")[0].split(" ")
        if owner in cores:
            dev = float(get_first(province, "base_tax")) + float(get_first(province, "base_production")) + float(get_first(province, "base_manpower"))
            dev = int(dev)
            if owner in countries_coast_dev:
                countries_coast_dev[owner] += dev
            else:
                countries_coast_dev[owner] = dev
    return countries_coast_dev

def get_player_countries(root):
    player_countries = {}
    ugly_list = get_first(root, "players_countries")
    for i in range(0, len(ugly_list), 2):
        player_countries[ugly_list[i]] = ugly_list[i + 1]
    return player_countries


if len(sys.argv) != 2:
    print("Path to the EU4 save file:")
    path = input()
else:
    path = sys.argv[1]

with open(path) as file:
    lines = file.readlines()
with open("coast_provinces.json") as file:
    coast_provinces = json.loads(file.read())
print("Calculating ...")

lines = lines[1:]
root, _ = parse_list(lines, 0)

provinces = get_first(root, "provinces")

countries_coast_dev = get_countries_coast_dev(provinces, coast_provinces)

player_countries = get_player_countries(root)

player_scores = {}
for player, country in player_countries.items():
    player_scores[player] = countries_coast_dev[country]

print("Countries dev:")
sorted_items = sorted(countries_coast_dev.items(), key=lambda x: x[1], reverse=True)
for key, value in sorted_items:
    print(f"{key}: {value}")

print()
print("Player score:")
sorted_items = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
for key, value in sorted_items:
    print(f"{key}: {value}")
