def KM273_ClearElementLists(hash):
    name = hash['NAME']
    print(name, 3, f"{name}: KM273_ClearElementLists")
    KM273_history = {}
    KM273_readingsRTR = []
    KM273_readingsRTRAll = []
    KM273_writingsTXD = {}
    KM273_elements = {}
    KM273_ReadElementListStatus = {'done': 0, 'wait': 0, 'readCounter': 0, 'readIndex': 0, 'readIndexLast': 0, 'writeIndex': 0, 'KM200active': 0, 'KM200wait': 0, 'readData': ""}
    KM273_ReadElementListElements = {}


