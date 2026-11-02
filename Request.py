import customtkinter as ctk
from tkinter import messagebox
import pymysql
from datetime import datetime
import smtplib 
from email.message import EmailMessage
import random
from twilio.rest import Client
import hashlib
import os
import glob
from Auth_admin import ScanUserWindow

# ------------------ UI SETTINGS ------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Request(ctk.CTkToplevel):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.title("User Registration System")
        self.geometry("1000x720+400+50")
        self.resizable(False, False)
        self.attributes("-topmost", True) 
        self.focus_force()

        # --- Variables ---
        self.entries = []
        self.generated_otp = None
        self.face_samples_collected = False

        self.sample_dir = r"D:\Data Scientist\Project\Final Project\User_Samples"
        
        if not os.path.exists(self.sample_dir):
            os.makedirs(self.sample_dir)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="👤 MENU", font=("Roboto", 20, "bold")).pack(pady=30)
        ctk.CTkButton(self.sidebar, text="Home", width=140, command=self.show_home).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="View Logs", width=140, command=self.show_view_logs).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Pin Change", width=140, command=self.show_Pin_change).pack(pady=10)

        # --- Content Frame (Home) ---
        self.content_frame = ctk.CTkFrame(self, corner_radius=15)
        self.content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.current_user_id = self.generate_numeric_id()

        self.id_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Generated User ID: {self.current_user_id}",
            font=("Roboto", 15, "bold"),
            text_color="#3b8ed0",
        )
        self.id_label.grid(row=0, column=0, columnspan=2, pady=15)

        self.left_col = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_col.grid(row=1, column=0, padx=20)
        self.right_col = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_col.grid(row=1, column=1, padx=20)

        # --- Registration Fields ---
        self.name_entry = self.add_field(self.left_col, "User Name")
        ctk.CTkLabel(self.left_col, text="Gender").pack(anchor="w")
        self.gender_var = ctk.StringVar(value="Male")
        ctk.CTkSegmentedButton(self.left_col, values=["Male", "Female", "Other"], variable=self.gender_var).pack(fill="x", pady=10)
        self.pin_entry = self.add_field(self.left_col, "Pin (4 Digit)")
        ctk.CTkLabel(self.left_col, text="Address").pack(anchor="w")
        self.address_text = ctk.CTkTextbox(self.left_col, height=90)
        self.address_text.pack(fill="x", pady=10)

        self.contact_entry = self.add_field(self.right_col, "Contact Number")
        self.email_entry = self.add_field(self.right_col, "Email")
        self.dept_entry = self.add_field(self.right_col, "Department")

        ctk.CTkLabel(self.right_col, text="Joining Date & Time").pack(anchor="w")
        self.join_entry = ctk.CTkEntry(self.right_col)
        self.join_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.join_entry.pack(fill="x", pady=10)
        self.entries.append(self.join_entry)

        self.face_var = ctk.StringVar(value="No")
        ctk.CTkSwitch(self.right_col, text="Face Sample Collected?", variable=self.face_var, onvalue="Yes", offvalue="No", command=self.handle_face_toggle).pack(anchor="w", pady=5)
        self.finger_var = ctk.StringVar(value="No")

        ctk.CTkButton(self.content_frame, text="Submit Request", height=45, width=250, command=self.validate_and_submit).grid(row=2, column=0, columnspan=2, pady=10)
        ctk.CTkButton(self.content_frame, text="Clear Form", height=45, width=250, fg_color="#444", command=self.clear_fields).grid(row=3, column=0, columnspan=2)

        # --- View Logs Frame ---
        self.view_logs_frame = ctk.CTkFrame(self, corner_radius=15)
        ctk.CTkLabel(self.view_logs_frame, text="Check Request Status", font=("Roboto", 22, "bold")).pack(pady=40)
        ctk.CTkLabel(self.view_logs_frame, text="User ID").pack(anchor="w", padx=200)
        self.log_user_id = ctk.CTkEntry(self.view_logs_frame, width=300)
        self.log_user_id.pack(pady=10)
        ctk.CTkLabel(self.view_logs_frame, text="User Name").pack(anchor="w", padx=200)
        self.log_user_name = ctk.CTkEntry(self.view_logs_frame, width=300)
        self.log_user_name.pack(pady=10)
        ctk.CTkButton(self.view_logs_frame, text="Check Status", width=200, height=40, command=self.check_request_status).pack(pady=20)
        self.status_label = ctk.CTkLabel(self.view_logs_frame, text="", font=("Roboto", 16, "bold"))
        self.status_label.pack(pady=10)

        # --- Pin Change Frame ---
        self.pin_change_frame = ctk.CTkFrame(self, corner_radius=15)
        ctk.CTkLabel(self.pin_change_frame, text="Pin Change Request", font=("Roboto", 22, "bold")).pack(pady=40)
        ctk.CTkLabel(self.pin_change_frame, text="User ID", font=("Roboto", 16)).place(x=200, y=150)
        self.pin_user_id = ctk.CTkEntry(self.pin_change_frame, width=300)
        self.pin_user_id.place(x=200, y=180)
        ctk.CTkLabel(self.pin_change_frame, text="New PIN (4 digits)", font=("Roboto", 16)).place(x=200, y=230)
        self.new_pin_entry = ctk.CTkEntry(self.pin_change_frame, width=300)
        self.new_pin_entry.place(x=200, y=260)
        ctk.CTkLabel(self.pin_change_frame, text="OTP", font=("Roboto", 16)).place(x=200, y=310)
        self.otp_entry = ctk.CTkEntry(self.pin_change_frame, width=150)
        self.otp_entry.place(x=200, y=340)
        self.otp_btn = ctk.CTkButton(self.pin_change_frame, text="Send OTP", command=self.handle_send_otp, width=100, height=30)
        self.otp_btn.place(x=400, y=340)
        ctk.CTkButton(self.pin_change_frame, text="Verify & Submit", command=self.verify_otp_and_proceed, width=300, height=30).place(x=200, y=400)

    # ------------------ MISSING METHODS ADDED BELOW ------------------

    def handle_send_otp(self):
        user_id = self.pin_user_id.get().strip()
        if not user_id:
            messagebox.showerror("Error", "Please enter User ID first", parent=self)
            return
        
        self.generated_otp = str(random.randint(100000, 999999))
        
        # Twilio Config 
        account_sid = "AC28018e898a11c75e02c46464f2545811"
        auth_token = "8266a2a2ff4cb21971abe4ecd902a96c"
        client = Client(account_sid, auth_token)

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Fetch BOTH contact number and Email from the database
            cursor.execute("SELECT contact_no, Email FROM users WHERE user_id=%s", (user_id,))
            result = cursor.fetchone()
            
            if result:
                contact_no = "+91" + str(result[0])
                user_email = result[1] 
                
                # 1. Attempt to send via Twilio SMS
                try:
                    client.messages.create(
                        body=f"Your OTP for PIN change is: {self.generated_otp}", 
                        from_="+18623862829", 
                        to=contact_no
                    )
                    messagebox.showinfo("Success", f"OTP sent via SMS to number ending in {contact_no[-4:]}", parent=self)
                    self.otp_btn.configure(state="disabled") 
                    
                # 2. Fallback to Email if Twilio fails
                except Exception as twilio_err:
                    print(f"Twilio SMS Failed: {twilio_err}")
                    
                    if user_email:
                        try:
                            # Using the standard email configuration for the project
                            sender = "kajuteam1124@gmail.com"
                            password = "esogwngbjfgigyeo" 
                            
                            email_msg = EmailMessage()
                            email_msg["Subject"] = "Security Alert: PIN Change OTP"
                            email_msg["From"] = sender
                            email_msg["To"] = user_email
                            email_msg.set_content(f"Dear User,\n\nYour OTP for changing your PIN is: {self.generated_otp}\n\nPlease do not share this code with anyone.")
                            
                            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                server.starttls()
                                server.login(sender, password)
                                server.send_message(email_msg)
                                
                            messagebox.showinfo("Success", f"SMS unavailable. OTP sent via Email to {user_email}", parent=self)
                            self.otp_btn.configure(state="disabled")
                            
                        except Exception as email_err:
                            messagebox.showerror("Error", f"Failed to send OTP via SMS and Email.\nEmail Error: {email_err}", parent=self)
                    else:
                        messagebox.showerror("Error", "SMS failed and no registered Email was found for this user.", parent=self)
                        
            else:
                messagebox.showerror("Error", "User ID not found in database.", parent=self)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve user data: {e}", parent=self)
        finally:
            if 'conn' in locals(): conn.close()

    def verify_otp_and_proceed(self):
        entered_otp = self.otp_entry.get().strip()
        new_pin = self.new_pin_entry.get().strip()
        
        if not self.generated_otp:
            messagebox.showerror("Error", "Please send OTP first.", parent=self)
            return
        if len(new_pin) != 4:
            messagebox.showerror("Error", "PIN must be exactly 4 digits.", parent=self)
            return
        
        # Verification works exactly the same whether it was sent via SMS or Email
        if entered_otp == self.generated_otp:
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                pin_hash = self.hash_pin(new_pin)
                cursor.execute("UPDATE users SET Pin_hash=%s WHERE user_id=%s", (pin_hash, self.pin_user_id.get().strip()))
                conn.commit()
                messagebox.showinfo("Success", "PIN updated successfully!", parent=self)
                self.otp_btn.configure(state="normal")
                self.show_home()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update PIN: {e}", parent=self)
            finally:
                if 'conn' in locals(): conn.close()
        else:
            messagebox.showerror("Error", "Invalid OTP. Please try again.", parent=self)

    # ------------------ REMAINING METHODS ------------------

    def handle_face_toggle(self):
        user_name = self.name_entry.get().strip()
        user_id = self.current_user_id

        if self.face_var.get() == "Yes":
            if not user_name:
                messagebox.showwarning("Input Required", "Please enter User Name before face sampling.", parent=self)
                self.face_var.set("No")
                return
            
            self.face_samples_collected = False
            self.scan_window = ScanUserWindow(self, user_name, user_id)
            self.withdraw() 
            
        else:
            confirm = messagebox.askyesno("Confirm", "Delete stored samples?", parent=self)
            if confirm:
                try:
                    pattern = os.path.join(self.sample_dir, f"{user_name}_{user_id}_*.jpg")
                    files = glob.glob(pattern)
                    for f in files: os.remove(f)
                    self.face_samples_collected = False
                    messagebox.showinfo("Deleted", "Stored biometric samples have been deleted.", parent=self)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete samples: {e}", parent=self)
            else:
                self.face_var.set("Yes")

    def on_registration_complete(self, name):
        self.deiconify() 
        self.focus_force()
        self.lift()
        pattern = os.path.join(self.sample_dir, f"{name}_{self.current_user_id}_*.jpg")
        captured_files = glob.glob(pattern)
        
        if len(captured_files) >= 20:
            self.face_samples_collected = True
            self.face_var.set("Yes")
        else:
            self.face_samples_collected = False
            self.face_var.set("No")

    def validate_and_submit(self):
        contact = self.contact_entry.get().strip()
        pin = self.pin_entry.get().strip()
        email = self.email_entry.get().strip()
        name = self.name_entry.get().strip()
       
        if self.face_var.get() == "Yes" and not self.face_samples_collected:
            messagebox.showerror("Biometrics Missing", "Face samples were not collected. Please toggle the Face switch to capture.", parent=self)
            return

        if not name or len(contact) != 10 or len(pin) != 4 or "@" not in email:
            messagebox.showerror("Validation Error", "Please fill all fields correctly:\n- 10-digit Contact\n- 4-digit PIN\n- Valid Email", parent=self)
            return
        
        try:
            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO request (user_id, user_name, contact_no, gender, department, address, email, joining_time, pin, face_sample, fingerprint) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (self.current_user_id, name, contact, self.gender_var.get(), self.dept_entry.get(), self.address_text.get("1.0", "end-1c"), email, self.join_entry.get(), pin, self.face_var.get(), self.finger_var.get())
                )
                conn.commit()
                self.send_confirmation_email(email, name)
                messagebox.showinfo("Success", f"Request for {name} submitted successfully.", parent=self)
                self.clear_fields()
                self.destroy() 
        except Exception as err:
            messagebox.showerror("DB Error", f"Failed to submit: {err}", parent=self)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def get_db_connection(self):
        return pymysql.connect(
            host="mysql-3d922716-sharma-9707.e.aivencloud.com",
            port=16640, user="avnadmin",
            password="AVNS_KIieaxZAfW67Nuh4VN2",
            database="Security_system_2",
            ssl={"ca": "ca.pem"}, cursorclass=pymysql.cursors.Cursor
        )

    def generate_numeric_id(self):
        return random.randint(10000000, 99999999)

    def add_field(self, parent, label):
        ctk.CTkLabel(parent, text=label).pack(anchor="w")
        entry = ctk.CTkEntry(parent)
        entry.pack(fill="x", pady=10)
        self.entries.append(entry)
        return entry

    def clear_fields(self):
        for e in self.entries:
            try:
                if e.winfo_exists(): e.delete(0, "end")
            except: continue
        self.address_text.delete("1.0", "end")
        self.join_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.gender_var.set("Male")
        self.face_var.set("No")
        self.face_samples_collected = False
        self.current_user_id = self.generate_numeric_id()
        self.id_label.configure(text=f"Generated User ID: {self.current_user_id}")

    def send_confirmation_email(self, to_email, name):
        try:
            sender, password = "kajuteam1124@gmail.com", "esogwngbjfgigyeo"
            msg = EmailMessage()
            msg["Subject"], msg["From"], msg["To"] = "Biometric Registration Received", sender, to_email
            msg.set_content(f"Hi {name},\n\nWe have received your biometric request (ID: {self.current_user_id}). Our models will update upon admin approval.")
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls(); server.login(sender, password)
            server.send_message(msg); server.quit()
        except: pass

    def show_view_logs(self):
        self.content_frame.grid_forget(); self.pin_change_frame.grid_forget() 
        self.view_logs_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def show_home(self):
        self.view_logs_frame.grid_forget(); self.pin_change_frame.grid_forget() 
        self.content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
    def show_Pin_change(self):
        self.content_frame.grid_forget(); self.view_logs_frame.grid_forget()
        self.pin_change_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
    def check_request_status(self):
        uid, uname = self.log_user_id.get(), self.log_user_name.get()
        if not uid.isdigit() or not uname:
            messagebox.showerror("Error", "Invalid inputs", parent=self)
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM request WHERE user_id=%s AND user_name=%s", (uid, uname))
            if cursor.fetchone():
                self.status_label.configure(text="⏳ Request Pending", text_color="orange")
            else:
                cursor.execute("SELECT user_id FROM users WHERE user_id=%s AND Name=%s", (uid, uname))
                if cursor.fetchone():
                    self.status_label.configure(text="✅ Request Accepted", text_color="green")
                else:
                    self.status_label.configure(text="❌ Not Found", text_color="red")
        except Exception as e: messagebox.showerror("Error", str(e), parent=self)
        finally:
            if 'conn' in locals(): conn.close()

    def hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = Request(master=root)
    root.mainloop()