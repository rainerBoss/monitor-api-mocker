import json
import sys

from page import Page

page = Page(sys.argv[1])

data = page.get_json()

with open("data.json", "w+", encoding="utf-8") as file:
    json.dump(data, file, indent=4)