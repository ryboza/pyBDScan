from ..km273_tables import KM273_elements_default
from .read_element_ist import *
import json
def KM273_LoadElementList(hash):
    name = hash["NAME"]
    print(f"{name}: KM273_LoadElementList")
    if "statefile" not in attr["global"]:
        return "No statefile specified"
    elementListFile = attr["global"]["statefile"]
    elementListFile = elementListFile.replace("fhem.save", "KM273ElementList.json")
    try:
        with open(elementListFile, "r") as fh:
            content = fh.read()
    except IOError as e:
        print(f"{name}: KM273_LoadElementList: Cannot open {elementListFile}: {e}")
        return f"Cannot open {elementListFile}: {e}"
    try:
        KM273_elements = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"{name}: KM273_LoadElementList: json file {elementListFile} is faulty: {e}")
        return None
    print(f"{name}: KM273_LoadElementList: json file {elementListFile} has been loaded")
    KM273_ReadElementListStatus["done"] = 1
    return None