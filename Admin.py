from tkinter import *
from tkinter import messagebox
import mysql.connector

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword",
    database="LaptopDataSystem"
)

cursor = db.cursor()

# Test case 5: System updates count and records new laptop models,specification and laptop price 


def add_update_laptop():
    brand = brand_var.get()
    model = model_var.get()
    processor_brand = processor_brand_var.get()
    processor_name = processor_name_var.get()
    ram_gb = ram_gb_var.get()
    ssd = ssd_var.get()
    hdd = hdd_var.get()
    os = os_var.get()
    weight = weight_var.get()
    display_size = display_size_var.get()
    touchscreen = touchscreen_var.get()
    latest_price = latest_price_var.get()

    try:
        cursor.execute("""
            INSERT INTO laptops (brand, model, processor_brand, processor_name, ram_gb, ssd, hdd, os, weight, display_size, touchscreen, latest_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                processor_brand=%s, processor_name=%s, ram_gb=%s, ssd=%s, hdd=%s, os=%s, weight=%s, display_size=%s, touchscreen=%s, latest_price=%s
        """, (brand, model, processor_brand, processor_name, ram_gb, ssd, hdd, os, weight, display_size, touchscreen, latest_price,
              processor_brand, processor_name, ram_gb, ssd, hdd, os, weight, display_size, touchscreen, latest_price))
        db.commit()
        messagebox.showinfo("Success", "Laptop details added/updated successfully")
        clear_form()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

def clear_form():
    brand_var.set("")
    model_var.set("")
    processor_brand_var.set("")
    processor_name_var.set("")
    ram_gb_var.set("")
    ssd_var.set("")
    hdd_var.set("")
    os_var.set("")
    weight_var.set("")
    display_size_var.set("")
    touchscreen_var.set("")
    latest_price_var.set("")

def admin_interface():
    global screen_admin
    screen_admin = Tk()
    screen_admin.title("Admin Interface")
    screen_admin.geometry("400x600")

    global brand_var, model_var, processor_brand_var, processor_name_var, ram_gb_var, ssd_var, hdd_var, os_var, weight_var, display_size_var, touchscreen_var, latest_price_var
    brand_var = StringVar()
    model_var = StringVar()
    processor_brand_var = StringVar()
    processor_name_var = StringVar()
    ram_gb_var = StringVar()
    ssd_var = StringVar()
    hdd_var = StringVar()
    os_var = StringVar()
    weight_var = StringVar()
    display_size_var = StringVar()
    touchscreen_var = StringVar()
    latest_price_var = StringVar()

    Label(screen_admin, text="Brand").pack()
    Entry(screen_admin, textvariable=brand_var).pack()
    Label(screen_admin, text="Model").pack()
    Entry(screen_admin, textvariable=model_var).pack()
    Label(screen_admin, text="Processor Brand").pack()
    Entry(screen_admin, textvariable=processor_brand_var).pack()
    Label(screen_admin, text="Processor Name").pack()
    Entry(screen_admin, textvariable=processor_name_var).pack()
    Label(screen_admin, text="RAM (GB)").pack()
    Entry(screen_admin, textvariable=ram_gb_var).pack()
    Label(screen_admin, text="SSD (GB)").pack()
    Entry(screen_admin, textvariable=ssd_var).pack()
    Label(screen_admin, text="HDD (GB)").pack()
    Entry(screen_admin, textvariable=hdd_var).pack()
    Label(screen_admin, text="Operating System").pack()
    Entry(screen_admin, textvariable=os_var).pack()
    Label(screen_admin, text="Weight (kg)").pack()
    Entry(screen_admin, textvariable=weight_var).pack()
    Label(screen_admin, text="Display Size (inches)").pack()
    Entry(screen_admin, textvariable=display_size_var).pack()
    Label(screen_admin, text="Touchscreen (Yes/No)").pack()
    Entry(screen_admin, textvariable=touchscreen_var).pack()
    Label(screen_admin, text="Latest Price").pack()
    Entry(screen_admin, textvariable=latest_price_var).pack()

    Button(screen_admin, text="Add/Update Laptop", command=add_update_laptop).pack()

    screen_admin.mainloop()

admin_interface()