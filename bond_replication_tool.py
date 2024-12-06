import customtkinter
import tkinter
import random
import re
from CTkXYFrame import *

def random_price(maturity, start_value_price, end_value_price):
    price = round(random.uniform(start_value_price,end_value_price))
    return price


def random_coupon(maturity, start_value_coupon, end_value_coupon):
    coupon = round(random.uniform(start_value_coupon,end_value_coupon),1)
    return coupon


def gen_coupon_bonds(maturity, coupon_bonds):
    for year in range(1, maturity+1):
        coupon_bonds.update({f"coupon_bond_{year}": []})

    return coupon_bonds


def gen_zero_bond(maturity):
    zero_bond = [100]
    for year in range(maturity):
        zero_bond.append(0)

    return zero_bond


def initalize_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, max_maturity, fraction_list, to_replic_cf):
    if coupon_bonds.get(f"coupon_bond_{maturity + 1}") is None:
        start_value = to_replic_cf[maturity - 1]
    else:
        value = difference(maturity, coupon_bonds, price_list, coupon_list, max_maturity)
        start_value = -value + to_replic_cf[maturity - 1]

    coupon_bonds[f"coupon_bond_{maturity}"].append(start_value)

    calc_fractions(maturity, coupon_bonds, price_list, coupon_list, fraction_list, max_maturity)

    if maturity > 1:
        initalize_coupon_bonds(maturity - 1, coupon_bonds, price_list, coupon_list, max_maturity, fraction_list, to_replic_cf)

    return coupon_bonds, fraction_list


def difference(maturity, coupon_bonds, price_list, coupon_list, max_maturity):
    if coupon_bonds.get(f"coupon_bond_{maturity + 1}") is not None:
        value = ((list(reversed(coupon_bonds[f"coupon_bond_{maturity + 1}"]))[maturity]) +
                  difference(maturity + 1, coupon_bonds, price_list, coupon_list, max_maturity))
        return value
    else:
        return 0

def calc_fractions(maturity, coupon_bonds, price_list, coupon_list, fraction_list, max_maturity):
    fraction = coupon_bonds[f"coupon_bond_{maturity}"][0] / (100 + coupon_list[maturity - 1])
    fraction_list.append(fraction)
    cashflows_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, fraction, max_maturity)


def cashflows_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, fraction, max_maturity):
    coupon = coupon_list[maturity - 1] * fraction
    price = -(price_list[maturity - 1] * fraction)

    for year in range(1, maturity):
        coupon_bonds[f"coupon_bond_{maturity}"].append(coupon)

    coupon_bonds[f"coupon_bond_{maturity}"].append(price)

    current_length = len(coupon_bonds[f"coupon_bond_{maturity}"])
    zeros_to_add = max_maturity + 1 - current_length
    for _ in range(zeros_to_add):
        coupon_bonds[f"coupon_bond_{maturity}"].insert(0, 0)


class BondReplicationApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("Bond Replication Tool")
        self.geometry("600x400")

        # Make Window scalable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Start Page Initialization
        self.current_frame = None
        self.create_start_page()

    def create_start_page(self):
        self.maturity = 0
        self.max_maturity = 0
        self.start_value_coupon = 1
        self.end_value_coupon = 10
        self.start_value_price = 85
        self.end_value_price = 115
        self.price_list = []
        self.coupon_list = []
        self.check_settings_var = tkinter.StringVar(value="off")
        self.checkbox_state = self.check_settings_var.get()
        self.fraction_list = []
        self.coupon_bonds = {}
        self.to_replic_cf = []
        self.check_rep_cf_var = tkinter.StringVar(value="off")
        self.checkbox_rep = self.check_rep_cf_var.get()
        self.saved_input_rep_value = ""

        self.clear_current_frame()

        # New Frame for Start Page
        self.current_frame = customtkinter.CTkFrame(self)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame.grid_rowconfigure(0, weight=1)
        self.current_frame.grid_columnconfigure(0, weight=1)

        self.maturity_label = customtkinter.CTkLabel(self.current_frame, text="Maturity in Years: ")
        self.maturity_label.pack(pady=5)

        self.maturity_entry = customtkinter.CTkEntry(self.current_frame)
        self.maturity_entry.pack(pady=5)

        # Wrapper Frame for Buttons
        fg_color = self.current_frame.cget("fg_color")
        self.button_wrapper_frame = customtkinter.CTkFrame(self.current_frame, fg_color=fg_color)
        self.button_wrapper_frame.pack(pady=15)

        # Button to generate random Bonds
        self.random_button = customtkinter.CTkButton(self.button_wrapper_frame, text="Generate Bonds", command=self.on_random_bonds_click)
        self.random_button.pack(side="left", padx=10)

        # Button to initialize Bonds
        self.initialize_button = customtkinter.CTkButton(self.button_wrapper_frame, text="Initialize Bond", command=self.on_init_bonds_click)
        self.initialize_button.pack(side="left", padx=10)

        # Check Box (Standard or Advanced Settings)
        self.checkbox = customtkinter.CTkCheckBox(self.current_frame, text="Advanced Settings", command=self.checkbox_event,
                                                  variable=self.check_settings_var, onvalue="on", offvalue="off")
        self.checkbox.pack(pady=5)

        # Wrapper Frame for Customization
        self.settings_wrapper_frame = customtkinter.CTkFrame(self.current_frame)
        self.settings_wrapper_frame.pack(pady=20)
        self.settings_wrapper_frame.pack_forget()

        # Slider for Advanced Settings (Price)
        self.price_settings_frame = customtkinter.CTkFrame(self.settings_wrapper_frame)
        self.price_settings_frame.pack(side="left")

        self.price_start_label = customtkinter.CTkLabel(self.price_settings_frame, text="Lower Bound for Price: ")
        self.price_start_label.pack(pady=5, padx=5)

        self.price_start_slider = customtkinter.CTkSlider(self.price_settings_frame, from_=1, to=100, command=self.price_start_slider_event, number_of_steps=99)
        self.price_start_slider.pack(pady=5, padx=5)

        self.price_start_slider_label = customtkinter.CTkLabel(self.price_settings_frame, text="Current Value: 50")
        self.price_start_slider_label.pack()
        self.start_value_price = 50

        self.price_end_label = customtkinter.CTkLabel(self.price_settings_frame, text="Upper Bound for Price: ")
        self.price_end_label.pack(pady=5, padx=5)

        self.price_end_slider = customtkinter.CTkSlider(self.price_settings_frame, from_=1, to=200, command=self.price_end_slider_event, number_of_steps=199)
        self.price_end_slider.pack(pady=5, padx=5)

        self.price_end_slider_label = customtkinter.CTkLabel(self.price_settings_frame, text="Current Value: 100")
        self.price_end_slider_label.pack()
        self.end_value_price = 100

        # Slider for Advanced Settings (Coupon)
        self.coupon_settings_frame = customtkinter.CTkFrame(self.settings_wrapper_frame)
        self.coupon_settings_frame.pack(side="left")

        self.coupon_start_label = customtkinter.CTkLabel(self.coupon_settings_frame, text="Lower Bound for Coupon: ")
        self.coupon_start_label.pack(pady=5, padx=5)

        self.coupon_start_slider = customtkinter.CTkSlider(self.coupon_settings_frame, from_=0, to=10, command=self.coupon_start_slider_event, number_of_steps=100)
        self.coupon_start_slider.pack(pady=5, padx=5)

        self.coupon_start_slider_label = customtkinter.CTkLabel(self.coupon_settings_frame, text="Current Value: 5")
        self.coupon_start_slider_label.pack()
        self.start_value_coupon = 5

        self.coupon_end_label = customtkinter.CTkLabel(self.coupon_settings_frame, text="Upper Bound for Coupon: ")
        self.coupon_end_label.pack(pady=5, padx=5)

        self.coupon_end_slider = customtkinter.CTkSlider(self.coupon_settings_frame, from_=0, to=20, command=self.coupon_end_slider_event, number_of_steps=200)
        self.coupon_end_slider.pack(pady=5, padx=5)

        self.coupon_end_slider_label = customtkinter.CTkLabel(self.coupon_settings_frame, text="Current Value: 10")
        self.coupon_end_slider_label.pack()
        self.end_value_coupon = 10

    def checkbox_event(self):
        self.checkbox_state = self.check_settings_var.get()

        if self.checkbox_state == "on":
            # Show advanced settings
            self.settings_wrapper_frame.pack()
        else:
            # Hide
            self.settings_wrapper_frame.pack_forget()

    def price_start_slider_event(self, value):
        self.start_value_price = round(float(value))
        self.price_start_slider_label.configure(text=f"Current Value: {self.start_value_price}")

    def price_end_slider_event(self, value):
        self.end_value_price = round(float(value))
        self.price_end_slider_label.configure(text=f"Current Value: {self.end_value_price}")

    def coupon_start_slider_event(self, value):
        self.start_value_coupon = round(float(value),1)
        self.coupon_start_slider_label.configure(text=f"Current Value: {self.start_value_coupon}")

    def coupon_end_slider_event(self, value):
        self.end_value_coupon = round(float(value),1)
        self.coupon_end_slider_label.configure(text=f"Current Value: {self.end_value_coupon}")

    def on_random_bonds_click(self):
        try:
            self.maturity = int(self.maturity_entry.get())
            self.max_maturity = int(self.maturity_entry.get())
            replic_cf = [0 for i in range(self.max_maturity - 1)]
            replic_cf.append(100)
            self.to_replic_cf.extend(replic_cf)

            if self.max_maturity < 1:
                if hasattr(self, 'error_label'):
                    self.error_label.destroy()
                self.error_label = customtkinter.CTkLabel(self.current_frame, text="Maturity too short")
                self.error_label.pack(pady=10)
            else:
                self.show_table()

        except ValueError:
            # Error Handling
            if hasattr(self, 'error_label'):
                self.error_label.destroy() # Destroy existing Error Label
            self.error_label = customtkinter.CTkLabel(self.current_frame, text="Please enter valid numbers")
            self.error_label.pack(pady=10)

    def on_init_bonds_click(self):
        try:
            self.maturity = int(self.maturity_entry.get())
            self.max_maturity = int(self.maturity_entry.get())
            replic_cf = [0 for i in range(self.max_maturity - 1)]
            replic_cf.append(100)
            self.to_replic_cf.extend(replic_cf)

            if self.max_maturity < 1:
                if hasattr(self, 'error_label'):
                    self.error_label.destroy()
                self.error_label = customtkinter.CTkLabel(self.current_frame, text="Maturity too short")
                self.error_label.pack(pady=10)
            else:
                self.show_init_bonds()

        except ValueError:
            # Error Handling
            if hasattr(self, 'error_label'):
                self.error_label.destroy() # Destroy existing Error Label
            self.error_label = customtkinter.CTkLabel(self.current_frame, text="Please enter valid numbers")
            self.error_label.pack(pady=10)


    def show_init_bonds(self):
        self.clear_current_frame()

        self.current_frame = customtkinter.CTkFrame(self)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame.grid_rowconfigure(0, weight=1)
        self.current_frame.grid_columnconfigure(0, weight=1)

        self.prices_init_label = customtkinter.CTkLabel(self.current_frame, text="Prices (Comma Separated): ")
        self.prices_init_label.pack(pady=5)

        self.prices_init_entry = customtkinter.CTkEntry(self.current_frame)
        self.prices_init_entry.pack(pady=5)

        self.coupons_init_label = customtkinter.CTkLabel(self.current_frame, text="Coupon Rates (Comma Separated): ")
        self.coupons_init_label.pack(pady=5)

        self.coupons_init_entry = customtkinter.CTkEntry(self.current_frame)
        self.coupons_init_entry.pack(pady=5)

        # Wrapper Frame for Buttons
        fg_color = self.current_frame.cget("fg_color")
        self.button_init_wrapper_frame = customtkinter.CTkFrame(self.current_frame, fg_color=fg_color)
        self.button_init_wrapper_frame.pack(pady=15)

        # Back Button
        self.back_button = customtkinter.CTkButton(self.button_init_wrapper_frame, text="Back", command=self.create_start_page)
        self.back_button.pack(side="left", padx=10)

        # Button to create specified Bonds
        self.create_button = customtkinter.CTkButton(self.button_init_wrapper_frame, text="Create Bonds", command=self.on_show_init_bonds_click)
        self.create_button.pack(side="left", padx=10)

    def show_table(self):
        self.clear_current_frame()

        self.current_frame = customtkinter.CTkScrollableFrame(self)
        self.current_frame.pack(pady=20, fill="both", expand=True)

        # Set column weights
        for i in range(3):
            self.current_frame.grid_columnconfigure(i, weight=1)

        header = ["Maturity", "Price", "Coupon"]
        for i, col in enumerate(header):
            header_label = customtkinter.CTkLabel(self.current_frame, text=col, anchor="center")
            header_label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        for year in range(1, self.maturity + 1):
            price = random_price(self.maturity, self.start_value_price, self.end_value_price)
            coupon = random_coupon(self.maturity, self.start_value_coupon, self.end_value_coupon)
            self.price_list.append(price)
            self.coupon_list.append(coupon)

            year_label = customtkinter.CTkLabel(self.current_frame, text=str(year), anchor="center")
            year_label.grid(row=year, column=0, padx=5, pady=5, sticky="ew")

            price_label = customtkinter.CTkLabel(self.current_frame, text=f"{price:.2f}", anchor="center")
            price_label.grid(row=year, column=1, padx=5, pady=5, sticky="ew")

            coupon_label = customtkinter.CTkLabel(self.current_frame, text=f"{coupon:.2f}", anchor="center")
            coupon_label.grid(row=year, column=2, padx=5, pady=5, sticky="ew")

        # Define Cashflow to replicate
        # Check Box (Standard or Specific Cashflow)
        self.checkbox = customtkinter.CTkCheckBox(self.current_frame, text="Replicate not a Zero Bond", command=self.checkbox_rep_cf_event,
                                                  variable=self.check_rep_cf_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=self.maturity + 1, column=1, columnspan=1, pady=10, sticky="ew")

        # Wrapper Frame for Cashflow Specification
        self.rep_cf_wrapper_frame = customtkinter.CTkFrame(self.current_frame)
        self.rep_cf_wrapper_frame.grid(row=self.maturity + 2, column=1, columnspan=1, pady=10, sticky="ew")
        self.rep_cf_wrapper_frame.grid_columnconfigure((0,2), weight=1)
        self.rep_cf_wrapper_frame.grid_columnconfigure(1, weight=2)
        if self.checkbox_rep == "off":
            self.rep_cf_wrapper_frame.grid_forget()

        # Display Label
        self.rep_cf_label = customtkinter.CTkLabel(self.rep_cf_wrapper_frame, text="Cashflow Sequence (Comma Separated): ")
        self.rep_cf_label.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Input of Cashflow
        self.rep_cf_entry = customtkinter.CTkEntry(self.rep_cf_wrapper_frame)
        self.rep_cf_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")


        # Buttons
        self.back_button = customtkinter.CTkButton(self.current_frame, text="Back", command=self.create_start_page)
        self.back_button.grid(row=self.maturity + 3, column=1, columnspan=1, pady=10, sticky="ew")

        self.result_button = customtkinter.CTkButton(self.current_frame, text="Result", command=self.on_result_button_click)
        self.result_button.grid(row=self.maturity + 4, column=1, columnspan=1, pady=10, sticky="ew")

    def checkbox_rep_cf_event(self):
        self.checkbox_rep = self.check_rep_cf_var.get()

        if self.checkbox_rep == "on":
            # Show Cashflow Specification
            self.rep_cf_wrapper_frame.grid(row=self.maturity + 2, column=1, columnspan=1, pady=10, sticky="ew")
        else:
            # Hide
            self.rep_cf_wrapper_frame.grid_forget()

    def on_show_init_bonds_click(self):
        try:
            price_list_string = self.prices_init_entry.get()
            price_list_string = price_list_string.replace(" ", "")
            price_list_split = re.split(";|,", price_list_string)
            self.price_list = [float(value) for value in price_list_split]

            coupon_list_string = self.coupons_init_entry.get()
            coupon_list_string = coupon_list_string.replace(" ", "")
            coupon_list_split = re.split(";|,", coupon_list_string)
            self.coupon_list = [float(value) for value in coupon_list_split]

            if (len(self.price_list) != self.max_maturity) or (len(self.coupon_list) != self.max_maturity):
                if hasattr(self, 'error_label'):
                    self.error_label.destroy()
                self.error_label = customtkinter.CTkLabel(self.current_frame, text="Maturity doesn't match")
                self.error_label.pack(pady=10)

            else:
                self.show_table_init_bonds()
        except ValueError:
            # Error Handling
            if hasattr(self, 'error_label'):
                self.error_label.destroy() # Destroy existing Error Label
            self.error_label = customtkinter.CTkLabel(self.current_frame, text="Please enter valid numbers")
            self.error_label.pack(pady=10)


    def on_result_button_click(self):
        if self.checkbox_rep == "on":
            try:
                rep_cf_string = self.rep_cf_entry.get()
                # Store input value
                self.saved_input_rep_value = rep_cf_string
                rep_cf_string = rep_cf_string.replace(" ", "")
                rep_cf_split = re.split(";|,", rep_cf_string)
                self.to_replic_cf = [float(value) for value in rep_cf_split]

                if len(self.to_replic_cf) != self.max_maturity:
                    if hasattr(self, 'error_label'):
                        self.error_label.destroy()
                    self.error_label = customtkinter.CTkLabel(self.current_frame, text="Maturity doesn't match")
                    self.error_label.grid(row=self.maturity + 5, column=1, columnspan=1, pady=10, sticky="ew")
                else:
                    self.show_result_table()
            except:
                # Error Handling
                if hasattr(self, 'error_label'):
                    self.error_label.destroy() # Destroy existing Error Label
                self.error_label = customtkinter.CTkLabel(self.current_frame, text="Please enter valid numbers")
                self.error_label.grid(row=self.maturity + 5, column=1, columnspan=1, pady=10, sticky="ew")
        else:
            self.show_result_table()

    def show_table_init_bonds(self):
        self.clear_current_frame()

        # New Frame for Table
        self.current_frame = customtkinter.CTkScrollableFrame(self)
        self.current_frame.pack(pady=20, fill="both", expand=True)

        # Set column weights
        for i in range(3):
            self.current_frame.grid_columnconfigure(i, weight=1)

        header = ["Maturity", "Price", "Coupon"]
        for i, col in enumerate(header):
            header_label = customtkinter.CTkLabel(self.current_frame, text=col, anchor="center")
            header_label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        for year in range(1, self.maturity + 1):
            price = self.price_list[year-1]
            coupon = self.coupon_list[year-1]

            year_label = customtkinter.CTkLabel(self.current_frame, text=str(year), anchor="center")
            year_label.grid(row=year, column=0, padx=5, pady=5, sticky="ew")

            price_label = customtkinter.CTkLabel(self.current_frame, text=f"{price:.2f}", anchor="center")
            price_label.grid(row=year, column=1, padx=5, pady=5, sticky="ew")

            coupon_label = customtkinter.CTkLabel(self.current_frame, text=f"{coupon:.2f}", anchor="center")
            coupon_label.grid(row=year, column=2, padx=5, pady=5, sticky="ew")

        # Define Cashflow to replicate
        # Check Box (Standard or Specific Cashflow)
        self.checkbox = customtkinter.CTkCheckBox(self.current_frame, text="Replicate not a Zero Bond", command=self.checkbox_rep_cf_event,
                                                  variable=self.check_rep_cf_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=self.maturity + 1, column=1, columnspan=1, pady=10, sticky="ew")

        # Wrapper Frame for Cashflow Specification
        self.rep_cf_wrapper_frame = customtkinter.CTkFrame(self.current_frame)
        self.rep_cf_wrapper_frame.grid(row=self.maturity + 2, column=1, columnspan=1, pady=10, sticky="ew")
        self.rep_cf_wrapper_frame.grid_columnconfigure((0,2), weight=1)
        self.rep_cf_wrapper_frame.grid_columnconfigure(1, weight=2)
        if self.checkbox_rep == "off":
            self.rep_cf_wrapper_frame.grid_forget()

        # Display Label
        self.rep_cf_label = customtkinter.CTkLabel(self.rep_cf_wrapper_frame, text="Cashflow Sequence (Comma Separated): ")
        self.rep_cf_label.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Input of Cashflow
        self.rep_cf_entry = customtkinter.CTkEntry(self.rep_cf_wrapper_frame)
        self.rep_cf_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Restore previously saved input value
        self.rep_cf_entry.insert(0, self.saved_input_rep_value)

        # Buttons
        self.back_button = customtkinter.CTkButton(self.current_frame, text="Back", command=self.create_start_page)
        self.back_button.grid(row=self.maturity + 3, column=1, columnspan=1, pady=10, sticky="ew")

        self.result_button = customtkinter.CTkButton(self.current_frame, text="Result", command=self.on_result_button_click)
        self.result_button.grid(row=self.maturity + 4, column=1, columnspan=1, pady=10, sticky="ew")

    def show_result_table(self):
        self.clear_current_frame()  # Remove old Widgets

        # New Frame for Table
        self.current_frame = CTkXYFrame(self)
        self.current_frame.pack(pady=20, fill="both", expand=True)

        # Dynamic Header based on maturity
        header = ["Maturity", "Fraction"]
        for year in range(self.maturity + 1):
            header.append(f"Cashflow t={year}")

        # Configure columns
        num_columns = len(header)
        for i in range(num_columns):
            self.current_frame.grid_columnconfigure(i, weight=1)

        # Create Header Labels
        for i, col in enumerate(header):
            header_label = customtkinter.CTkLabel(self.current_frame, text=col, anchor="center")
            header_label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        # Initialize Data
        self.coupon_bonds = gen_coupon_bonds(self.maturity, self.coupon_bonds)
        coupon_bonds, fraction_list = initalize_coupon_bonds(self.maturity, self.coupon_bonds, self.price_list,
                                                             self.coupon_list, self.max_maturity, self.fraction_list,
                                                             self.to_replic_cf)

        npv_list = [sum(values) for values in zip(*coupon_bonds.values())]

        # Fill Table
        for year in reversed(range(1, self.maturity + 1)):
            fraction = list(reversed(fraction_list))[year - 1]

            year_label = customtkinter.CTkLabel(self.current_frame, text=str(year), anchor="center")
            year_label.grid(row=self.maturity - year + 1, column=0, padx=5, pady=5, sticky="ew")

            fraction_label = customtkinter.CTkLabel(self.current_frame, text=f"{fraction:.4f}", anchor="center")
            fraction_label.grid(row=self.maturity - year + 1, column=1, padx=5, pady=5, sticky="ew")

            for col_index in range(self.maturity + 1):
                cashflow = list(reversed(coupon_bonds[f"coupon_bond_{year}"]))[col_index]

                cashflow_label = customtkinter.CTkLabel(self.current_frame, text=f"{cashflow:.2f}", anchor="center")
                cashflow_label.grid(row=self.maturity - year + 1, column=2 + col_index, padx=5, pady=5, sticky="ew")

        # Create Net Present Value (Difference) row
        for col_index in range(2, self.maturity + 3):
            npv = list(reversed(npv_list))[col_index - 2]
            npv_label = customtkinter.CTkLabel(self.current_frame, text=f"{npv:.2f}", anchor="center")
            npv_label.grid(row=self.maturity + 1, column=col_index, padx=5, pady=5, sticky="ew")

        npv_name_label = customtkinter.CTkLabel(self.current_frame, text="Diff.", anchor="center")
        npv_name_label.grid(row=self.maturity + 1, column=0, padx=5, pady=5, sticky="ew")

        # Back-Button
        self.back_button = customtkinter.CTkButton(self.current_frame, text="Back", command=self.show_table_init_bonds)
        self.back_button.grid(row=self.maturity + 2, column=0, columnspan=num_columns, pady=10, sticky="ew")

        # Home-Button
        self.home_button = customtkinter.CTkButton(self.current_frame, text="Home", command=self.create_start_page)
        self.home_button.grid(row=self.maturity + 3, column=0, columnspan=num_columns, pady=10, sticky="ew")

    def clear_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()


if __name__ == "__main__":
    app = BondReplicationApp()
    app.mainloop()