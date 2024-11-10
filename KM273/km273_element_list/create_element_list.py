from ..km273_tables import KM273_elements_default
from .read_element_ist import *
def KM273_CreateElementList(hash):
    name = hash['NAME']
    print(name, 3, f"{name}: KM273_CreateElementList")
    KM273_ReadElementListElements = {}
    for elementRef in KM273_elements_default:
        text = elementRef['text']
        idx = elementRef['idx']
        extid = elementRef['extid']
        max = elementRef['max']
        min = elementRef['min']
        KM273_ReadElementListElements[text] = {'idx': idx, 'extid': extid, 'max': max, 'min': min}
    KM273_ReadElementListStatus['done'] = 1