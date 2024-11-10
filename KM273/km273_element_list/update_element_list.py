
from KM273_tables import *

def KM273_UpdateElements(hash):
    name = hash['NAME']
    print(name, 3, f"{name}: KM273_UpdateElements")
    AddToReadingsKeys = []
    if 'AddToReadings' in attr[name]:
        AddToReadingsKeys = attr[name]['AddToReadings'].split(' ')
    if 'AddToGetSet' in attr[name]:
        AddToReadingsKeys += attr[name]['AddToGetSet'].split(' ')
    AddToReadingsRegex = '|'.join(AddToReadingsKeys)
    KM273_elements = {}
    for elementRef in KM273_elements_default:
        text = elementRef['text']
        read = elementRef['read']
        elem1 = KM273_ReadElementListElements.get(text)
        if re.search(AddToReadingsRegex, text):
            read = 1
            print(name, 3, f"{name}: KM273_UpdateElements AddToReadings {text}")
        if (not elem1) and ((read == 1) or ((read == 2) and 'HeatCircuit2Active' in attr[name] and attr[name]['HeatCircuit2Active'] == 1)):
            days = ["1MON", "2TUE", "3WED", "4THU", "5FRI", "6SAT", "7SUN"]
            for day in days:
                pos = text.find(day)
                if pos > 0:
                    text1 = text[:pos] + text[pos+1:]
                    elem1 = KM273_ReadElementListElements.get(text1)
                    if elem1:
                        print(name, 3, f"{name}: KM273_UpdateElements change {text1} to {text}")
                    break
        if elem1:
            idx = elem1['idx']
            rtr = f"{0x04003FE0 | (idx << 14):08X}"
            txd = f"{0x0C003FE0 | (idx << 14):08X}"
            format = elementRef['format']
            KM273_elements[txd] = {'rtr': rtr, 'idx': idx, 'extid': elem1['extid'], 'max': elem1['max'], 'min': elem1['min'], 'format': format, 'read': read, 'text': text}
        else:
            if read != 0:
                print(name, 3, f"{name}: KM273_UpdateElements {text} not found")
    return None




