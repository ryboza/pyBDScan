from pyusbtin.usbtin import USBtin, CANMessage

def on_button_click(usbtin):
    print("Button clicked!")
    usbtin.send(CANMessage(0x5abbfe0, []))