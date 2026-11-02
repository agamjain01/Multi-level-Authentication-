from unittest import result
import customtkinter as ctk
from PIL import Image
from datetime import datetime
from Request import Request
from Admin import Admin
from UserDashboard import UserDashboard
from Auth_admin import ScanUserWindow
from tkinter import messagebox
import os
from activity_logger import log_activity
import traceback

class Security_System(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- Window ----------------
        self.title("Security System")
        self.geometry("1530x785+0+0")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.request_window = None
        self.admin_window = None
        self.scan_user_window = None
        self.admin_dashboard = None  

        # ---------------- Background ----------------
        try:
            self.bg_image = ctk.CTkImage(
                Image.open(r"Image\MainBgImage.jpg"),
                size=(1530, 785)
            )
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Background image not found: {e}")

        # ---------------- GLASS MAIN FRAME ----------------
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=32,
            fg_color=("#1e1e1e", "#1e1e1e"),
            bg_color="transparent",
            border_width=1,
            border_color="white"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.72)

        # ---------------- Header ----------------
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=35, pady=(25, 10))

        self.date_lbl = ctk.CTkLabel(self.header_frame, text="", font=("Segoe UI", 14), text_color="white")
        self.date_lbl.pack(side="left")

        self.time_lbl = ctk.CTkLabel(self.header_frame, text="", font=("Segoe UI", 14), text_color="white")
        self.time_lbl.pack(side="right")

        # ---------------- Title ----------------
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Security System with DualAuth",
            fg_color="#2a2a2a",
            corner_radius=14,
            height=48,
            font=("Segoe UI", 18, "bold"),
            text_color="white",
            padx=35
        )
        self.title_label.pack(pady=25)

        # ---------------- Buttons ----------------
        btn_config = {"width": 190, "height": 190, "corner_radius": 20, "font": ("Segoe UI", 22, "bold")}
        
        self.b1 = ctk.CTkButton(self.main_frame, text="USER", command=self.scan_user, **btn_config)
        self.b1.place(x=100, y=200)

        self.b2 = ctk.CTkButton(self.main_frame, text="REQUEST", command=self.request_action, **btn_config)
        self.b2.place(x=400, y=200)
        
        self.b3 = ctk.CTkButton(self.main_frame, text="ADMIN", command=self.admin_action, **btn_config)
        self.b3.place(x=700, y=200) 

        # ---------------- Footer ----------------
        self.footer = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.footer.place(x=750, y=450)
        
        self.footer_b1 = ctk.CTkButton(self.footer, text="ⓘ", command=self.information, width=60, fg_color="transparent", font=("Arial", 24))
        self.footer_b1.grid(row=0, column=0, padx=10)
        
        self.footer_b2 = ctk.CTkButton(self.footer, text="☼", command=self.change_theme, width=60, fg_color="transparent", font=("Arial", 24))
        self.footer_b2.grid(row=0, column=1, padx=10)
        
        self.footer_b3 = ctk.CTkButton(self.footer, text="👤", command=self.developer, width=60, fg_color="transparent", font=("Arial", 24))
        self.footer_b3.grid(row=0, column=2, padx=10)
        
        self.update_time()

    # ---------------- Clock ----------------
    def update_time(self):
        if self.winfo_exists():
            now = datetime.now()
            self.date_lbl.configure(text=f"Date: {now.strftime('%Y-%m-%d')}")
            self.time_lbl.configure(text=f"Time: {now.strftime('%H:%M:%S')}")
            self.after(1000, self.update_time)

    # ---------------- Window Management ----------------
    def request_action(self):
        if self.request_window is None or not self.request_window.winfo_exists():
            self.request_window = Request()
        self.request_window.lift()
        self.request_window.focus_force()

    def admin_action(self):
        if self.admin_window is None or not self.admin_window.winfo_exists():
            self.admin_window = ScanUserWindow(self, is_admin=True)
        else:
            self.admin_window.lift()

    def scan_user(self):
        if self.scan_user_window is None or not self.scan_user_window.winfo_exists():
            self.scan_user_window = ScanUserWindow(self)
        else:
            self.scan_user_window.lift()

    def test_auth(self, result, user_info=None):
        if self.admin_window:
            try:
                self.admin_window.destroy()
            except:
                pass
            self.admin_window = None
            
        if self.scan_user_window:
            try:
                self.scan_user_window.destroy()
            except:
                pass
            self.scan_user_window = None

        if result:
            is_admin_flag = user_info.get('is_admin', False) if user_info else False
            u_name = user_info.get('Name') or "Unknown" if user_info else "Admin"
            u_id = user_info.get('user_id', 'Unknown') if user_info else 'Unknown'
            dept = user_info.get('Department', 'Admin' if is_admin_flag else 'General') if user_info else 'General'
            contact = user_info.get('Contact', 'N/A') if user_info else 'N/A'
        
            log_activity(u_id, u_name, dept, contact, "Login")
    
            
            if is_admin_flag:
                self.after(300, lambda: self.launch_admin(user_info))
            else:
                self.after(300, lambda: self.launch_user(user_info))
        else:
            messagebox.showerror("Authentication Failed", "Access Revoked.", parent=self)

    def launch_admin(self, admin_info):
        try:
            self.withdraw()

            if hasattr(self, 'admin_dashboard') and self.admin_dashboard is not None:
                try:
                    if self.admin_dashboard.winfo_exists():
                        self.admin_dashboard.deiconify()
                        self.admin_dashboard.lift()
                        self.admin_dashboard.focus_force()
                        return
                except:
                    pass

    
            self.admin_dashboard = Admin(master=self, admin_info=admin_info)
            
            self.admin_dashboard.update()
            self.admin_dashboard.deiconify()
            self.admin_dashboard.lift()
            self.admin_dashboard.focus_force()

        except Exception as e:
            error_details = traceback.format_exc()
            messagebox.showerror(
                "Internal Component Error", 
                f"Admin Dashboard initialization failed!\n\nError: {e}",
                parent=self
            ) 


    def launch_user(self, user_info): 
        try:
            self.withdraw()

            if hasattr(self, 'user_dashboard') and self.user_dashboard is not None:
                try:
                    if self.user_dashboard.winfo_exists():
                        self.user_dashboard.deiconify()
                        self.user_dashboard.lift()
                        self.user_dashboard.focus_force()
                        return
                except:
                    pass

            dept_name = user_info.get('Department', 'GENERAL')

            self.user_dashboard = UserDashboard(master=self, user_info=user_info)
            
            self.user_dashboard.update()
            self.user_dashboard.deiconify()
            self.user_dashboard.lift()
            self.user_dashboard.focus_force()

        except Exception as e:
            error_details = traceback.format_exc()
            messagebox.showerror(
                "Internal Component Error", 
                f"User Dashboard initialization failed!\n\nError: {e}",
                parent=self
            ) 
            
    def change_theme(self):
        current_mode = ctk.get_appearance_mode()
        
        if current_mode.lower() == "dark":
            ctk.set_appearance_mode("light")
            
            self.footer_b2.configure(text="☾")
            
            self.main_frame.configure(fg_color="#F0F0F0", border_color="black")
            self.title_label.configure(fg_color="#E0E0E0", text_color="black")
            
            self.date_lbl.configure(text_color="black")
            self.time_lbl.configure(text_color="black")
            
            self.footer_b1.configure(text_color="black")
            self.footer_b2.configure(text_color="black")
            self.footer_b3.configure(text_color="black")

        else:
            ctk.set_appearance_mode("dark")
            
            self.footer_b2.configure(text="☼")
            
            self.main_frame.configure(fg_color="#1e1e1e", border_color="white")
            self.title_label.configure(fg_color="#2a2a2a", text_color="white")
            
            self.date_lbl.configure(text_color="white")
            self.time_lbl.configure(text_color="white")
            
            self.footer_b1.configure(text_color="white")
            self.footer_b2.configure(text_color="white")
            self.footer_b3.configure(text_color="white")
    
    def information(self):
        info_win = ctk.CTkToplevel(self)
        info_win.title("Project Information")
        info_win.geometry("900x700+450+100")
        info_win.attributes("-topmost", True)
        info_win.resizable(True, True)

        title_label = ctk.CTkLabel(info_win, text="🛡️ SECURITY SYSTEM USING DUALAUTH", font=("Roboto", 28, "bold"), text_color="#3b8ed0")
        title_label.pack(pady=(20, 10))
        
        scroll_frame = ctk.CTkScrollableFrame(info_win, width=840, height=550, corner_radius=15)
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self._add_info_section(scroll_frame, "📋 Project Overview", 
            "This project is an advanced Smart Security Management System designed to bridge the gap between "
            "physical security and digital intelligence. It serves as an automated gatekeeper that manages "
            "personnel entry through biometric and digital verification.")

        self._add_info_section(scroll_frame, "🔍 Implementation Logics", 
            "Think of this as a 'Digital Security Guard.' It recognizes faces just like a human would but "
            "never gets tired. It asks for a secret PIN to make sure you are who you say you are, and it "
            "alerts the authorities (Admin) if someone unknown tries to gain access."
            "The system is a multi-layered authentication architecture. It utilizes a Deep Learning pipeline "
            "for Biometric Feature Extraction and a Relational Database Management System (RDBMS) for "
            "state persistence. It implements asynchronous notification protocols via SMTP and REST APIs.")

        tech_content = (
            "• Python: The core engine.\n"
            "• Dlib & OpenCV: Computer Vision for face detection and image processing.\n"
            "• ResNet-50: A Deep Residual Network used for highly accurate face recognition.\n"
            "• CustomTkinter: For a modern, responsive User Interface.\n"
            "• MySQL/Aiven: Cloud-hosted database for secure logs and user data.\n"
            "• Twilio & SMTP: For SMS OTP and Email notifications.")
        self._add_info_section(scroll_frame, "🛠️ Technical Stack", tech_content)

        roles_content = (
            "👤 USER ROLE:\n"
            "   - Request registration by providing biometric (Face) and personal data.\n"
            "   - Authenticate at checkpoints using the recognized face and 4-digit PIN.\n"
            "   - Manage personal security settings (PIN Change via OTP).\n\n"
            "🔑 ADMIN ROLE:\n"
            "   - Review, Approve, or Reject pending registration requests.\n"
            "   - Monitor real-time access logs and system health.\n"
            "   - Manage the global user database and system overrides.")
        self._add_info_section(scroll_frame, "👥 Roles & Responsibilities", roles_content)


    def _add_info_section(self, parent, title, content):
        """Helper function to format sections consistently"""
        section_title = ctk.CTkLabel(parent, text=title, font=("Roboto", 18, "bold"), text_color="#3b8ed0", justify="left")
        section_title.pack(anchor="w", pady=(15, 5), padx=10)
        
        section_content = ctk.CTkLabel(parent, text=content, font=("Roboto", 14), wraplength=780, justify="left")
        section_content.pack(anchor="w", pady=(0, 10), padx=20)
    
    def developer(self):
        dev_win = ctk.CTkToplevel(self)
        dev_win.title("Project Development Team")
        dev_win.geometry("1100x550+300+150")
        dev_win.attributes("-topmost", True)
        dev_win.resizable(False, False)

        ctk.CTkLabel(dev_win, text="🚀 MEET THE DEVELOPERS", font=("Roboto", 26, "bold"), text_color="#3b8ed0").pack(pady=20)
        cards_container = ctk.CTkFrame(dev_win, fg_color="transparent")
        cards_container.pack(padx=20, pady=10, fill="both", expand=True)

        developers = [
            {
                "name": "Agam Jain",
                "email": "agam8126@gmail.com",
                "role": "UI Developer / Secondary Authentication Developement / DBA",
                "contact": "+91 7078395009"
            },
            {
                "name": "Abhijeet Sharma",
                "email": "jeetabhi1308@gmail.com",
                "role": " Primary Authentication Development",
                "contact": "+91 7078499281"
            },
            {
                "name": "Vanshika Tripathi",
                "email": "tripathivanshika12@gmail.com",
                "role": "Project Testing / Cloud DB Integration",
                "contact": "+91 8410840615"
            }
        ]
        
        for i, dev in enumerate(developers):
            dev_card = ctk.CTkFrame(cards_container, width=320, corner_radius=15, border_width=2, border_color="#3b8ed0")
            dev_card.grid(row=0, column=i, padx=15, pady=10, sticky="nsew")
            dev_card.grid_propagate(False)

            ctk.CTkLabel(dev_card, text="👨‍💻", font=("Roboto", 50)).pack(pady=(20, 10))
            ctk.CTkLabel(dev_card, text=dev["name"], font=("Roboto", 20, "bold"), text_color="#3b8ed0").pack(pady=5)
            
            ctk.CTkFrame(dev_card, height=2, width=200, fg_color="#444").pack(pady=5)
            
            details_font = ("Roboto", 13)
            
            ctk.CTkLabel(dev_card, text=f"📍 Role:", font=("Roboto", 13, "bold")).pack(pady=(10, 0))
            ctk.CTkLabel(dev_card, text=dev["role"], font=details_font, wraplength=280).pack()

            ctk.CTkLabel(dev_card, text=f"📧 Email:", font=("Roboto", 13, "bold")).pack(pady=(15, 0))
            ctk.CTkLabel(dev_card, text=dev["email"], font=details_font).pack()

            ctk.CTkLabel(dev_card, text=f"📞 Contact:", font=("Roboto", 13, "bold")).pack(pady=(15, 0))
            ctk.CTkLabel(dev_card, text=dev["contact"], font=details_font).pack()

        cards_container.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(dev_win, text="Close", command=dev_win.destroy, width=150, fg_color="#444").pack(pady=20)
         

if __name__ == "__main__":
    app = Security_System()
    app.mainloop()
    