import customtkinter as ctk
from PIL import Image as PILImage
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import pymysql
import random
from test2 import *
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from twilio.rest import Client
import hashlib
from activity_logger import log_activity

class Admin(ctk.CTkToplevel):
    def __init__(self, master=None, admin_info=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.admin_info = admin_info or {}
        self.user_details_window = None
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ---------------- Window Setup ----------------
        self.title("Admin Panel")
        self.geometry("1530x785+0+0")
        self.resizable(False, False)
        
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.focus_force()
        
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False) if self.winfo_exists() else None)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")



        # ---------------- Background ---------------
        try:
            # Use PILImage instead of Image
            img_data = PILImage.open(r"Image\Admin.jpg") 
            self.bg_image = ctk.CTkImage(
                light_image=img_data,
                size=(1530, 785)
            )
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background image: {e}", parent=self)

        # ---------------- Glass Main Frame ----------------
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=32,
            fg_color="#1e1e1e",
            bg_color="transparent",
            border_width=1,
            border_color="white"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)

        # ---------------- Top Bar ----------------
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=30, pady=(20, 10))

        self.date_lbl = ctk.CTkLabel(self.top_bar, font=("Segoe UI", 14), text_color="white")
        self.date_lbl.pack(side="left")

        self.time_lbl = ctk.CTkLabel(self.top_bar, font=("Segoe UI", 14), text_color="white")
        self.time_lbl.pack(side="right")

        self.update_time()

        # ---------------- Body Frame ----------------
        self.body_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ---------------- Sidebar ----------------
        self.sidebar = ctk.CTkFrame(self.body_frame, width=200, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))

        ctk.CTkLabel(self.sidebar, text="👤 MENU", font=("Roboto", 20, "bold")).pack(pady=30)

        ctk.CTkButton(self.sidebar, text="Admin", command=self.show_home, width=160).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Pin Change", command=self.show_pin_change, width=160).pack(pady=10)

        # ---------------- Home Content Frame ----------------
        self.content_frame = ctk.CTkFrame(self.body_frame, corner_radius=15)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        self.b1 = ctk.CTkButton(self.content_frame, text="USER DETAIL", command=self.show_user_details, width=190, height=190, corner_radius=20, font=("Segoe UI", 22, "bold"))
        self.b1.place(x=50, y=100)

        self.b2 = ctk.CTkButton(self.content_frame, text="PHOTOS", command=self.show_user_photos, width=190, height=190, corner_radius=20, font=("Segoe UI", 22, "bold"))
        self.b2.place(x=360, y=100)
        
        self.b3 = ctk.CTkButton(self.content_frame, text="RECORDS", command=self.show_user_records, width=190, height=190, corner_radius=20, font=("Segoe UI", 22, "bold"))
        self.b3.place(x=660, y=100) 

        # ---------------- Pin Change Frame (Initially Hidden) ----------------
        self.pin_frame = ctk.CTkFrame(self.body_frame, corner_radius=15)
        
        ctk.CTkLabel(self.pin_frame, text="Pin Change Admin", font=("Roboto", 22, "bold")).pack(pady=40)
        
        
        ctk.CTkLabel(self.pin_frame, text="Admin ID", font=("Roboto", 16)).place(x=200, y=140)
        self.pin_Admin_id = ctk.CTkEntry(self.pin_frame, width=300)
        self.pin_Admin_id.place(x=200, y=180)
        
        ctk.CTkLabel(self.pin_frame, text="New PIN (4 digits)", font=("Roboto", 16)).place(x=200, y=230)
        self.new_pin_entry = ctk.CTkEntry(self.pin_frame, width=300)
        self.new_pin_entry.place(x=200, y=260)
        
        
        ctk.CTkLabel(self.pin_frame, text="OTP", font=("Roboto", 16)).place(x=200, y=310)
        self.otp_entry = ctk.CTkEntry(self.pin_frame, width=150)
        self.otp_entry.place(x=200, y=340)

        self.generated_otp = None
        self.otp_btn = ctk.CTkButton(self.pin_frame, text="Send OTP",command=self.handle_send_otp,width=100, height=30)
        self.otp_btn.place(x=400, y=340) 
        
        ctk.CTkButton(self.pin_frame, text="Verify & Submit", command=self.verify_otp_and_proceed,width=300, height=30).place(x=200, y=400) 
        

    # -----------------------------------------------------------------Functions ------------------------------------------------------------------------------------------
    
    
    #-----------------------------------   Send OTP Functionality (To be implemented) --------------------------------------
    def handle_send_otp(self):
        Admin_id = self.pin_Admin_id.get().strip()
        if not Admin_id:
            messagebox.showerror("Error", "Please enter Admin ID first", parent=self)
            return

        self.generated_otp = str(random.randint(100000, 999999))
        
        # Twilio Config 
        account_sid = "AC28018e898a11c75e02c46464f2545811"
        auth_token = "8266a2a2ff4cb21971abe4ecd902a96c"
        client = Client(account_sid, auth_token)

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Fetch BOTH contact number and Email from the admins table
            cursor.execute("SELECT contact_no, Email FROM admins WHERE admin_id=%s", (Admin_id,))
            result = cursor.fetchone()
            
            if result:
                contact_no = "+91" + str(result[0]) 
                admin_email = result[1]
                
                try:
                    client.messages.create(
                        body=f"Your Admin OTP for PIN change is: {self.generated_otp}",
                        from_="+18623862829",
                        to=contact_no
                    )
                    messagebox.showinfo("Success", f"OTP sent via SMS to registered number ending in {contact_no[-4:]}", parent=self)
                    self.otp_btn.configure(state="disabled") 
                    
                except Exception as twilio_err:
                    print(f"Twilio SMS Failed: {twilio_err}")
                    
                    if admin_email:
                        try:
                            sender = "kajuteam1124@gmail.com"
                            password = "esogwngbjfgigyeo" 
                            
                            email_msg = EmailMessage()
                            email_msg["Subject"] = "Admin Security Alert: PIN Change OTP"
                            email_msg["From"] = sender
                            email_msg["To"] = admin_email
                            email_msg.set_content(f"Dear Admin,\n\nYour OTP for changing your PIN is: {self.generated_otp}\n\nPlease do not share this code with anyone.")
                            
                            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                server.starttls()
                                server.login(sender, password)
                                server.send_message(email_msg)
                                
                            messagebox.showinfo("Success", f"SMS unavailable. OTP sent via Email to {admin_email}", parent=self)
                            self.otp_btn.configure(state="disabled")
                            
                        except Exception as email_err:
                            messagebox.showerror("Error", f"Failed to send OTP via SMS and Email.\nEmail Error: {email_err}", parent=self)
                    else:
                        messagebox.showerror("Error", "SMS failed and no registered Email was found for this Admin.", parent=self)
            else:
                messagebox.showerror("Error", "Admin ID not found in database.", parent=self)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve admin data: {e}", parent=self)
        finally:
            if 'conn' in locals(): conn.close()

    def verify_otp_and_proceed(self):
        entered_otp = self.otp_entry.get().strip()
        
        if not self.generated_otp:
            messagebox.showerror("Error", "Please send OTP first.", parent=self)
            return

        if entered_otp == self.generated_otp:
            messagebox.showinfo("Verified", "OTP Correct! You can now set your new PIN.", parent=self)
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                New_pin_for_database = self.hash_pin(self.new_pin_entry.get().strip())
                cursor.execute("UPDATE admins SET Pin_hash=%s WHERE admin_id=%s", (New_pin_for_database, self.pin_Admin_id.get().strip()))
                conn.commit()
                messagebox.showinfo("Success", "Admin PIN updated successfully!", parent=self)
                self.new_pin_entry.delete(0, "end")
                self.otp_entry.delete(0, "end")
                self.otp_btn.configure(state="normal")
                
                self.clear_fields()
                self.show_home()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update PIN: {e}", parent=self)
            finally:
                if 'conn' in locals(): conn.close()

        else:
            messagebox.showerror("Error", "Invalid OTP. Please try again.", parent=self)        
        
     
     #-----------------------------------   Functions for User Details, Photos, Records handling -------------------------------------------------
     
    def show_user_details(self):
        if self.user_details_window and self.user_details_window.winfo_exists():
            self.user_details_window.focus()
            self.user_details_window.attributes("-topmost", True)
        else:
            self.user_details_window = User_details(master =self)
            self.user_details_window.attributes("-topmost", True)
            self.user_details_window.focus()
    
    def show_user_photos(self):
        # 1. Create a selection popup
        choice_win = ctk.CTkToplevel(self)
        choice_win.title("Select Repository")
        choice_win.geometry("450x200+540+300")
        choice_win.attributes("-topmost", True)
        choice_win.grab_set() # User must select an option

        ctk.CTkLabel(choice_win, text="Whose photos would you like to view?", font=("Segoe UI", 16, "bold")).pack(pady=20)

        btn_frame = ctk.CTkFrame(choice_win, fg_color="transparent")
        btn_frame.pack()

        # User Button
        ctk.CTkButton(btn_frame, text="👥 USER PHOTOS", width=160, height=40,
                      command=lambda: [choice_win.destroy(), self.open_viewer("user")]).grid(row=0, column=0, padx=10)
        
        # Admin Button
        ctk.CTkButton(btn_frame, text="🛡️ ADMIN PHOTOS", width=160, height=40, fg_color="#d32f2f", hover_color="#b71c1c",
                      command=lambda: [choice_win.destroy(), self.open_viewer("admin")]).grid(row=0, column=1, padx=10)

    def open_viewer(self, target):
        if target == "user":
            path = r"D:\Data Scientist\Project\Final Project\Active_Users"
            title = "Active User Directory"
        else:
            path = r"D:\Data Scientist\Project\Final Project\Admin_Samples"
            title = "Admin Photo Directory"
            
        self.active_viewer = PhotoViewer(self, path, title, target)
    
    def show_user_records(self):
        records_window = ctk.CTkToplevel(self)
        records_window.title("System Activity Logs")
        records_window.geometry("1200x650+150+50")
        records_window.attributes("-topmost", True)
        records_window.focus_force()

        style = ttk.Style(records_window)
        style.theme_use("default")
        
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=35,
                        fieldbackground="#2b2b2b",
                        bordercolor="#343638",
                        borderwidth=0,
                        font=("Segoe UI", 12))
        
        style.map('Treeview', background=[('selected', '#1f6aa5')])
        
        style.configure("Treeview.Heading",
                        background="#1f538d",
                        foreground="white",
                        relief="flat",
                        font=("Segoe UI", 13, "bold"))
        style.map("Treeview.Heading", background=[('active', '#14375e')])

        top_frame = ctk.CTkFrame(records_window, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = ctk.CTkLabel(top_frame, text="📊 Real-Time Activity Logs", font=("Segoe UI", 24, "bold"))
        title_lbl.pack(side="left")

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(top_frame, placeholder_text="Search by Name or ID...", width=250, height=35, textvariable=search_var)
        search_entry.pack(side="right", padx=(10, 0))
        
        table_frame = ctk.CTkFrame(records_window, corner_radius=15, fg_color="#2b2b2b")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        scroll_y = ctk.CTkScrollbar(table_frame, orientation="vertical")
        scroll_y.pack(side="right", fill="y", padx=(0, 5), pady=5)
        
        scroll_x = ctk.CTkScrollbar(table_frame, orientation="horizontal")
        scroll_x.pack(side="bottom", fill="x", padx=5, pady=(0, 5))

        columns = ("Timestamp", "UserID", "Name", "Department", "Contact", "Status")
        self.log_tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                                     yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.configure(command=self.log_tree.yview)
        scroll_x.configure(command=self.log_tree.xview)

        col_widths = {"Timestamp": 180, "UserID": 120, "Name": 200, "Department": 150, "Contact": 150, "Status": 120}
        for col in columns:
            self.log_tree.heading(col, text=col, anchor="w")
            self.log_tree.column(col, width=col_widths[col], anchor="w")

        self.log_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.log_tree.tag_configure("evenrow", background="#333333")
        self.log_tree.tag_configure("oddrow", background="#2b2b2b")
        
        self.log_tree.tag_configure("Login", foreground="#00FF00")  # Green text
        self.log_tree.tag_configure("Logout", foreground="#FF4444") # Red text

        def load_csv_data(search_query=""):
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
                
            file_path = r"D:\Data Scientist\Project\Final Project\Activity_Log.csv"
            
            if not os.path.exists(file_path):
                return
                
            try:
                import csv
                with open(file_path, mode="r", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    header = next(reader, None)
                    
                    count = 0
                    for row in reader:
                        if not row: continue # Skip empty lines
                        
                        if search_query.lower() in str(row).lower():
                            row_tag = "evenrow" if count % 2 == 0 else "oddrow"
                            
                            # Add an extra tag if it's a Login or Logout for color formatting
                            status = row[5] if len(row) > 5 else ""
                            tags = (row_tag, status) if status in ["Login", "Logout"] else (row_tag,)
                            
                            self.log_tree.insert("", "end", values=row, tags=tags)
                            count += 1
            except Exception as e:
                print(f"Error loading CSV: {e}")

        def on_search(event):
            load_csv_data(search_var.get())
            
        search_entry.bind("<KeyRelease>", on_search)

        refresh_btn = ctk.CTkButton(top_frame, text="🔄 Refresh", width=100, command=lambda: load_csv_data(search_var.get()))
        refresh_btn.pack(side="right", padx=10)

        load_csv_data()
         

    # ------------------ DB CONNECTION HELPER ------------------
    def get_db_connection(self):
        return pymysql.connect(
            host="mysql-3d922716-sharma-9707.e.aivencloud.com", 
            port=16640, 
            user="avnadmin", 
            password="AVNS_KIieaxZAfW67Nuh4VN2", 
            database="Security_system_2", 
            ssl={"ca": "ca.pem"},
            cursorclass=pymysql.cursors.Cursor
        )
        
    def hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()

    
    def update_time(self):
        try:
            if self.winfo_exists():
                now = datetime.now()
                self.date_lbl.configure(text=now.strftime("%d %B %Y"))
                self.time_lbl.configure(text=now.strftime("%I:%M:%S %p"))
                self.after(1000, self.update_time)
        except Exception:
            pass
        
    def clear_fields(self):
        self.pin_Admin_id.delete(0, "end")
        self.new_pin_entry.delete(0, "end")
        self.otp_entry.delete(0, "end")
        self.otp_btn.configure(state="normal")
        
        
    def show_home(self):
        self.pin_frame.pack_forget()
        self.content_frame.pack(side="right", fill="both", expand=True)
        
    def show_pin_change(self):
        self.content_frame.pack_forget()
        self.pin_frame.pack(side="right", fill="both", expand=True)
        
    def on_closing(self):
        
        log_activity(
            self.admin_info.get('user_id', 'Unknown'),
            self.admin_info.get('Name', 'Admin'),
            self.admin_info.get('Department', 'Admin'),
            self.admin_info.get('Contact', 'N/A'),
            "Logout"
        )
        if self.user_details_window and self.user_details_window.winfo_exists():
            self.user_details_window.destroy()
            
        if self.master:
            self.master.deiconify()
        self.destroy()    
        
#--------------------------------------------------PhotoViewer Class ------------------------------------------------------------
class PhotoViewer(ctk.CTkToplevel):
    def __init__(self, master, folder_path, title_text, target_type):
        super().__init__(master)
        self.title(title_text)
        self.geometry("1100x750+200+30")
        self.attributes("-topmost", True)
        
        self.folder_path = folder_path
        self.target_type = target_type
        
        self.image_references = []

        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        self.refresh_btn = ctk.CTkButton(self.top_frame, text="🔄 Refresh Gallery", font=("Segoe UI", 14, "bold"), command=self.refresh_photos)
        self.refresh_btn.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            label_text=f"📂 {title_text}", 
            label_font=("Segoe UI", 20, "bold"),
            fg_color="#1a1a1a"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.load_photos()

    def refresh_photos(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.image_references.clear()
        self.load_photos()

    def load_photos(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path, exist_ok=True)

        active_records = []
        try:
            conn = self.master.get_db_connection()
            cur = conn.cursor()
            
            if self.target_type == "user":
                cur.execute("SELECT user_id, Name, Face_Sample FROM users WHERE Face_Sample IS NOT NULL")
            else:
                cur.execute("SELECT Admin_id, Name, face_sample FROM admins WHERE face_sample IS NOT NULL")
                
            active_records = cur.fetchall()
        except Exception as e:
            print(f"DB Error while loading photos: {e}")
            ctk.CTkLabel(self.scroll_frame, text="⚠️ Database Connection Error").pack(pady=50)
            return
        finally:
            if 'conn' in locals() and conn: conn.close()

        active_ids = [str(row[0]) for row in active_records]

        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.png')]
        
        for filename in files:
            full_path = os.path.join(self.folder_path, filename)
            name_part = os.path.splitext(filename)[0]
            
            parts = name_part.split("_")
            

            if self.target_type == "admin" and name_part.startswith("admin_"):
                u_id = parts[-1] if len(parts) >= 3 else "N/A"
            else:
                u_id = parts[-1] if len(parts) >= 2 else "N/A"

            if u_id != "N/A" and u_id not in active_ids:
                try:
                    os.remove(full_path) 
                    print(f"Cleaned up orphaned photo from disk: {filename}")
                except Exception as e:
                   print(f"Could not delete orphaned file: {e}")
                

        valid_files_count = 0

        for row in active_records:
            u_id = str(row[0])
            u_name = str(row[1])
            blob = row[2]
            
            if self.target_type == "admin":
                expected_filename = f"admin_{u_name}_{u_id}.png"
            else:
                expected_filename = f"{u_name}_{u_id}.png"
                
            full_path = os.path.join(self.folder_path, expected_filename)
            
            if not os.path.exists(full_path) and blob:
                try:
                    import io
                    image_stream = io.BytesIO(blob)
                    img = PILImage.open(image_stream)
                    img.save(full_path, "PNG")
                    print(f"🔧 Recovered missing photo for {u_name} from Database.")
                except Exception as e:
                    print(f"Could not recover {expected_filename} from DB: {e}")
                    continue

            if os.path.exists(full_path):
                card = ctk.CTkFrame(self.scroll_frame, corner_radius=15, border_width=2, border_color="#3b8ed0", fg_color="#252525")
                card.grid(row=valid_files_count // 4, column=valid_files_count % 4, padx=15, pady=15, sticky="nsew")
                
                try:
                    pil_img = PILImage.open(full_path) 
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(160, 160))
                    self.image_references.append(ctk_img)

                    img_label = ctk.CTkLabel(card, image=ctk_img, text="")
                    img_label.pack(pady=(15, 5))
                except Exception as e:
                    print(f"Error loading {expected_filename}: {e}")

                ctk.CTkLabel(card, text=f"ID: {u_id}", font=("Segoe UI", 12, "bold"), text_color="#3b8ed0").pack()
                ctk.CTkLabel(card, text=u_name.replace("_", " ").title(), font=("Segoe UI", 15, "bold"), text_color="white").pack(pady=(0, 15))
                
                valid_files_count += 1

        if valid_files_count == 0:
            ctk.CTkLabel(self.scroll_frame, text="No active photos found in the database.", font=("Segoe UI", 16)).grid(row=0, column=0, columnspan=4, pady=50)
            
   

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = Admin(master=root)
    root.mainloop()