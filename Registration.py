from tkinter import *
from tkinter import messagebox
import mysql.connector
from datetime import datetime

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword",
    database="LaptopDataSystem"
)

cursor = db.cursor()

def register_user():
    first_name = first_name_var.get()
    last_name = last_name_var.get()
    user_budget = user_budget_var.get()
    user_major = user_major_var.get()
    username_info = username_var.get()
    password_info = password_var.get()
    
    try:
        cursor.execute("INSERT INTO users (First_Name, Last_Name, User_Budget, User_Major, Username, Password) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (first_name, last_name, user_budget, user_major, username_info, password_info))
        db.commit()
        clear_registration_form()
        messagebox.showinfo("Success", "Registration Successful")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

def login_verify():
    username1 = username_verify.get()
    password1 = password_verify.get()
    clear_login_form()
    
    cursor.execute("SELECT * FROM users WHERE Username = %s AND Password = %s", (username1, password1))
    result = cursor.fetchone()
    
    if result:
        user_id = result[0]
        now = datetime.now()
        cursor.execute("INSERT INTO logins (User_ID, Access_Time) VALUES (%s, %s)", (user_id, now))
        db.commit()
        login_success(user_id)
    else:
        messagebox.showerror("Error", "Incorrect Username or Password")

def login_success(user_id):
    global screen7
    screen7 = Toplevel(screen)
    screen7.title("Dashboard")
    screen7.geometry("300x250")
    Label(screen7, text="Login Successful").pack()
    Button(screen7, text="Input Previous Purchase", command=lambda: input_purchase(user_id)).pack()
    Button(screen7, text="Logout", command=logout).pack()

def input_purchase(user_id):
    global screen8
    screen8 = Toplevel(screen)
    screen8.title("Input Purchase")
    screen8.geometry("300x250")
    
    global laptop_model_var
    global purchase_date_var
    
    laptop_model_var = StringVar()
    purchase_date_var = StringVar()
    
    Label(screen8, text="Laptop Model").pack()
    laptop_model_entry = Entry(screen8, textvariable=laptop_model_var)
    laptop_model_entry.pack()
    Label(screen8, text="Purchase Date (YYYY-MM-DD)").pack()
    purchase_date_entry = Entry(screen8, textvariable=purchase_date_var)
    purchase_date_entry.pack()
    
    Button(screen8, text="Submit", command=lambda: save_purchase(user_id)).pack()

def save_purchase(user_id):
    model = laptop_model_var.get()
    date = purchase_date_var.get()
    
    try:
        cursor.execute("INSERT INTO purchases (User_ID, Laptop_Model, Purchase_Date) VALUES (%s, %s, %s)", (user_id, model, date))
        db.commit()
        messagebox.showinfo("Success", "Purchase recorded successfully")
        screen8.destroy()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

def register():
    global screen1
    screen1 = Toplevel(screen)
    screen1.title("Register")
    screen1.geometry("300x350")
    
    global first_name_var, last_name_var, user_budget_var, user_major_var, username_var, password_var
    first_name_var = StringVar()
    last_name_var = StringVar()
    user_budget_var = StringVar()
    user_major_var = StringVar()
    username_var = StringVar()
    password_var = StringVar()

    Label(screen1, text="Please enter details below").pack()
    Label(screen1, text="").pack()
    Label(screen1, text="First Name * ").pack()
    Entry(screen1, textvariable=first_name_var).pack()
    Label(screen1, text="Last Name * ").pack()
    Entry(screen1, textvariable=last_name_var).pack()
    Label(screen1, text="User Budget * ").pack()
    Entry(screen1, textvariable=user_budget_var).pack()
    Label(screen1, text="User Major * ").pack()
    Entry(screen1, textvariable=user_major_var).pack()
    Label(screen1, text="Username * ").pack()
    Entry(screen1, textvariable=username_var).pack()
    Label(screen1, text="Password * ").pack()
    Entry(screen1, textvariable=password_var).pack()
    Label(screen1, text="").pack()
    Button(screen1, text="Register", width=10, height=1, command=register_user).pack()

def login():
    global screen2
    screen2 = Toplevel(screen)
    screen2.title("Login")
    screen2.geometry("300x250")
    Label(screen2, text="Please enter details below to login").pack()
    Label(screen2, text="").pack()

    global username_verify, password_verify
    username_verify = StringVar()
    password_verify = StringVar()

    global username_entry1, password_entry1
    Label(screen2, text="Username * ").pack()
    username_entry1 = Entry(screen2, textvariable=username_verify)
    username_entry1.pack()
    Label(screen2, text="").pack()
    Label(screen2, text="Password * ").pack()
    password_entry1 = Entry(screen2, textvariable=password_verify)
    password_entry1.pack()
    Label(screen2, text="").pack()
    Button(screen2, text="Login", width=10, height=1, command=login_verify).pack()

def clear_registration_form():
    first_name_var.set("")
    last_name_var.set("")
    user_budget_var.set("")
    user_major_var.set("")
    username_var.set("")
    password_var.set("")

def clear_login_form():
    username_verify.set("")
    password_verify.set("")

def logout():
    screen7.destroy()

def main_screen():
    global screen
    screen = Tk()
    screen.geometry("300x250")
    screen.title("Laptop Data System")
    Label(text="Laptop Data System", bg="#f8b86f", width="300", height="2", font=("Calibri", 13)).pack()
    Label(text="").pack()
    Button(text="Login", height="2", width="30", command=login).pack()
    Label(text="").pack()
    Button(text="Register", height="2", width="30", command=register).pack()

    screen.mainloop()

main_screen()