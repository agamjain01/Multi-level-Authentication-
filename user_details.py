from email.message import EmailMessage
import smtplib
import customtkinter as ctk
from tkinter import messagebox, ttk
import pymysql
from datetime import datetime
import re
import hashlib
import threading
import serial
import time

# --- Arduino Configuration ---
PORT = "COM9"   
BAUD = 9600

class User_details(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- Window ----------------  
        self.title("Security System")
        self.geometry("1530x785+0+0")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        tabview = ctk.CTkTabview(
            self, width=1500, height=750,
            fg_color=("#91DBDE", "#96cbd3")
        )
        tabview.place(x=15, y=15)

        tabview.add("Requests")
        tabview.add("User Details")
        tabview.add("Admin Details")
        
        # --- Hardware State ---
        self.arduino = None
        self.current_assigned_slot = None
        

# ---------------------------------------------  Requests Tab -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # ---------------- Frame 1 ----------------
        Frame_1 = ctk.CTkFrame(tabview.tab("Requests"), corner_radius=15, width=1200, height=250, fg_color=("#1e1e1e", "#1e1e1e"))
        Frame_1.place(x=20, y=20)

        ctk.CTkLabel(Frame_1, text="User Id :", font=("Roboto", 15, "bold")).place(x=10, y=25)
        self.User_ID_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.User_ID_for_request_entry.place(x=80, y=25)

        ctk.CTkLabel(Frame_1, text="Login Id :", font=("Roboto", 15, "bold")).place(x=325, y=25)
        self.Logiin_ID_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.Logiin_ID_for_request_entry.place(x=400, y=25)

        ctk.CTkLabel(Frame_1, text="User Name :", font=("Roboto", 15, "bold")).place(x=650, y=25)
        self.User_name_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.User_name_for_request_entry.place(x=760, y=25)

        ctk.CTkLabel(Frame_1, text="Contact No. :", font=("Roboto", 15, "bold")).place(x=10, y=75)
        self.contact_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.contact_for_request_entry.place(x=130, y=75)

        ctk.CTkLabel(Frame_1, text="Address :", font=("Roboto", 15, "bold")).place(x=350, y=75)
        self.Address_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.Address_for_request_entry.place(x=430, y=75)

        ctk.CTkLabel(Frame_1, text="Gender :", font=("Roboto", 15, "bold")).place(x=650, y=75)
        self.gender_for_request_var = ctk.StringVar(value="Select")
        ctk.CTkSegmentedButton(Frame_1, values=["Male", "Female", "Other"], variable=self.gender_for_request_var).place(x=730, y=75)

        ctk.CTkLabel(Frame_1, text="Pin :", font=("Roboto", 15, "bold")).place(x=900, y=75)
        self.Pin_for_request_entry = ctk.CTkEntry(Frame_1, width=150)
        self.Pin_for_request_entry.place(x=940, y=75)

        ctk.CTkLabel(Frame_1, text="Email :", font=("Roboto", 15, "bold")).place(x=10, y=125)
        self.Email_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.Email_for_request_entry.place(x=80, y=125)

        ctk.CTkLabel(Frame_1, text="Joining Time :", font=("Roboto", 15, "bold")).place(x=325, y=125)
        self.joining_date_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.joining_date_for_request_entry.place(x=450, y=125)

        ctk.CTkLabel(Frame_1, text="Department :", font=("Roboto", 15, "bold")).place(x=700, y=125)
        self.department_for_request_entry = ctk.CTkEntry(Frame_1, width=200)
        self.department_for_request_entry.place(x=820, y=125)

        self.face_for_requestsample = ctk.StringVar(value="No")
        self.fingerprint_for_request = ctk.StringVar(value="No")
        
        ctk.CTkLabel(Frame_1, text="Face Sample :", font=("Roboto", 15, "bold")).place(x=10, y=175)       
        ctk.CTkSwitch(Frame_1, text="Face Sample", variable=self.face_for_requestsample, onvalue="Yes", offvalue="No").place(x=130, y=180)

        ctk.CTkLabel(Frame_1, text="Fingerprint :", font=("Roboto", 15, "bold")).place(x=350, y=175)
        ctk.CTkSwitch(Frame_1, text="Fingerprint", variable=self.fingerprint_for_request, command=self.fingerprint_switch, onvalue="Yes", offvalue="No").place(x=480, y=180)
        
        # ----------------------- frame 2 Requests -----------------------
        Frame_2 = ctk.CTkFrame(tabview.tab("Requests"), corner_radius=15, width=200, height=250, fg_color=("#3F3C3C", "#1e1e1e"))
        Frame_2.place(x=1250, y=20)
        
        ctk.CTkButton(Frame_2, text="Accept", command=self.accept_request, width=150, height=50, fg_color="#003F6F", hover_color="#129A61", font=("Segoe UI", 16, "bold")).place(x=25, y=25)
        ctk.CTkButton(Frame_2, text="Reject", command=self.reject_request, width=150, height=50, fg_color="#003F6F", hover_color="#D9534F", font=("Segoe UI", 16, "bold")).place(x=25, y=100)    
        ctk.CTkButton(Frame_2, text="Clear", command=self.Clear_for_request_entries, width=150, height=50, fg_color="#003F6F", hover_color="#F0AD4E", font=("Segoe UI", 16, "bold")).place(x=25, y=175)
        
        # ------------------------ frame 3 for count -----------------------
        frame_3 = ctk.CTkFrame(tabview.tab("Requests"), corner_radius=15, width=1430, height=50, fg_color=("#3F3C3C", "#1e1e1e"))
        frame_3.place(x=20, y=300)
        ctk.CTkLabel(frame_3, text="Requests Count :", font=("Roboto", 15, "bold")).place(x=10, y=10)
        self.Show_request_count_label = ctk.CTkLabel(frame_3, text="0", font=("Roboto", 15, "bold"))
        self.Show_request_count_label.place(x=150, y=10)
        self.request_user_count()
        
        ctk.CTkLabel(frame_3, text="Request Table DB", font=("Roboto", 15, "bold")).place(x=650, y=10)
        ctk.CTkLabel(frame_3, text="Search By Request Id :", font=("Roboto", 15, "bold")).place(x=980, y=10)
        self.search_request_entry = ctk.CTkEntry(frame_3, placeholder_text="Enter User Id", width=200)
        self.search_request_entry.place(x=1150, y=10)
        ctk.CTkButton(frame_3, text="Search", command=self.search_request_by_id,width=30, height=30, fg_color="#00F0BC", hover_color="#129A61", text_color="black", font=("Segoe UI", 12, "bold")).place(x=1360, y=10)

        # ---------------- Frame 4 Table ----------------
        Frame_4 = ctk.CTkFrame(tabview.tab("Requests"), width=1430, height=300)
        Frame_4.place(x=20, y=370)

        columns = ("User ID", "User Name", "Contact No", "Address", "Gender", "Department", "Email", "Joining Date", "Pin", "Face Sample", "Fingerprint")
        self.tree = ttk.Treeview(Frame_4, columns=columns, show="headings")
        self.tree.place(x=0, y=0, relwidth=1, relheight=1)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.bind("<<TreeviewSelect>>", self.fill_for_request_entries)
        self.load_requests_data()
        
        
# ----------------------------------------------------- User Details Tab ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ----------------------- frame 1 for User Details  -----------------------
        
        Frame_1_user = ctk.CTkFrame(tabview.tab("User Details"), corner_radius=15,width=1050, height=250, fg_color=("#3F3C3C", "#1e1e1e"))
        Frame_1_user.place(x=20, y=20)
        
        ctk.CTkLabel(Frame_1_user, text="User Id :", font=("Roboto", 15, "bold")).place(x=10, y=25)
        self.User_ID_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.User_ID_for_user_entry.place(x=80, y=25)
        
        ctk.CTkLabel(Frame_1_user, text="Login Id :", font=("Roboto", 15, "bold")).place(x=325, y=25)
        self.Login_ID_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.Login_ID_for_user_entry.place(x=400, y=25)
        
        ctk.CTkLabel(Frame_1_user, text="Name :", font=("Roboto", 15, "bold")).place(x=650, y=25)
        self.Name_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.Name_for_user_entry.place(x=760, y=25)
        
        ctk.CTkLabel(Frame_1_user, text="Contact No. :", font=("Roboto", 15, "bold")).place(x=10, y=75)
        self.Contact_no_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.Contact_no_for_user_entry.place(x=130, y=75)
        
        ctk.CTkLabel(Frame_1_user, text="Address :", font=("Roboto", 15, "bold")).place(x=350, y=75)
        self.Address_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.Address_for_user_entry.place(x=430, y=75)
    
        ctk.CTkLabel(Frame_1_user, text="Gender :", font=("Roboto", 15, "bold")).place(x=650, y=75)
        self.Gender_for_user_var = ctk.StringVar()
        ctk.CTkSegmentedButton(Frame_1_user, values=["Male", "Female", "Other"], variable=self.Gender_for_user_var).place(x=760, y=75)
        
        ctk.CTkLabel(Frame_1_user, text="Email :", font=("Roboto", 15, "bold")).place(x=10, y=125)
        self.Email_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.Email_for_user_entry.place(x=80, y=125)
        
        ctk.CTkLabel(Frame_1_user, text="Joining Date :", font=("Roboto", 15, "bold")).place(x=325, y=125)
        self.Joining_date_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.Joining_date_for_user_entry.place(x=450, y=125)
        
        ctk.CTkLabel(Frame_1_user, text="Department :", font=("Roboto", 15, "bold")).place(x=700, y=125)
        self.Department_for_user_entry = ctk.CTkEntry(Frame_1_user, width=200)
        self.Department_for_user_entry.place(x=820, y=125)
        
        ctk.CTkLabel(Frame_1_user, text="Face Sample :", font=("Roboto", 15, "bold")).place(x=10, y=175)
        self.Face_sample_for_user_var = ctk.StringVar(value="No")
        ctk.CTkSwitch(Frame_1_user, text="No / Yes", variable=self.Face_sample_for_user_var, onvalue = "Yes", offvalue = "No").place(x=130, y=180)
        
        ctk.CTkLabel(Frame_1_user, text="Fingerprint :", font=("Roboto", 15, "bold")).place(x=350, y=175)
        self.Fingerprint_for_user_var = ctk.StringVar(value="No")
        ctk.CTkSwitch(Frame_1_user, text="No / Yes", variable=self.Fingerprint_for_user_var,command=self.user_details_fingerprint_switch, onvalue = "Yes", offvalue = "No").place(x=480, y=180)
        
        ctk.CTkLabel(Frame_1_user, text="Fingerprint ID :", font=("Roboto", 15, "bold")).place(x=600, y=175)
        self.Fingerprint_ID_for_user_entry = ctk.CTkEntry(Frame_1_user, width=50)
        self.Fingerprint_ID_for_user_entry.place(x=725, y=175)
        
        #---------------------  frame 1.1 for User Details  -----------------------
        frame_1_1_user = ctk.CTkFrame(tabview.tab("User Details"), corner_radius=15,width=150 ,height=250, fg_color=("#3F3C3C", "#1e1e1e"))
        frame_1_1_user.place(x=1085, y=20)
        
        ctk.CTkLabel(frame_1_1_user, text="Update \n Biometric Data", font=("Roboto", 15, "bold")).place(x=10, y=10)
        
        
        ctk.CTkButton(frame_1_1_user, text="Update FC", width=120, height=50, fg_color="#003F6F", hover_color="#129A61", 
                      font=("Segoe UI", 16, "bold")).place(x=15, y=75)
        
        ctk.CTkButton(frame_1_1_user, text="Update FP", width=120, height=50, command=self.update_existing_fingerprint, fg_color="#003F6F", hover_color="#129A61", 
                      font=("Segoe UI", 16, "bold")).place(x=15, y=150) 
        
        
        # -----------------------  frame 2 for User Details  -----------------------
        Frame_2_user = ctk.CTkFrame(tabview.tab("User Details"), corner_radius=15,width=200, height=250, fg_color=("#3F3C3C", "#1e1e1e"))
        Frame_2_user.place(x=1250, y=20)
        
        Update_button = ctk.CTkButton(Frame_2_user, text="Update", command=self.update_for_user, width=150, height=50, fg_color="#003F6F", hover_color="#129A61", font=("Segoe UI", 16, "bold"))
        Update_button.place(x=25, y=25)
        
        Delete_button = ctk.CTkButton(Frame_2_user, text="Delete", command=self.delete_for_user, width=150, height=50, fg_color="#003F6F", hover_color="#D9534F", font=("Segoe UI", 16, "bold"))
        Delete_button.place(x=25, y=100)
        
        clear_button_for_user = ctk.CTkButton(Frame_2_user, text="Clear", command=self.Clear_for_user_entries, width=150, height=50, fg_color="#003F6F", hover_color="#F0AD4E", font=("Segoe UI", 16, "bold"))
        clear_button_for_user.place(x=25, y=175)
        
        
        # ------------------------  frame 3 for User Details  -----------------------
        frame_3_user = ctk.CTkFrame(tabview.tab("User Details"), corner_radius=15,width=1430, height=50, fg_color=("#3F3C3C", "#1e1e1e"))
        frame_3_user.place(x=20, y=300)
        
        ctk.CTkLabel(frame_3_user, text="Active Users Count :", font=("Roboto", 15, "bold")).place(x=10, y=10)
        self.active_user_count_label = ctk.CTkLabel(frame_3_user, text="0", font=("Roboto", 15, "bold"))
        self.active_user_count_label.place(x=170, y=10)
        self.update_user_count()
        
        ctk.CTkLabel(frame_3_user, text="User Details Table DB", font=("Roboto", 15, "bold")).place(x=650, y=10)
        ctk.CTkLabel(frame_3_user, text="Search By User Id :", font=("Roboto", 15, "bold")).place(x=1000, y=10)
        self.search_user_entry = ctk.CTkEntry(frame_3_user, placeholder_text="Enter User Id", width=200)
        self.search_user_entry.place(x=1150, y=10)
        ctk.CTkButton(frame_3_user, text="Search", command=self.search_user_by_id,width=30, height=30, fg_color="#00F0BC", hover_color="#129A61", text_color="black", font=("Segoe UI", 12, "bold")).place(x=1360, y=10)   
        
        # Output Box for Serial Data
        self.output_box = ctk.CTkTextbox(tabview.tab("User Details"), width=1430, height=60, font=("Courier", 12))
        self.output_box.place(x=20, y=680)
        self.output_box.configure(state="disabled")
        
        
        # ----------------------- frame 4 for User Details Data Load   -----------------------
        Frame_4_user = ctk.CTkFrame(tabview.tab("User Details"), corner_radius=15,width=1430, height=300, fg_color=("#3F3C3C", "#1e1e1e"))
        Frame_4_user .place(x=20, y=370)
        
        columns_user = ("User ID", "Login ID", "Name", "Contact No", "Address", "Email", "Joining Date", "Department", "Gender", "Face Sample", "Fingerprint", "Fingerprint ID")
        self.user_tree = ttk.Treeview(Frame_4_user, columns=columns_user, show="headings")
        self.user_tree.place(x=0, y=0, relwidth=1, relheight=1) 
        for col in columns_user:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=120)
            
        self.user_tree.bind("<<TreeviewSelect>>", self.Fill_user_details_entries)
        self.load_user_details_data()
        
        
# ----------------------------------------------------------------  Admin Details Tab -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------- frame 1 for Admin  -----------------------
        
        Frame_1_admin = ctk.CTkFrame(tabview.tab("Admin Details"), corner_radius=15,width=800, height=250, fg_color=("#3F3C3C", "#1e1e1e"))
        Frame_1_admin.place(x=20, y=20)
        
        ctk.CTkLabel(Frame_1_admin,text="Admin ID :",font=("Roboto",15,"bold")).place(x=10,y=25)
        self.admin_Id=ctk.CTkEntry(Frame_1_admin,width=200)
        self.admin_Id.place(x=100,y=25)
        
        ctk.CTkLabel(Frame_1_admin,text="Login Id :",font=("Roboto",15,"bold")).place(x=350,y=25)
        self.login_Id_admin=ctk.CTkEntry(Frame_1_admin,width=200)
        self.login_Id_admin.place(x=450,y=25)
        
        ctk.CTkLabel(Frame_1_admin,text="Name :",font=("Roboto",15,"bold")).place(x=10,y=75)
        self.Name_admin=ctk.CTkEntry(Frame_1_admin,width=200)
        self.Name_admin.place(x=100,y=75)
        
        ctk.CTkLabel(Frame_1_admin,text="Contact no. :",font=("Roboto",15,"bold")).place(x=350,y=75)
        self.Contact_No_admin=ctk.CTkEntry(Frame_1_admin,width=200)
        self.Contact_No_admin.place(x=450,y=75)
        
        ctk.CTkLabel(Frame_1_admin,text="Email. :",font=("Roboto",15,"bold")).place(x=10,y=125)
        self.Email_admin=ctk.CTkEntry(Frame_1_admin,width=200)
        self.Email_admin.place(x=100,y=125)
        
        ctk.CTkLabel(Frame_1_admin,text="Joining Date :",font=("Roboto",15,"bold")).place(x=350,y=125)
        self.Joining_date_admin=ctk.CTkEntry(Frame_1_admin,width=200)
        self.Joining_date_admin.place(x=470,y=125)
        
        ctk.CTkLabel(Frame_1_admin,text="Gender :",font=("Roboto",15,"bold")).place(x=10,y=175)
        self.Gender_for_Admin_var = ctk.StringVar()
        ctk.CTkSegmentedButton(Frame_1_admin, values=["Male", "Female", "Other"], variable=self.Gender_for_Admin_var).place(x=90, y=180)
        
        ctk.CTkLabel(Frame_1_admin,text="Pin :",font=("Roboto",15,"bold")).place(x=280,y=175)
        self.pin_admin=ctk.CTkEntry(Frame_1_admin,width=100)
        self.pin_admin.place(x=325,y=175)
        
        ctk.CTkLabel(Frame_1_admin,text="Fingerprint Id :",font=("Roboto",15,"bold")).place(x=450,y=175)
        self.Admin_Fingerprint_Id_admin=ctk.CTkEntry(Frame_1_admin,width=100)
        self.Admin_Fingerprint_Id_admin.place(x=570,y=175)
        
 
        #---------------   frame 1.1 for admin face sample and fingerprint -----------------
        frame1_1_admin_face_fingerprint = ctk.CTkFrame(tabview.tab("Admin Details"), corner_radius=15,width=150, height=250,fg_color=("#3F3C3C", "#1e1e1e"))
        frame1_1_admin_face_fingerprint.place(x=850, y=20)
        
        admin_face_sample_button = ctk.CTkButton(frame1_1_admin_face_fingerprint, text="Face Sample", width=130, height=50, fg_color="#2BA9B2", hover_color="#129A61", font=("Segoe UI", 16, "bold"))
        admin_face_sample_button.place(x=10, y=50)
        
        admin_fingerprint_button = ctk.CTkButton(frame1_1_admin_face_fingerprint, text="Fingerprint", command=self.enroll_admin_fingerprint, width=130, height=50, fg_color="#2BA9B2", hover_color="#129A61", font=("Segoe UI", 16, "bold"))
        admin_fingerprint_button.place(x=10, y=150) 
        
        # -----------------------  frame 2 for Admin  -----------------------
        Frame_2_admin = ctk.CTkFrame(tabview.tab("Admin Details"), corner_radius=15,width=400, height=250, fg_color=("#3F3C3C", "#1e1e1e"))
        Frame_2_admin.place(x=1030, y=20)
        
        Add_button_admin = ctk.CTkButton(Frame_2_admin, text="Add", command=self.add_admin, width=150, height=50, fg_color="#003F6F", hover_color="#129A61", font=("Segoe UI", 16, "bold"))
        Add_button_admin.place(x=50, y=50)  
        
        clear_button_admin = ctk.CTkButton(Frame_2_admin, text="Clear", command=self.Clear_Admin_details, width=150, height=50, fg_color="#003F6F", hover_color="#F0AD4E", font=("Segoe UI", 16, "bold"))
        clear_button_admin.place(x=220, y=50)
        
        delete_button_admin = ctk.CTkButton(Frame_2_admin, text="Delete", command=self.delete_admin, width=150, height=50, fg_color="#003F6F", hover_color="#D9534F", font=("Segoe UI", 16, "bold"))
        delete_button_admin.place(x=50, y=150)
        
        update_button_admin = ctk.CTkButton(Frame_2_admin, text="Update", command=self.update_admin, width=150, height=50, fg_color="#003F6F", hover_color="#129A61", font=("Segoe UI", 16, "bold"))
        update_button_admin.place(x=220, y=150)
        
        
        
        # ------------------------  frame 3 for Admin  -----------------------
        frame_3_admin = ctk.CTkFrame(tabview.tab("Admin Details"), corner_radius=15,width=1430, height=50, fg_color=("#3F3C3C", "#1e1e1e"))
        frame_3_admin.place(x=20, y=300)
        
        ctk.CTkLabel(frame_3_admin, text="Admin Count :", font=("Roboto", 15, "bold")).place(x=10, y=10)
        self.admin_count_label = ctk.CTkLabel(frame_3_admin, text="0", font=("Roboto", 15, "bold"))
        self.admin_count_label.place(x=150, y=10)
        self.update_admin_count()
        
        ctk.CTkLabel(frame_3_admin, text="Admin Table DB", font=("Roboto", 15, "bold")).place(x=650, y=10)
        
        ctk.CTkLabel(frame_3_admin, text="Search By Admin User Id :", font=("Roboto", 15, "bold")).place(x=980, y=10)  
        self.search_admin_entry = ctk.CTkEntry(frame_3_admin, placeholder_text="Enter Admin Id", width=150)
        self.search_admin_entry.place(x=1200, y=10)
        ctk.CTkButton(frame_3_admin, text="Search", command=self.search_admin_by_id, width=60, height=30, fg_color="#00F0BC", hover_color="#129A61", text_color="black", font=("Segoe UI", 12, "bold")).place(x=1360, y=10)
        
        
        # ----------------------- frame 4 for Admin   data load -----------------------
        Frame_4_admin = ctk.CTkFrame(tabview.tab("Admin Details"), corner_radius=15,width=1430, height=300, fg_color=("#3F3C3C", "#1e1e1e"))
        Frame_4_admin .place(x=20, y=370)
        
        columns_for_admin=("Admin Id","Login Id","Name","Contact no","Address","Email","Joining Time","Gender","Face Sample","FingerPrint","Admin_Fingerprint_Id")
        self.admin_tree=ttk.Treeview(Frame_4_admin,columns=columns_for_admin,show="headings")
        self.admin_tree.place(x=0,y=0,relwidth=1,relheight=1)
        for col in columns_for_admin:
            self.admin_tree.heading(col,text=col)
            self.admin_tree.column(col,width=120)
            
        self.admin_tree.bind("<<TreeviewSelect>>", self.Fill_Admin_details_entries)
        self.load_Admin_details()
        
        self.connect_arduino()
        
# ------------------------------------------------------- Arduino Connection and Serial Reading -----------------------------------------------------------------------------------------------------------------------------------------------------------------------   
    def connect_arduino(self):
        try:
            self.arduino = serial.Serial(PORT, BAUD, timeout=1)
            time.sleep(2)
            self.log(f"✅ Connected to Hardware on {PORT}")
        except Exception as e:
            print(f"Serial Error: {e}")
            messagebox.showerror("Hardware Error", f"Could not connect to sensor on {PORT}. Check connection.")    
                
    def log(self, message):
        """Displays hardware messages in the Output Box"""
        self.output_box.configure(state="normal")
        self.output_box.insert("end", f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.output_box.see("end")
        self.output_box.configure(state="disabled") 
        
    def send_command(self, command):
        if self.arduino and self.arduino.is_open:
            self.arduino.write((command + "\n").encode())  
            
    def read_response_loop(self):
        """Background thread to read Arduino data dynamically."""
        while self.arduino and self.arduino.is_open:
            if self.arduino.in_waiting:
                line = self.arduino.readline().decode(errors='ignore').strip()
                if line:
                    self.log("Sensor: " + line)
                    self.update_status_lbl(line)
                    if "MATCHED" in line:
                        user_id = line.split(":")[1]
                        self.log(f"✅ ACCESS GRANTED (ID: {user_id})")
            time.sleep(0.1)

    def match_fingerprint(self):
        self.log("\n--- INITIATING MATCH MODE ---")
        self.send_command("MATCH")
        threading.Thread(target=self.read_response_loop, daemon=True).start()

    def enroll_fingerprint_direct(self):
        user_id = self.Fingerprint_ID_for_user_entry.get()
        if not user_id.isdigit():
            self.log("❌ Invalid ID for Enrollment. Check ID entry.")
            return
        self.log(f"\n--- ENROLLING ID {user_id} ---")
        self.send_command(f"ENROLL {user_id}")
        threading.Thread(target=self.read_response_loop, daemon=True).start()
        
    def update_existing_fingerprint(self):
        user_id = self.User_ID_for_user_entry.get()
        existing_fp_id = self.Fingerprint_ID_for_user_entry.get()

        if not user_id:
            messagebox.showwarning("Selection Error", "Please select a user from the table first.")
            return

        if not existing_fp_id or existing_fp_id.lower() == "none" or existing_fp_id == "":
            messagebox.showinfo("No Sample Found", f"User ID {user_id} has no existing fingerprint sample to update.")
            return

        confirm = messagebox.askyesno("Confirm Update", 
                                      f"This will delete the old fingerprint in Slot {existing_fp_id} and record a new one. Proceed?")
        
        if confirm:
            self.log(f"Updating FP: Deleting old sample in Slot {existing_fp_id}")
            self.send_command(f"DELETE {existing_fp_id}")
            
            self.after(500, lambda: self.trigger_re_enrollment(user_id, existing_fp_id))

    def trigger_re_enrollment(self, user_id, slot):
        """Triggers the enrollment UI for the same slot ID"""
        self.enroll_window = ctk.CTkToplevel(self)
        self.enroll_window.title("Update Fingerprint")
        self.enroll_window.geometry("400x300+600+250")
        self.enroll_window.attributes('-topmost', True)
        
        self.status_lbl = ctk.CTkLabel(self.enroll_window, text=f"Updating Slot {slot}\nPlace NEW finger on sensor...", font=("Roboto", 16))
        self.status_lbl.pack(pady=50)
        
        self.log(f"Update Mode: Re-enrolling Slot {slot}")
        self.send_command(f"ENROLL {slot}")
        threading.Thread(target=self.process_enrollment_ui_for_user, args=(user_id, slot), daemon=True).start()

    def delete_fingerprint_direct(self):
        user_id = self.Fingerprint_ID_for_user_entry.get()
        if not user_id.isdigit():
            self.log("❌ Invalid ID for Deletion.")
            return
        self.log(f"\n--- DELETING ID {user_id} ---")
        self.send_command(f"DELETE {user_id}")
        threading.Thread(target=self.read_response_loop, daemon=True).start()

                
    def fingerprint_switch(self):
        toggle_state = self.fingerprint_for_request.get()
        user_id = self.User_ID_for_request_entry.get()
        
        if not user_id:
            messagebox.showwarning("Selection Error", "Please select a user request from the table first.")
            self.after(0, lambda: self.fingerprint_for_request.set("No"))
            return

        if toggle_state == "Yes":
            slot = self.get_next_fingerprint_slot(is_admin=False)
            if not slot:
                messagebox.showerror("Memory Full", "Fingerprint sensor memory is full.")
                self.after(0, lambda: self.fingerprint_for_request.set("No"))
                return
            
            self.enroll_window = ctk.CTkToplevel(self)
            self.enroll_window.title("Fingerprint Enrollment")
            self.enroll_window.geometry("400x300+600+250")
            self.enroll_window.attributes('-topmost', True)
            self.status_lbl = ctk.CTkLabel(self.enroll_window, text=f"Preparing slot {slot}...", font=("Roboto", 16))
            self.status_lbl.pack(pady=50)
            
            self.send_command(f"ENROLL {slot}")
            self.current_assigned_slot = slot 
            threading.Thread(target=self.process_enrollment_ui, daemon=True).start()
            
            self.update_request_db_status("Yes", user_id)
        
        else:
            confirm = messagebox.askyesno("Confirm Deletion", 
                                          f"Are you sure you want to delete the fingerprint data for User {user_id}?")
            
            if confirm:
                if self.current_assigned_slot:
                    self.log(f"Deleting slot: {self.current_assigned_slot}")
                    self.send_command(f"DELETE {self.current_assigned_slot}")
                    self.current_assigned_slot = None 
                
                self.update_request_db_status("No", user_id)
            else:
                self.fingerprint_for_request.set("Yes")

    def update_request_db_status(self, status, user_id):
        try:
            conn = self.db_connect()
            cur = conn.cursor()
            cur.execute("UPDATE request SET fingerprint=%s WHERE user_id=%s", (status, user_id))
            conn.commit()
            cur.close()
            conn.close()
            self.load_requests_data() 
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to update table: {e}")

    def process_enrollment_ui(self):
        start_time = time.time()
        success = False
        
        while time.time() - start_time < 30:
            try:
                if self.arduino and self.arduino.is_open and self.arduino.in_waiting:
                    line = self.arduino.readline().decode(errors='ignore').strip()
                    self.update_status_lbl(line)
                    
                    if "ENROLL_SUCCESS" in line:
                        success = True
                        self.log(f"✅ Slot {self.current_assigned_slot} Enrolled Successfully.")
                        self.after(2000, self.enroll_window.destroy)
                        break
                    
                    if "ENROLL_FAILED" in line or "ERROR" in line:
                        self.log("❌ Enrollment Failed on Hardware.")
                        break
            except Exception as e:
                self.log(f"Connection Lost: {e}")
                break
            time.sleep(0.1)
        
        if not success:
            self.after(0, lambda: self.fingerprint_for_request.set("No"))
            self.current_assigned_slot = None
            if hasattr(self, 'enroll_window') and self.enroll_window.winfo_exists():
                self.after(1000, self.enroll_window.destroy)

    def update_status_lbl(self, msg):
        if hasattr(self, 'status_lbl') and self.status_lbl.winfo_exists():
            self.after(0, lambda: self.status_lbl.configure(text=msg))

    def get_next_fingerprint_slot(self, is_admin=False):
        conn = self.db_connect()
        cur = conn.cursor()
        if is_admin:
            cur.execute("SELECT Admin_Fingerprint_Id FROM admins")
            start, end = 1, 10
        else:
            cur.execute("SELECT user_Fingerprint_Id FROM users")
            start, end = 11, 127
        ids = [row[0] for row in cur.fetchall() if row[0] is not None]
        cur.close()
        conn.close()
        for i in range(start, end + 1):
            if i not in ids: return i
        return None
        
# -----------------------------------------------  For requests tab Function ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def request_user_count(self):
        try: 
            conn = self.db_connect()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM request")
            self.Show_request_count_label.configure(text=str(cur.fetchone()[0]))
            cur.close(); conn.close()
        except Exception as e: print(e)
    
    def load_requests_data(self):
        try:
            conn = self.db_connect()
            cur = conn.cursor()
            cur.execute("SELECT user_id, user_name, contact_no, address, gender, department, email, joining_time, pin, face_sample, fingerprint FROM request")
            rows = cur.fetchall()
            for item in self.tree.get_children(): self.tree.delete(item)
            for row in rows: self.tree.insert("", "end", values=row)
            self.request_user_count()
            cur.close(); conn.close()
        except Exception as e: print(e)

    def fill_for_request_entries(self, event):
        selected = self.tree.focus()
        if not selected: return
        values = self.tree.item(selected, "values")

        self.Clear_for_request_entries()
        self.User_ID_for_request_entry.insert(0, values[0])
        self.User_name_for_request_entry.insert(0, values[1])
        self.contact_for_request_entry.insert(0, values[2])
        self.Address_for_request_entry.insert(0, values[3])
        self.gender_for_request_var.set(values[4])
        self.department_for_request_entry.insert(0, values[5])
        self.Email_for_request_entry.insert(0, values[6])
        self.joining_date_for_request_entry.insert(0, values[7])
        self.Pin_for_request_entry.insert(0, values[8])
        self.face_for_requestsample.set(values[9])
        self.fingerprint_for_request.set(values[10])
        
        self.Logiin_ID_for_request_entry.delete(0, "end")
        self.Logiin_ID_for_request_entry.insert(0, self.generate_login_id())

    def reject_request(self):
        uid = self.User_ID_for_request_entry.get()
        if not uid: return
        
        conn = self.db_connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM request WHERE user_id=%s", (uid,))
        conn.commit()
        cur.close(); conn.close()
        
        self.send_confirmation_email(self.Email_for_request_entry.get(), "Registration Rejected", f"Dear {self.User_name_for_request_entry.get()},\nYour registration request has been rejected by the Admin.")
        
        self.load_requests_data()
        self.Clear_for_request_entries()
        messagebox.showinfo("Success", "Request Rejected & Email Sent.")

    def accept_request(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        login_id = self.Logiin_ID_for_request_entry.get()
        pin = self.Pin_for_request_entry.get()
        user_id = self.User_ID_for_request_entry.get()

        if not user_id or not pin:
            messagebox.showerror("Error", "Please select a request first.")
            return

        pin_hash = self.hash_pin(pin)
        conn = self.db_connect()
        cur = conn.cursor()

        try:
            cur.execute("""INSERT INTO users (user_id, login_username, Name, Contact_no, Address, Email, Joining_time, Department, Gender, Pin_hash, Face_Sample, Fingerprint, user_Fingerprint_Id) 
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
                        (user_id, login_id, self.User_name_for_request_entry.get(), self.contact_for_request_entry.get(), 
                         self.Address_for_request_entry.get(), self.Email_for_request_entry.get(), current_time, 
                         self.department_for_request_entry.get(), self.gender_for_request_var.get(), pin_hash, 
                         self.face_for_requestsample.get(), self.fingerprint_for_request.get(), self.current_assigned_slot))

            cur.execute("DELETE FROM request WHERE user_id=%s", (user_id,))
            conn.commit()
            
            self.send_confirmation_email(self.Email_for_request_entry.get(), "Registration Accepted", f"Dear {self.User_name_for_request_entry.get()},\nYour request is ACCEPTED.\nLogin ID: {login_id}")
            messagebox.showinfo("Success", "Request Accepted & Email Sent.")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            self.load_user_details_data()
            self.update_user_count()
            cur.close()
            conn.close()
            self.load_requests_data()
            self.Clear_for_request_entries()
            self.current_assigned_slot = None 

    def Clear_for_request_entries(self):
        self.User_ID_for_request_entry.delete(0, "end")
        self.Logiin_ID_for_request_entry.delete(0, "end")
        self.User_name_for_request_entry.delete(0, "end")
        self.contact_for_request_entry.delete(0, "end")
        self.Address_for_request_entry.delete(0, "end")
        self.Email_for_request_entry.delete(0, "end")
        self.department_for_request_entry.delete(0, "end")
        self.joining_date_for_request_entry.delete(0, "end")
        self.Pin_for_request_entry.delete(0, "end")
        self.gender_for_request_var.set("Select")
        self.face_for_requestsample.set("No")      
        self.fingerprint_for_request.set("No")
        
    def generate_login_id(self):
        name = self.User_name_for_request_entry.get().strip()
        user_id = self.User_ID_for_request_entry.get().strip()
        if not name or not user_id: return ""
        return f"{name.split()[0].lower()}_{user_id[-4:].zfill(4)}"
    
    def search_request_by_id(self):
        request_id = self.search_request_entry.get().strip()
        conn = self.db_connect(); cur = conn.cursor()
        try:
            q = "SELECT user_id, user_name, contact_no, address, gender, department, email, joining_time, pin, face_sample, fingerprint FROM request"
            if request_id: cur.execute(q + " WHERE user_id = %s", (request_id,))
            else: cur.execute(q)
            rows = cur.fetchall()
            for item in self.tree.get_children(): self.tree.delete(item)
            for row in rows: self.tree.insert("", "end", values=row)
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: cur.close(); conn.close()

    
    
#---------------------------------------------------------------  Functions for User Details Tab ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def update_user_count(self):
        try: 
            conn = self.db_connect(); cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            self.active_user_count_label.configure(text=str(cur.fetchone()[0]))
            cur.close(); conn.close()
        except Exception as e: print(e)
    
    def load_user_details_data(self):
        try:
            conn=self.db_connect(); cur=conn.cursor()
            cur.execute("SELECT user_id, login_username, Name, Contact_no, Address, Email, Joining_time, Department, Gender, Face_Sample, Fingerprint, user_Fingerprint_Id FROM users")
            rows = cur.fetchall()
            for item in self.user_tree.get_children(): self.user_tree.delete(item)
            for row in rows: self.user_tree.insert("", "end", values=row)
            self.update_user_count()
            cur.close(); conn.close()
        except Exception as e: print(e) 
            
    def Fill_user_details_entries(self, event):
        selected = self.user_tree.focus()
        if not selected:
            return
        values = self.user_tree.item(selected, "values")
        self.Clear_for_user_entries()
        
        self.User_ID_for_user_entry.insert(0, values[0])
        self.Login_ID_for_user_entry.insert(0, values[1])
        self.Name_for_user_entry.insert(0, values[2])
        self.Contact_no_for_user_entry.insert(0, values[3])
        self.Address_for_user_entry.insert(0, values[4])
        self.Email_for_user_entry.insert(0, values[5])
        self.Joining_date_for_user_entry.insert(0, values[6])
        self.Department_for_user_entry.insert(0, values[7])
        self.Gender_for_user_var.set(str(values[8]).strip())
        face_val = str(values[9]).strip()
        self.Face_sample_for_user_var.set(face_val if face_val in ["Yes", "No"] else "No")
        finger_val = str(values[10]).strip()
        self.Fingerprint_for_user_var.set(finger_val if finger_val in ["Yes", "No"] else "No")
        fp_id = values[11] if values[11] and str(values[11]).lower() != "none" else ""
        self.Fingerprint_ID_for_user_entry.insert(0, fp_id)
        
    def Clear_for_user_entries(self):
        self.User_ID_for_user_entry.delete(0, "end")
        self.Login_ID_for_user_entry.delete(0, "end")
        self.Name_for_user_entry.delete(0, "end")
        self.Contact_no_for_user_entry.delete(0, "end")
        self.Address_for_user_entry.delete(0, "end")
        self.Email_for_user_entry.delete(0, "end")
        self.Joining_date_for_user_entry.delete(0, "end")
        self.Department_for_user_entry.delete(0, "end")
        self.Face_sample_for_user_var.set("No")
        self.Fingerprint_for_user_var.set("No")
        self.Fingerprint_ID_for_user_entry.delete(0, "end")
        
    def delete_for_user(self):
        user_id = self.User_ID_for_user_entry.get()
        if not user_id: return
        conn = self.db_connect(); cur = conn.cursor()
        try:
            self.delete_fingerprint_direct()
            cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
            conn.commit()
            self.send_confirmation_email(self.Email_for_user_entry.get(), "Account Deleted", f"Dear {self.Name_for_user_entry.get()},\nYour account has been deleted by the Admin.")
            messagebox.showinfo("Success", f"User with ID {user_id} Deleted Successfully.")
        except Exception as e: messagebox.showerror("DB Error", str(e))
        finally:
            cur.close(); conn.close()
            self.load_user_details_data(); self.update_user_count(); self.Clear_for_user_entries()
        
    def update_for_user(self):
        user_id = self.User_ID_for_user_entry.get()
        if not user_id: return
        conn = self.db_connect(); cur = conn.cursor()
        try:
            cur.execute("""UPDATE users SET login_username=%s, Name=%s, Contact_no=%s, Address=%s, Email=%s,
                        Joining_time=%s, Department=%s, Gender=%s, Face_Sample=%s, Fingerprint=%s, 
                        user_Fingerprint_Id=%s WHERE user_id=%s""",
                        (self.Login_ID_for_user_entry.get(), self.Name_for_user_entry.get(), 
                         self.Contact_no_for_user_entry.get(), self.Address_for_user_entry.get(),
                         self.Email_for_user_entry.get(), self.Joining_date_for_user_entry.get(), 
                         self.Department_for_user_entry.get(), self.Gender_for_user_var.get(), 
                         self.Face_sample_for_user_var.get(), self.Fingerprint_for_user_var.get(), 
                         self.Fingerprint_ID_for_user_entry.get(), user_id))
            conn.commit()
            self.send_confirmation_email(self.Email_for_user_entry.get(), "Account Updated", f"Dear {self.Name_for_user_entry.get()},\nYour account details have been updated by the Admin.")
            messagebox.showinfo("Success", f"User {user_id} Updated Successfully.")
        except Exception as e: messagebox.showerror("Error", f"Failed to update user: {e}")  
        finally:
            cur.close(); conn.close()
            self.load_user_details_data(); self.Clear_for_user_entries()
            
    def search_user_by_id(self):
        user_id = self.search_user_entry.get().strip()
        conn = self.db_connect(); cur = conn.cursor()
        try:
            q = "SELECT user_id, login_username, Name, Contact_no, Address, Email, Joining_time, Department, Gender, Face_Sample, Fingerprint, user_Fingerprint_Id FROM users"
            if user_id: cur.execute(q + " WHERE user_id = %s", (user_id,))
            else: cur.execute(q)
            rows = cur.fetchall()
            for item in self.user_tree.get_children(): self.user_tree.delete(item)
            for row in rows: self.user_tree.insert("", "end", values=row)
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: cur.close(); conn.close()
        
    def user_details_fingerprint_switch(self):
        toggle_state = self.Fingerprint_for_user_var.get()
        user_id = self.User_ID_for_user_entry.get()
        
        if not user_id:
            messagebox.showwarning("Selection Error", "Please select a user from the table first.")
            self.after(0, lambda: self.Fingerprint_for_user_var.set("No"))
            return

        if toggle_state == "Yes":
            slot = self.get_next_fingerprint_slot(is_admin=False)
            if not slot:
                messagebox.showerror("Memory Full", "Fingerprint sensor memory is full (Slots 11-127).")
                self.after(0, lambda: self.Fingerprint_for_user_var.set("No"))
                return
            
            self.enroll_window = ctk.CTkToplevel(self)
            self.enroll_window.title("User FP Enrollment")
            self.enroll_window.geometry("400x300+600+250")
            self.enroll_window.attributes('-topmost', True)
            
            self.status_lbl = ctk.CTkLabel(self.enroll_window, text=f"Scanning for Slot {slot}...", font=("Roboto", 16))
            self.status_lbl.pack(pady=50)
            
            self.log(f"User Details: Initiating Enrollment for Slot {slot}")
            self.send_command(f"ENROLL {slot}")
            
            self.Fingerprint_ID_for_user_entry.delete(0, "end")
            self.Fingerprint_ID_for_user_entry.insert(0, str(slot))
            
            threading.Thread(target=self.process_enrollment_ui_for_user, args=(user_id, slot), daemon=True).start()
        
        else:
            current_slot = self.Fingerprint_ID_for_user_entry.get()
            
            if not current_slot or current_slot.lower() == "none":
                self.update_user_db_biometric("No", None, user_id)
                return

            confirm = messagebox.askyesno("Confirm Deletion", 
                                          f"Delete Fingerprint for User {user_id} (Slot {current_slot}) from hardware and database?")
            
            if confirm:
                self.log(f"User Details: Deleting Slot {current_slot}")
                self.send_command(f"DELETE {current_slot}")
                
                self.Fingerprint_ID_for_user_entry.delete(0, "end")
                self.update_user_db_biometric("No", None, user_id)
            else:
                self.Fingerprint_for_user_var.set("Yes")

    def process_enrollment_ui_for_user(self, user_id, slot):
        start_time = time.time()
        success = False
        
        while time.time() - start_time < 30:
            if self.arduino and self.arduino.is_open and self.arduino.in_waiting:
                line = self.arduino.readline().decode(errors='ignore').strip()
                self.update_status_lbl(line)
                
                if "ENROLL_SUCCESS" in line:
                    success = True
                    self.log(f"✅ User {user_id} Slot {slot} Enrolled.")
                    self.update_user_db_biometric("Yes", slot, user_id)
                    self.after(1500, self.enroll_window.destroy)
                    break
                
                if "FAILED" in line or "ERROR" in line:
                    break
            time.sleep(0.1)
        
        if not success:
            self.after(0, lambda: self.Fingerprint_for_user_var.set("No"))
            self.after(0, lambda: self.Fingerprint_ID_for_user_entry.delete(0, "end"))

    def update_user_db_biometric(self, status, slot, user_id):
        try:
            conn = self.db_connect()
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET Fingerprint=%s, user_Fingerprint_Id=%s WHERE user_id=%s", 
                (status, slot, user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            self.load_user_details_data() 
        except Exception as e:
            messagebox.showerror("DB Error", f"Update failed: {e}")

# ---------------------------------------------------------------  Admin Details  Function  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def update_admin_count(self):
        try: 
            conn = self.db_connect(); cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM admins")
            self.admin_count_label.configure(text=str(cur.fetchone()[0]))
            cur.close(); conn.close()
        except Exception as e: print(e)
    
    def load_Admin_details(self):
        try:
            conn=self.db_connect(); cur=conn.cursor()
            cur.execute("SELECT Admin_id, loginId_Admin, Name, Contact_no, Address, Email, Joining_time, Gender, Face_Sample, Fingerprint, Admin_Fingerprint_Id FROM admins")
            rows=cur.fetchall()
            for item in self.admin_tree.get_children(): self.admin_tree.delete(item)
            for row in rows: self.admin_tree.insert("", "end", values=row)
            cur.close(); conn.close()
        except Exception as e: print(e)
            
    def Fill_Admin_details_entries(self, event):
        selected = self.admin_tree.focus()
        if not selected: return
        values = self.admin_tree.item(selected, "values")

        self.Clear_Admin_details()
        self.admin_Id.insert(0, values[0])
        self.login_Id_admin.insert(0, values[1])
        self.Name_admin.insert(0, values[2])
        self.Contact_No_admin.insert(0, values[3])
        self.Email_admin.insert(0, values[5])  
        self.Joining_date_admin.insert(0, values[6])
        self.Gender_for_Admin_var.set(values[7])
        self.Admin_Fingerprint_Id_admin.insert(0, values[10] if values[10] != "None" else "")    

    def Clear_Admin_details(self):
        self.admin_Id.delete(0, "end")
        self.login_Id_admin.delete(0, "end")
        self.Name_admin.delete(0, "end")
        self.Contact_No_admin.delete(0, "end")
        self.Email_admin.delete(0, "end")
        self.Joining_date_admin.delete(0, "end")
        self.pin_admin.delete(0, "end")
        self.Admin_Fingerprint_Id_admin.delete(0, "end")
        self.Gender_for_Admin_var.set("Select")

    def add_admin(self):
        admin_id = self.admin_Id.get()
        pin = self.pin_admin.get()
        if not admin_id or not pin:
            messagebox.showerror("Error", "Admin ID and Pin are required.")
            return
        
        pin_hash = self.hash_pin(pin)
        conn = self.db_connect(); cur = conn.cursor()
        try:
            cur.execute("""INSERT INTO admins (Admin_id, loginId_Admin, Name, Contact_no, Email, Joining_time, Gender, Pin_hash, Admin_Fingerprint_Id)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (admin_id, self.login_Id_admin.get(), self.Name_admin.get(), self.Contact_No_admin.get(), 
                         self.Email_admin.get(), self.Joining_date_admin.get(), self.Gender_for_Admin_var.get(), 
                         pin_hash, self.Admin_Fingerprint_Id_admin.get() or None))
            conn.commit()
            messagebox.showinfo("Success", "Admin Added Successfully.")
        except Exception as e: messagebox.showerror("DB Error", str(e))
        finally:
            cur.close(); conn.close()
            self.load_Admin_details(); self.update_admin_count(); self.Clear_Admin_details()

    def update_admin(self):
        admin_id = self.admin_Id.get()
        if not admin_id: return
        conn = self.db_connect(); cur = conn.cursor()
        try:
            cur.execute("""UPDATE admins SET loginId_Admin=%s, Name=%s, Contact_no=%s, Email=%s, 
                           Joining_time=%s, Gender=%s, Admin_Fingerprint_Id=%s WHERE Admin_id=%s""",
                        (self.login_Id_admin.get(), self.Name_admin.get(), self.Contact_No_admin.get(), 
                         self.Email_admin.get(), self.Joining_date_admin.get(), self.Gender_for_Admin_var.get(), 
                         self.Admin_Fingerprint_Id_admin.get() or None, admin_id))
            conn.commit()
            messagebox.showinfo("Success", "Admin Updated Successfully.")
        except Exception as e: messagebox.showerror("DB Error", str(e))
        finally:
            cur.close(); conn.close()
            self.load_Admin_details(); self.Clear_Admin_details()

    def delete_admin(self):
        admin_id = self.admin_Id.get()
        if not admin_id: return
        conn = self.db_connect(); cur = conn.cursor()
        try:
            cur.execute("DELETE FROM admins WHERE Admin_id=%s", (admin_id,))
            conn.commit()
            messagebox.showinfo("Success", "Admin Deleted Successfully.")
        except Exception as e: messagebox.showerror("DB Error", str(e))
        finally:
            cur.close(); conn.close()
            self.load_Admin_details(); self.update_admin_count(); self.Clear_Admin_details()

    def search_admin_by_id(self):
        admin_id = self.search_admin_entry.get().strip()
        conn = self.db_connect(); cur = conn.cursor()
        try:
            q = "SELECT Admin_id, loginId_Admin, Name, Contact_no, Address, Email, Joining_time, Gender, Face_Sample, Fingerprint, Admin_Fingerprint_Id FROM admins"
            if admin_id: cur.execute(q + " WHERE Admin_id=%s", (admin_id,))
            else: cur.execute(q)
            rows = cur.fetchall()
            for item in self.admin_tree.get_children(): self.admin_tree.delete(item)
            for row in rows: self.admin_tree.insert("", "end", values=row)
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: cur.close(); conn.close()

    def enroll_admin_fingerprint(self):
        """Hardware call to enroll an Admin fingerprint (Slots 1-10)"""
        slot = self.get_next_fingerprint_slot(is_admin=True)
        if not slot:
            messagebox.showerror("Memory Full", "Admin fingerprint slots (1-10) are full.")
            return

        self.Admin_Fingerprint_Id_admin.delete(0, "end")
        self.Admin_Fingerprint_Id_admin.insert(0, str(slot))

        self.enroll_window = ctk.CTkToplevel(self)
        self.enroll_window.geometry("400x300+600+250")
        self.enroll_window.attributes('-topmost', True)
        self.status_lbl = ctk.CTkLabel(self.enroll_window, text=f"Preparing Admin Slot {slot}...", font=("Roboto", 16))
        self.status_lbl.pack(pady=50)

        self.log(f"Enrolling Admin into slot {slot}")
        self.send_command(f"ENROLL {slot}")
        threading.Thread(target=self.process_enrollment_ui, daemon=True).start()
        
# ----------------------------------------------------- Common Functions for all  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def db_connect(self):
            try:
                return pymysql.connect(
                    host="mysql-3d922716-sharma-9707.e.aivencloud.com", 
                    port=16640, 
                    user="avnadmin", 
                    password="AVNS_KIieaxZAfW67Nuh4VN2", 
                    database="Security_system_2", 
                    ssl={"ca": "ca.pem"},
                    cursorclass=pymysql.cursors.Cursor
                )
            except Exception as e:
                messagebox.showerror("Connection Error", f"Could not connect to database: {e}")
                return None

    def send_confirmation_email(self, to_email, subject, body):
        try:
            sender = "kajuteam1124@gmail.com"
            password = "esogwngbjfgigyeo" 
            email_msg = EmailMessage()
            email_msg["Subject"] = subject
            email_msg["From"] = sender
            email_msg["To"] = to_email
            email_msg.set_content(body)
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(email_msg)
        except Exception as e:
            print(f"Email Error: {e}")
            
    def hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()
    
    def on_closing(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        self.destroy()

if __name__ == "__main__":
    app = User_details()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()