from bs4 import BeautifulSoup
import httpx
import json
import random
import string
import datetime
import sys

types = {
    "Int32": lambda *args: random.randint(0,2147483647),
    "Int64": lambda *args: random.randint(0,9223372036854775807),
    "String": lambda field_name, *args: field_name + str(random.randint(0,100)),
    "Boolean": lambda *args: bool(random.randint(0,1)),
    "Decimal": lambda *args: random.randint(0,2147483647)/random.randint(0,1000000000),
    "DateTimeOffset": lambda *args: str(datetime.datetime.now()),
    "Guid": lambda *args: "588D53FE-EC54-43F1-9FCF-C4C35C55BEB5",
    "TimeSpan": lambda *args: str(random.randint(0,2147483647)),
}

query = sys.argv[1]

parts_url = f"https://api.monitor.se/api/Monitor.API.{query}.html"

r = httpx.get(parts_url)

r.raise_for_status()

soup = BeautifulSoup(r.text, features="html.parser")

all_code = soup.find_all("code")

example = all_code[3]

json_data: dict = json.loads(example.text)

def get_type(field):
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if cells and cells[0].text.strip() == field:  # Check first cell
            return cells[1].text.strip() if len(cells) > 1 else None

finished_json = {}
for k,v in json_data.items():
    type_ = get_type(k)
    type_func = types.get(type_, lambda *args: type_)
    finished_json[k] = type_func(k)

with open("output.json", "w+") as file:
    json.dump(finished_json, file, indent=4)

