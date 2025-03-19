import os
import json
import helpers
import time

filenames = list()
for item in os.listdir():
    if "Cable_data" in item:
        filenames.append(item)


print(f"found these files: {filenames}")

for filename in filenames:
    print(f"showing file: {filename}")
    time.sleep(1)
    with open(filename, 'r') as file:
        review_data = json.load(file)

    helpers.plot_data(review_data)