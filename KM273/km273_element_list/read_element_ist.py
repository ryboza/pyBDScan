from ..can import *
KM273_ReadElementListStatus = { "done" : 0, 
                                "wait" : 0, 
                                "readCounter" : 0, 
                                "readIndex" : 0, 
                                "readIndexLast" : 0, 
                                "writeIndex" : 0,
                                "KM200active" : 0, 
                                "KM200wait" : 0, 
                                "readData" : ""}
def KM273_ReadElementList(hash):
    name = hash['NAME']
    print(f"{name}: KM273_ReadElementList entry readCounter={KM273_ReadElementListStatus['readCounter']} readIndex={KM273_ReadElementListStatus['readIndex']}")
    if (KM273_ReadElementListStatus['readCounter'] == 0) and (KM273_ReadElementListStatus['KM200wait'] == 0):
        print(f"{name}: KM273_ReadElementList send R01FD7FE00")
        CAN_Write(hash, "R01FD7FE00")
        KM273_ReadElementListStatus['KM200wait'] = 20
    elif KM273_ReadElementListStatus['KM200wait'] > 0:
        KM273_ReadElementListStatus['KM200wait'] -= 1 if KM273_ReadElementListStatus['KM200wait'] > 0
        if KM273_ReadElementListStatus['KM200wait'] <= 0:
            KM273_ReadElementListStatus['KM200active'] = 0
            KM273_ReadElementListStatus['readIndex'] = 0
            KM273_ReadElementListStatus['writeIndex'] = 0
            KM273_ReadElementListStatus['readData'] = ""
        print(f"{name}: KM273_ReadElementList KM200active={KM273_ReadElementListStatus['KM200active']} KM200wait={KM273_ReadElementListStatus['KM200wait']} readIndex={KM273_ReadElementListStatus['readIndex']}")
    elif KM273_ReadElementListStatus['writeIndex'] <= KM273_ReadElementListStatus['readIndex']:
        sendTel = f"T01FD3FE08{4096:08x}{KM273_ReadElementListStatus['writeIndex']:08x}"
        KM273_ReadElementListStatus['writeIndex'] += 4096
        KM273_ReadElementListStatus['wait'] = 20
        print(f"{name}: KM273_ReadElementList send {sendTel}")
        CAN_Write(hash, sendTel)
        print(f"{name}: KM273_ReadElementList send R01FDBFE00")
        CAN_Write(hash, "R01FDBFE00")
    elif (KM273_ReadElementListStatus['wait'] -= 1) <= 0:
        KM273_ReadElementListStatus['readIndexLast'] = KM273_ReadElementListStatus['readIndex']
        KM273_ReadElementListStatus['readIndex'] = 0
        KM273_ReadElementListStatus['writeIndex'] = 0
        KM273_ReadElementListStatus['readData'] = ""
    count = 1
    while count > 0:
        CAN_ReadBuffer(hash)
        count = 0
        dir, canId, len1, value1 = None, None, None, None
        dir = 'R'
        while (dir == 'T') or (dir == 'R'):
            dir, canId, len1, value1 = CAN_Read(hash)
            dir = '_' if dir is None
            if dir == 'T':
                if int(canId, 16) == 0x09FDBFE0:
                    if len1 <= 8:
                        KM273_ReadElementListStatus['readIndex'] += len1
                        value1 <<= 8 * (8 - len1) if len1 < 8
                        KM273_ReadElementListStatus['readData'] += struct.pack("NN", value1 >> 32, value1 & 0xffffffff)
                    if (KM273_ReadElementListStatus['readIndexLast'] > 0) and (KM273_ReadElementListStatus['readIndexLast'] == KM273_ReadElementListStatus['readIndex']):
                        print(f"{name}: KM273_ReadElementList readCounter {KM273_ReadElementListStatus['readCounter']} changed to {KM273_ReadElementListStatus['readIndex']}")
                        KM273_ReadElementListStatus['readCounter'] = KM273_ReadElementListStatus['readIndex']
                    if (not KM273_ReadElementListStatus['KM200active']) and (KM273_ReadElementListStatus['readCounter'] > 0) and (KM273_ReadElementListStatus['readIndex'] >= KM273_ReadElementListStatus['readCounter']):
                        KM273_ReadElementListStatus['done'] = 1
                        print(f"{name}: KM273_ReadElementList done, readCounter={KM273_ReadElementListStatus['readCounter']} readIndex={KM273_ReadElementListStatus['readIndex']}")
                        KM273_ReadElementListElements = {}
                        i1 = 0
                        imax = KM273_ReadElementListStatus['readIndex']
                        idLast = -1
                        while i1 < imax:
                            if imax - i1 > 18:
                                idx, extid, max2, min2, len2 = struct.unpack("nH14NNc", KM273_ReadElementListStatus['readData'][i1:i1+18])
                                min2 = struct.unpack('l*', struct.pack('L*', min2))[0]  # unsigned long to signed long
                                max2 = struct.unpack('l*', struct.pack('L*', max2))[0]
                                if (idx > idLast) and (len2 > 1) and (len2 < 100):
                                    element2 = KM273_ReadElementListStatus['readData'][i1+18:i1+len2-1]
                                    i1 += 18 + len2
                                    KM273_ReadElementListElements[element2] = {'idx': idx, 'extid': extid, 'max': max2, 'min': min2}
                                    print(f"{name}: KM273_ReadElementList done, idx={idx} extid={extid} max={max2} min={min2} element={element2}")
                                else:
                                    print(f"{name}: KM273_ReadElementList error, idx={idx} extid={extid} max={max2} min={min2} len={len2}")
                                    KM273_ReadElementListStatus['done'] = 0
                                    KM273_ReadElementListStatus['KM200active'] = 1
                                    KM273_ReadElementListStatus['KM200wait'] = 20
                                    imax = 0
                            else:
                                i1 += 18
                    count += 1
                elif int(canId, 16) == 0x09FD7FE0:
                    readCounter = value1 >> 24
                    KM273_ReadElementListStatus['readCounter'] = readCounter
                    print(f"{name}: KM273_ReadElementList read T09FD7FE0 len={len1} value={value1} readCounter={readCounter}")
                elif int(canId, 16) == 0x01FD3FE0:
                    dataLen = value1 >> 32
                    dataStart = value1 & 0xffffffff
                    print(f"{name}: KM273_ReadElementList KM200 read canId={canId} len={len1} dataStart={dataStart} dataLen={dataLen}")
                    KM273_ReadElementListStatus['KM200active'] = 1
                    KM273_ReadElementListStatus['KM200wait'] = 20
            elif dir == 'R':
                if (int(canId, 16) == 0x01FD7FE0) or (int(canId, 16) == 0x01FDBFE0):
                    print(f"{name}: KM273_ReadElementList KM200 read canId={canId}")
                    KM273_ReadElementListStatus['KM200active'] = 1
                    KM273_ReadElementListStatus['KM200wait'] = 20
    return None


