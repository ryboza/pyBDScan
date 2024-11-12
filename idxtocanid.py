
value =1710
result = (value << 14) | 0x04003FE0
print("Send: " + hex(result))
result = (value << 14) | 0x0C003FE0
print("Return: " + hex(result))
