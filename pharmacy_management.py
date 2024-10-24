import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

class PharmacyManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")

        self.customer_name = tk.StringVar()
        self.customer_contact = tk.StringVar()

        self.medicines = {}  
        self.orders = {}

        self.gst_percentage = 12  

        self.records_file = "past_records.json"
        self.create_gui()

    def create_gui(self):
        # Title with specific font, size, and style
        title_label = tk.Label(self.root, text="QUICK MEDS", font=("Arial", 24, "bold"))
        title_label.pack(pady=10)

        details_frame = tk.LabelFrame(self.root, text="Customer Details", font=("Arial", 14, "bold"))
        details_frame.pack(fill="x", padx=10, pady=10)

        name_label = tk.Label(details_frame, text="Name:", font=("Arial", 12))
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = tk.Entry(details_frame, textvariable=self.customer_name, font=("Arial", 12))
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        contact_label = tk.Label(details_frame, text="Contact:", font=("Arial", 12))
        contact_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        contact_entry = tk.Entry(details_frame, textvariable=self.customer_contact, font=("Arial", 12))
        contact_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        validate_contact_cmd = contact_entry.register(self.validate_contact)
        contact_entry.configure(validate="key", validatecommand=(validate_contact_cmd, "%P"))

        inventory_frame = tk.LabelFrame(self.root, text="Inventory", font=("Arial", 14, "bold"))
        inventory_frame.pack(fill="both", expand=True, padx=10, pady=10)

        add_medicine_label = tk.Label(inventory_frame, text="Add Medicine:", font=("Arial", 12, "bold"))
        add_medicine_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.medicine_name = tk.StringVar()
        self.medicine_price = tk.DoubleVar()

        add_name_entry = tk.Entry(inventory_frame, textvariable=self.medicine_name, font=("Arial", 12))
        add_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        add_price_entry = tk.Entry(inventory_frame, textvariable=self.medicine_price, font=("Arial", 12))
        add_price_entry.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        add_button = tk.Button(inventory_frame, text="Add", command=self.add_medicine, font=("Arial", 12))
        add_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.medicine_frame = tk.Frame(inventory_frame)
        self.medicine_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(fill="x", padx=10, pady=10)

        print_bill_button = tk.Button(buttons_frame, text="Print Bill", command=self.show_bill_popup, font=("Arial", 12, "bold"))
        print_bill_button.pack(side="left", padx=5)

        past_record_button = tk.Button(buttons_frame, text="Past Records", command=self.past_records, font=("Arial", 12, "bold"))
        past_record_button.pack(side="left", padx=5)

        clear_selection_button = tk.Button(buttons_frame, text="Clear Selection", command=self.clear_selection, font=("Arial", 12, "bold"))
        clear_selection_button.pack(side="left", padx=5)

        self.sample_bill_text = tk.Text(self.root, height=10, font=("Arial", 12))
        self.sample_bill_text.pack(fill="x", padx=10, pady=10)

    def add_medicine(self):
        medicine_name = self.medicine_name.get().strip()
        medicine_price = self.medicine_price.get()

        if medicine_name and medicine_price > 0:
            self.medicines[medicine_name] = medicine_price
            self.display_medicines()
            
            # Clear the input fields
            self.medicine_name.set("")
            self.medicine_price.set(0.0)

    def display_medicines(self):
        for widget in self.medicine_frame.winfo_children():
            widget.destroy()

        row = 0
        for medicine, price in self.medicines.items():
            item_var = tk.IntVar()
            item_label = tk.Label(self.medicine_frame, text=f"{medicine} - {self.convert_to_inr(price)}", font=("Arial", 12))
            item_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            quantity_entry = tk.Entry(self.medicine_frame, width=5, font=("Arial", 12))
            quantity_entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")

            self.orders[medicine] = {"var": item_var, "quantity": quantity_entry}

            row += 1

    def show_bill_popup(self):
        if not self.customer_name.get().strip():
            messagebox.showwarning("Warning", "Please enter customer name.")
            return
        
        if len(self.customer_contact.get().strip()) != 10:
            messagebox.showwarning("Warning", "Please enter a valid 10-digit contact number.")
            return

        selected_items = []
        total_price = 0

        for medicine, info in self.orders.items():
            quantity = info["quantity"].get()
            if quantity:
                selected_items.append((medicine, int(quantity)))
                total_price += self.medicines[medicine] * int(quantity)

        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one medicine.")
            return

        gst_amount = (total_price * self.gst_percentage) / 100

        bill = f"Customer Name: {self.customer_name.get()}\n"
        bill += f"Customer Contact: {self.customer_contact.get()}\n\n"
        bill += "Selected Medicines:\n"
        for medicine, quantity in selected_items:
            bill += f"{medicine} x {quantity} - {self.convert_to_inr(self.medicines[medicine] * quantity)}\n"
        bill += f"\nTotal Price: {self.convert_to_inr(total_price)}\n"
        bill += f"GST ({self.gst_percentage}%): {self.convert_to_inr(gst_amount)}\n"
        bill += f"Grand Total: {self.convert_to_inr(total_price + gst_amount)}"

        self.save_record(bill)
        messagebox.showinfo("Bill", bill)

    def save_record(self, bill):
        records = self.load_records()
        records.append(bill)
        with open(self.records_file, 'w') as file:
            json.dump(records, file)

    def load_records(self):
        if os.path.exists(self.records_file):
            with open(self.records_file, 'r') as file:
                return json.load(file)
        return []

    def past_records(self):
        records = self.load_records()

        past_records_window = tk.Toplevel(self.root)
        past_records_window.title("Past Records")

        if records:
            records_listbox = tk.Listbox(past_records_window, selectmode=tk.SINGLE, width=80, height=15, font=("Arial", 12))
            records_listbox.pack(padx=10, pady=10)

            for record in records:
                records_listbox.insert(tk.END, record)

            delete_button = tk.Button(past_records_window, text="Delete Selected Record", command=lambda: self.delete_record(records_listbox), font=("Arial", 12, "bold"))
            delete_button.pack(pady=5)

        else:
            no_records_label = tk.Label(past_records_window, text="No past records found.", font=("Arial", 12))
            no_records_label.pack(padx=10, pady=10)

    def delete_record(self, listbox):
        try:
            selected_index = listbox.curselection()[0]
            selected_record = listbox.get(selected_index)
            
            records = self.load_records()
            records.pop(selected_index)

            with open(self.records_file, 'w') as file:
                json.dump(records, file)

            listbox.delete(selected_index)
            messagebox.showinfo("Success", "Record deleted successfully.")

        except IndexError:
            messagebox.showwarning("Warning", "No record selected.")

    def clear_selection(self):
        for medicine, info in self.orders.items():
            info["var"].set(0)
            info["quantity"].delete(0, tk.END)

        self.customer_name.set("")
        self.customer_contact.set("")
        self.sample_bill_text.delete("1.0", tk.END)

    def validate_contact(self, value):
        if value.isdigit() and len(value) <= 10:
            return True
        return False

    @staticmethod
    def convert_to_inr(amount):
        return "₹" + str(amount)

root = tk.Tk()
pharmacy_system = PharmacyManagementSystem(root)
root.mainloop()
