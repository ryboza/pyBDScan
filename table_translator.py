from KM273.km273_tables.elements_default import KM273_elements_default
from KM273.km273_tables.format import KM273_format
def translate_can_id(index):
    """
    Translates the received index into a CAN ID and formats it according to the specified structure.
    
    Args:
    index (int): The index to translate.

    Returns:
    str: The formatted string with the translated CAN ID.
    """
    # Calculate the CAN ID for receiving the value
    can_id_receive = (index << 14) | 0x0C003FE0
    
    # Format the CAN ID as hexadecimal
    can_id_hex = f'{can_id_receive:X}'  # Converts to hexadecimal without 0x prefix
        
    return can_id_hex

def index_from_can_id(can_id):
    """
    Calculates the index from the given CAN ID.

    Args:
    can_id (str): The CAN ID in hexadecimal format.

    Returns:
    int: The index corresponding to the CAN ID, or None if not found.
    """
    # Convert the CAN ID from hexadecimal string to an integer
    can_id_value = int(can_id, 16)

    # Reverse the calculation to find the index
    index = (can_id_value & 0x3FFFFC0) >> 14  # Mask and shift to extract the index
    
    return index

def print_element_by_index(index):
    """
    Prints the details of the element with the specified index.

    Args:
    index (int): The index of the element to print.
    """
    # Find the element with the specified index
    for element in KM273_elements_default:
        if element['idx'] == index:
            # Print the details of the found element
            print(f"Index: {element['idx']}")
            print(f"External ID: {element['extid']}")
            print(f"Max: {element['max']}")
            print(f"Min: {element['min']}")
            print(f"Format: {element['format']}")
            print(f"Read: {element['read']}")
            print(f"Text: {element['text']}")
            return
    
    print(f"No element found with index {index}")


