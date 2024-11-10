from ..km273_tables import *
import json
def KM273_StoreElementList(hash):
    name = hash['NAME']
    print(name, 3, f"{name}: KM273_StoreElementList")
    if not attr['global']['statefile']:
        return "No statefile specified"
    elementListFile = attr['global']['statefile'].replace('fhem.save', 'KM273ElementList.json')
    try:

    except ImportError as e:
        print(name, 1, f"{name}: KM273_StoreElementList: json/utf8 library missing: {e}")
        return None
    try:
        with open(elementListFile, 'w') as fh:
            fh.write("{\n")
            first = True
            for key in sorted(KM273_elements.keys()):
                if not first:
                    fh.write(",\n")
                fh.write(f'"{key}":' + json().new().utf8().encode(KM273_elements[key]))
                first = False
            fh.write("\n}")
    except Exception as e:
        print(name, 3, f"{name}: KM273_StoreElementList: Cannot open {elementListFile}: {e}")
        return f"Cannot open {elementListFile}: {e}"
    print(name, 3, f"{name}: KM273_StoreElementList: json file {elementListFile} has been stored")
    return f"json file {elementListFile} has been stored"

