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
    screen7.geometry("400x400")
    Label(screen7, text="Login Successful").pack()
    Button(screen7, text="Set Preferences", command=lambda: set_preferences(user_id)).pack()
    Button(screen7, text="View Recommendations", command=lambda: view_recommendations(user_id)).pack()
    Button(screen7, text="Manage Wishlist", command=lambda: manage_wishlist(user_id)).pack()
    Button(screen7, text="Logout", command=logout).pack()

def set_preferences(user_id):
    global screen9
    screen9 = Toplevel(screen)
    screen9.title("Set Preferences")
    screen9.geometry("300x300")
    
    global laptop_budget_var, laptop_major_var, laptop_usage_var
    
    laptop_budget_var = StringVar()
    laptop_major_var = StringVar()
    laptop_usage_var = StringVar()
    
    Label(screen9, text="Budget").pack()
    laptop_budget_entry = Entry(screen9, textvariable=laptop_budget_var)
    laptop_budget_entry.pack()
    Label(screen9, text="Major").pack()
    laptop_major_entry = Entry(screen9, textvariable=laptop_major_var)
    laptop_major_entry.pack()
    Label(screen9, text="Usage").pack()
    laptop_usage_entry = Entry(screen9, textvariable=laptop_usage_var)
    laptop_usage_entry.pack()
    
    Button(screen9, text="Save Preferences", command=lambda: save_preferences(user_id)).pack()

def save_preferences(user_id):
    budget = laptop_budget_var.get()
    major = laptop_major_var.get()
    usage = laptop_usage_var.get()
    
    try:
        cursor.execute("INSERT INTO preferences (User_ID, Budget, Major, Usage) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE Budget=%s, Major=%s, Usage=%s", 
                       (user_id, budget, major, usage, budget, major, usage))
        db.commit()
        messagebox.showinfo("Success", "Preferences saved successfully")
        screen9.destroy()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

def view_recommendations(user_id):
    global screen10
    screen10 = Toplevel(screen)
    screen10.title("Laptop Recommendations")
    screen10.geometry("600x400")

    # Test case 3: System filters laptops based on customer specification 
    cursor.execute("SELECT Budget, Major, Usage FROM preferences WHERE User_ID = %s", (user_id,))
    preferences = cursor.fetchone()
    if not preferences:
        messagebox.showerror("Error", "No preferences found. Please set your preferences first.")
        screen10.destroy()
        return
    
    budget, major, usage = preferences
   # Test case 3: System lists laptops based on user preference 
    query = "SELECT * FROM laptops WHERE Laptop_Price <= %s"
    params = [budget]
    
    if usage == "Gaming":
        query += " AND RAM_GB >= 16"
    elif usage == "Data Analysis":
        query += " AND RAM_GB >= 8 AND SSD_GB >= 256"
    elif usage == "Coding":
        query += " AND RAM_GB >= 8"
    elif usage == "Web Browsing":
        query += " AND RAM_GB >= 4"

    # Test case 4: System highlights selected laptop model  
    cursor.execute(query, tuple(params))
    laptops = cursor.fetchall()

    


    for laptop in laptops:
        Label(screen10, text=f"Model: {laptop[1]}, Price: ${laptop[2]}, RAM: {laptop[3]}GB, Brand: {laptop[4]}, SSD: {laptop[5]}GB").pack()
        Button(screen10, text="Add to Wishlist", command=lambda l=laptop: add_to_wishlist(user_id, l)).pack()

# Test case 4: System adds laptop to users Wishlist 
def add_to_wishlist(user_id, laptop):
    try:
        cursor.execute("INSERT INTO wishlist (User_ID, Laptop_ID) VALUES (%s, %s)", (user_id, laptop[0]))
        db.commit()
        messagebox.showinfo("Success", f"{laptop[1]} added to wishlist.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

#Test case 4: System displays users Wishlist 

def manage_wishlist(user_id):
    global screen11
    screen11 = Toplevel(screen)
    screen11.title("Wishlist")
    screen11.geometry("600x400")
    
    cursor.execute("SELECT w.Laptop_ID, l.Laptop_Model, l.Laptop_Price, l.RAM_GB, l.Brand, l.SSD_GB FROM wishlist w JOIN laptops l ON w.Laptop_ID = l.Laptop_ID WHERE w.User_ID = %s", (user_id,))
    wishlist_items = cursor.fetchall()
    
    for item in wishlist_items:
        Label(screen11, text=f"Model: {item[1]}, Price: ${item[2]}, RAM: {item[3]}GB, Brand: {item[4]}, SSD: {item[5]}GB").pack()
        Button(screen11, text="Remove from Wishlist", command=lambda i=item: remove_from_wishlist(user_id, i[0])).pack()


#Test case 4: System displays user adjustments to Wishlist 
def remove_from_wishlist(user_id, laptop_id):
    try:
        cursor.execute("DELETE FROM wishlist WHERE User_ID = %s AND Laptop_ID = %s", (user_id, laptop_id))
        db.commit()
        messagebox.showinfo("Success", "Item removed from wishlist.")
        screen11.destroy()
        manage_wishlist(user_id)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

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
    password_entry1 = Entry(screen2, textvariable=password_verify, show='*')
    password_entry1.pack()
    Label(screen2, text="").pack()
    Button(screen2, text="Login", width=10, height=1, command=login_verify).pack()

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