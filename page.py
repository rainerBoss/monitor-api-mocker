from bs4 import BeautifulSoup
from dataclasses import dataclass
import json
import httpx
import datetime
import random
import time 

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

class Property:
    def __init__(self, row):
        self.row = row
        self.cells = self.row.find_all("td")

    @property
    def name(self):
        return self.cells[0].text
    
    @property
    def type(self):
        return self.cells[1].text.replace("?", "").replace("[]", "")
    
    @property
    def monitor_type(self) -> str|None:
        href = self.cells[1].find("a")["href"]
        if href.startswith("Monitor.API."):
            return href.replace("Monitor.API.", "").replace(".html", "")
    
    @property
    def nullable(self) -> bool:
        return self.cells[1].text.endswith("?")

    @property
    def array(self) -> bool:
        return self.cells[1].text.endswith("[]")

    @property
    def summary(self):
        return self.cells[2].text
    
    @property
    def expandable(self) -> bool:
        cell_text: str = self.cells[2].text
        return "Expandable" in cell_text
    
class Page:
    def __init__(self, query: str, level=0):
        parts_url = f"https://api.monitor.se/api/Monitor.API.{query}.html"
        r = httpx.get(parts_url)
        r.raise_for_status()
        self.soup = BeautifulSoup(r.text, features="html.parser")
        self.table = self.soup.find("table")
        self.tbody = self.table.find("tbody")
        self.rows = self.tbody.find_all("tr")
        self.level = level

    @property
    def properties(self):
        return[Property(row) for row in self.rows]
    
    def get_value(self, p: Property):
        if p.nullable and not random.randint(0,4): return None
        
        type_func = types.get(p.type)
        if type_func: return type_func(p.name)
        if p.monitor_type:
            page = Page(p.monitor_type, level=self.level+1)
            return page.get_json()
        else: return f"Unknow property type {p.type}"

    def get_json(self):
        data = {}
        for p in self.properties:
            if p.monitor_type and self.level != 0: continue
            value = self.get_value(p)
            data[p.name] = value
        return data