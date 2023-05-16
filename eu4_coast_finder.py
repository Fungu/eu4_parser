import json
from PIL import Image
import os
import csv

def find_land_provinces(directory_path):
    land_provinces = []

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                file_contents = file.read()

                if "base_production" in file_contents:
                    filename = filename.split("-")[0].strip().split(" ")[0]
                    land_provinces.append(int(filename))

    return land_provinces

def parse_csv_file(file_path):
    province_colors = {}
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        next(reader)  # Read the header line
        
        for row in reader:
            province_colors[(int(row[1]), int(row[2]), int(row[3]))] = int(row[0])

    return province_colors

def area_search(image, x, y, x_min, land_provinces, province_colors):
    coast_provinces = []
    closed_set = set()
    width, height = image.size
    pixel_queue = [(x, y)]

    while pixel_queue:
        x, y = pixel_queue.pop()
        if x < x_min or x >= width or y < 0 or y >= height:
            continue
        if (x, y) in closed_set:
            continue
        closed_set.add((x, y))

        current_color = image.getpixel((x, y))
        province = province_colors[current_color]
        if province in land_provinces:
            if not province in coast_provinces:
                coast_provinces.append(province)
        else:
            pixel_queue.append((x + 1, y))
            pixel_queue.append((x - 1, y))
            pixel_queue.append((x, y + 1))
            pixel_queue.append((x, y - 1))
    
    return coast_provinces


land_provinces = find_land_provinces("resources/provinces")
province_colors = parse_csv_file("resources/definition.csv")
image = Image.open("resources/provinces.bmp")
coast_provinces = area_search(image, 2730, 800, 2700, land_provinces, province_colors)

out_file = open("coast_provinces.json", "w")
json.dump(coast_provinces, out_file)
