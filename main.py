import asyncio
import tkinter as tk
from tkinter import ttk
from pyusbtin.usbtin import USBtin
from table_translator import *


class CANMonitorApp:
    def __init__(self, master):
        self.master = master
        self.tree = ttk.Treeview(master, columns=("CAN ID", "Index", "External ID", "Max", "Min", "Format", "Text"))
        self.tree.heading("#0", text="CAN Messages")
        self.tree.heading("CAN ID", text="CAN ID")
        self.tree.heading("Index", text="Index")
        self.tree.heading("External ID", text="External ID")
        self.tree.heading("Max", text="Max")
        self.tree.heading("Min", text="Min")
        self.tree.heading("Format", text="Format")
        self.tree.heading("Text", text="Text")
        self.tree.pack()

    def display_message(self, msg):
        can_id = hex(msg.mid)
        index = index_from_can_id(can_id)

        # Default values in case element is not found
        details = {
            "Index": "N/A", 
            "External ID": "N/A", 
            "Max": "N/A", 
            "Min": "N/A", 
            "Format": "N/A", 
            "Text": "N/A"
        }

        # Search for the element by index
        if index is not None:
            for element in KM273_elements_default:
                if element['idx'] == index:
                    # Populate details from the found element
                    details = {
                        "Index": element['idx'],
                        "External ID": element['extid'],
                        "Max": element['max'],
                        "Min": element['min'],
                        "Format": element['format'],
                        "Text": element['text']
                    }
                    break

        # Insert each detail into separate columns
        self.tree.insert("", "end", values=(can_id, details["Index"], details["External ID"], 
                                            details["Max"], details["Min"], details["Format"], details["Text"]))



# Logging function to process and display each received message
def log_data(app, msg):
    print('Received:', hex(msg.mid))
    app.display_message(msg)


# Main function to initialize the USBtin connection and Tkinter GUI loop
async def main():
    root = tk.Tk()
    root.title("CAN Monitor")
    app = CANMonitorApp(root)

    usbtin = USBtin()

    try:
        usbtin.connect("COM3")  # Make sure 'COM3' is the correct port
        usbtin.add_message_listener(lambda msg: log_data(app, msg))  # Set up the message listener
        usbtin.open_can_channel(125000, USBtin.ACTIVE)  # Open CAN channel with the required baud rate
    except Exception as e:
        print(f"Error setting up USBtin: {e}")
        return

    print("USBtin is listening for messages... Press Ctrl+C to stop.")

    # Start Tkinter event loop in the main thread
    root.after(0, lambda: asyncio.create_task(asyncio.sleep(0)))
    root.mainloop()

    try:
        while True:
            await asyncio.sleep(1)  # Keeps the loop running, so the listener remains active
    except asyncio.CancelledError:
        print("Process stopped.")

# Run the async process
asyncio.run(main())
