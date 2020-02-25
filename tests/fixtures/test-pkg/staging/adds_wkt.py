import os
import csv
import random
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from pprint import pprint as pp

workspace = "/Users/awuthrich/Downloads"
input_file = os.path.join(workspace, "MOCK_DATA.csv")
output_file = os.path.join(workspace, "MOCK_DATA_COMPLETE.csv")

with open(input_file, "r") as f:
    records = list(csv.DictReader(f))

pp(records[1])

for record in records:
    pnt = Point(random.uniform(-122.5, -122.0), random.uniform(37.0, 37.5), srid=4326)
    record["location"] = pnt.wkt

with open(output_file, "w") as of:
    fieldnames = records[0].keys()
    writer = csv.DictWriter(of, fieldnames=fieldnames)
    writer.writeheader()
    for record in records:
        writer.writerow(record)
