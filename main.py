import asyncio
import tkinter as tk
from tkinter import ttk
from pyusbtin.usbtin import USBtin
from table_translator import *
from queue import Queue, Empty
import tkinter.font as tkFont

class CANMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("BUDERUS CAN Monitor Application")

        # Dictionary to store messages by idx
        self.messages_dict = {}
        self.update_queue = Queue()  # Queue for safely passing messages

        
        # Create a Treeview widget without the "Msg session Id" column
        self.tree = ttk.Treeview(
            master,
            columns=("S_ID", "r/w", "CAN_ID", "INDEX", "KM200_ID", "MAX", "MIN", "FORMAT", "DATA", "VALUE", "UNIT", "DESCRIPTION"),
            show="headings"  # Only show defined columns
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        
        # Configure the grid to make the Treeview expand when the window resizes
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        #Heading configuration
        self.tree.heading("S_ID", text="Msg session Id")
        self.tree.heading("r/w", text="r/w")
        self.tree.heading("CAN_ID", text="CAN ID")
        self.tree.heading("INDEX", text="Index")
        self.tree.heading("KM200_ID", text="KM200 ID")
        self.tree.heading("MAX", text="Max")
        self.tree.heading("MIN", text="Min")
        self.tree.heading("FORMAT", text="Format")
        self.tree.heading("DATA", text="Data")
        self.tree.heading("VALUE", text="Value")
        self.tree.heading("UNIT", text="Unit")
        self.tree.heading("DESCRIPTION", text="Description")
        self.update_timer()  # Start the periodic refresh loop
        
        
    def update_or_add_message(self, msg):
        """
        Updates or adds a message to the dictionary, but does not interact with the Treeview.
        This method assumes the message contains `can_id`, `details`, and `message_type`.
        """
        # Extract relevant data from the message object
        # Default values in case element is not found
        can_id = hex(msg.mid)
        index = index_from_can_id(can_id)
        details = {
            "INDEX": "N/A", 
            "KM200_ID": "N/A", 
            "CAN_ID": "N/A",
            "MAX": "N/A", 
            "MIN": "N/A", 
            "FORMAT": "N/A",                          
            "DATA": "N/A",
            "VALUE": "N/A",
            "UNIT": "N/A",
            "DESCRIPTION": "N/A"          
        }
        # Determine message type (r or w) based on the message
        message_type = 'r' if msg.mid & 0x1 else 'w'  # Adjust condition as needed for your message type

        # Ensure that details are populated by looking up the element in KM273_elements_default
        if index is not None:
            # Search for the element by index in the KM273_elements_default table
            for element in KM273_elements_default:
                if element['idx'] == index:
                    # Populate details from the found element
                    details = {
                        "INDEX": element['idx'],
                        "KM200_ID": element['extid'],
                        "CAN_ID": can_id,
                        "MAX": element['max'],
                        "MIN": element['min'],
                        "FORMAT": element['format'],                          
                        "DATA": msg._data,
                        "VALUE": self.get_value(msg._data, element['format'] ),
                        "UNIT": self.get_unit(element['format'] ),
                        "DESCRIPTION": element['text']
                    }
                    break  # Stop searching once we find the matching element
          # Package message for the queue
        update_data = {
            "index": index, "message_type": message_type, "details": details, 
        }
        self.update_queue.put(update_data)    
          
    def get_value(self, data, format_type):
        """
        Convert raw data based on the format type.
        `data` is expected to be a raw integer value, and `format_type` specifies the data format.
        """
        format_info = KM273_format.get(format_type, {'factor': 1, 'unit': ''})
        factor = format_info['factor']
        
        # Convert data to value by applying the factor
        value = data * factor

        # If 'select' list exists, get the descriptive value for the select options
        if 'select' in format_info:
            # Assuming data is an integer index that maps to an option
            select_options = format_info['select']
            if 0 <= data < len(select_options):
                value = select_options[data].split(':')[1]  # Get the descriptive name after ":"
        
        return value

    def get_unit(self, format_type):
        """
        Retrieve the unit associated with the format type.
        """
        format_info = KM273_format.get(format_type, {'factor': 1, 'unit': ''})
        return format_info['unit']

    def update_treeview(self):
        """
        Refreshes the Treeview by processing messages from the update_queue.
        """
        while not self.update_queue.empty():
            try:
                update = self.update_queue.get_nowait()
                index = update["index"]
                details = update["details"]
                message_type = update["message_type"]

                if index in self.messages_dict:
                    # Update the existing entry
                    self.messages_dict[index].update(details)
                    self.messages_dict[index]["Message Type"] = message_type

                    # Update Treeview entry if it exists
                    tree_id = self.messages_dict[index]["tree_id"]
                    self.tree.item(tree_id, values=(self.messages_dict[index]["counter"],
                                                    message_type, 
                                                    details["CAN_ID"],
                                                    details["INDEX"], 
                                                    details["KM200_ID"],
                                                    details["MAX"], 
                                                    details["MIN"],
                                                    details["FORMAT"], 
                                                    details["DATA"],
                                                    details["VALUE"],
                                                    details["UNIT"],
                                                    details["DESCRIPTION"]))
                                                    
                else:
                    # Insert a new entry if it doesn't exist
                    counter_received = len(self.messages_dict) + 1
                    tree_id = self.tree.insert("", "end", values=(counter_received, 
                                                                  message_type,
                                                                  details["CAN_ID"],
                                                                  details["INDEX"],
                                                                  details["KM200_ID"],
                                                                  details["MAX"], 
                                                                  details["MIN"],
                                                                  details["FORMAT"], 
                                                                  details["DATA"],
                                                                  details["VALUE"],
                                                                  details["UNIT"],
                                                                  details["DESCRIPTION"]))
                    self.messages_dict[index] = {**details, "Message Type": message_type,
                                                 "counter": counter_received, "tree_id": tree_id}

                # Limit the size of messages_dict and Treeview
                if len(self.messages_dict) > 500:
                    # Get the oldest entry by counter and remove it
                    oldest_index = min(self.messages_dict, key=lambda k: self.messages_dict[k]["counter"])
                    self.tree.delete(self.messages_dict[oldest_index]["tree_id"])
                    del self.messages_dict[oldest_index]

            except Empty:
                break
            self.fit_columns_to_content()

    # Logging function to process and display each received message
    def log_data(self, msg):
        """
        Log CAN messages and update the dictionary.
        This method will be called by the USBtin message listener.
        """

        print('Received:', hex(msg.mid))
        self.update_or_add_message(msg)
        

    def update_timer(self):
        """
        Periodically calls `update_treeview` every second using Tkinter’s `after`.
        """
        self.update_treeview()
        self.master.after(1000, self.update_timer)

    def fit_columns_to_content(self):
            """Adjust Treeview column widths to fit the content, with a minimum size for each column."""
            font = tkFont.nametofont("TkDefaultFont")
            
            # Define minimum width for each column except the last one
            min_widths = {
                "Message Type": 80,
                "CAN ID": 80,
                "Index": 50,
                "External ID": 80,
                "Max": 60,
                "Min": 60,
                "Format": 80
            }
            
            # Iterate over each column in the Treeview except the last one
            for col in self.tree["columns"][:-1]:
                max_width = font.measure(self.tree.heading(col, "text"))  # Start with the header text width

                # Measure the width of each cell's content in the column
                for item in self.tree.get_children():
                    cell_text = str(self.tree.set(item, col))
                    max_width = max(max_width, font.measure(cell_text))

                # Set the column width to the maximum of content width or minimum width
                column_width = max(max_width + 10, min_widths.get(col, 50))  # Default min width of 50 if not in min_widths
                self.tree.column(col, width=column_width, stretch=False)

            # Set the last column ("Text") to take up the remaining space
            self.tree.column(self.tree["columns"][-1], width=100, stretch=True)



# Main function to initialize the USBtin connection and Tkinter GUI loop
async def main():
    root = tk.Tk()
    app = CANMonitorApp(root)
    
    usbtin = USBtin()

    try:
        usbtin.connect("COM3")  # Make sure 'COM3' is the correct port
        usbtin.add_message_listener(lambda msg: app.log_data(msg))  # Set up the message listener
        usbtin.open_can_channel(125000, USBtin.ACTIVE)  # Open CAN channel with the required baud rate
    except Exception as e:
        print(f"Error setting up USBtin: {e}")
        return

    print("USBtin is listening for messages... Press Ctrl+C to stop.")
    
    
    # Start Tkinter mainloop in the main thread
    root.mainloop()  # Start the Tkinter event loop


if __name__ == "__main__":
    asyncio.run(main())