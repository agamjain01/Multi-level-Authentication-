import customtkinter as ctk
from activity_logger import log_activity
from datetime import datetime

ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue") 

class UserDashboard(ctk.CTkToplevel):
    def __init__(self, master, user_info): 
        super().__init__(master)

        self.user_info = user_info 
        
        self.username = user_info.get('Name', 'User')
        self.department = user_info.get('Department', 'GENERAL').upper()
        self.role = "User"
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Retrieve the specific configuration for the logged-in user's department
        self.config = self.get_department_config()

        self.title(f"Enterprise Dashboard - {self.config['title']}")
        self.geometry("1530x785+0+0")
        self.minsize(950, 550)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}
        self.frames = {}

        self.create_sidebar()
        self.create_main_frames()
        self.select_frame("Home")

    # ------------------ DEPARTMENT CONFIGURATION DICTIONARY ------------------
    def get_department_config(self):
        """Defines the unique UI structures, cards, and modules for real-world departments."""
        configs = {
            "IT": {
                "title": "Information Technology",
                "modules": [("🏠 System Overview", "Home"), ("💻 Server Monitor", "Workspace"), ("📊 Network Logs", "Analytics"), ("⚙️ Settings", "Settings")],
                "home_cards": [("Active Servers", "1,248", "🟢 99.9% Uptime"), ("Pending Tickets", "42", "🔴 High Priority"), ("Network Load", "75%", "🔵 Stable")],
                "log_feed": "SYS_LOG {id}: Firewall ping accepted from node 0{id}...\nSEC_WARN {id}: Unauthorized access blocked."
            },
            "HR": {
                "title": "Human Resources",
                "modules": [("🏠 HR Dashboard", "Home"), ("👥 Recruitment", "Workspace"), ("📊 Attrition Data", "Analytics"), ("⚙️ Settings", "Settings")],
                "home_cards": [("Active Employees", "450", "🟢 +5 this month"), ("Pending Leave Reqs", "12", "🔴 Needs action"), ("Open Job Postings", "8", "🔵 Sourcing Candidates")],
                "log_feed": "EMP_RECORD {id}: Payroll details updated successfully...\nLEAVE_REQ {id}: Approved by manager."
            },
            "ACCOUNTS": {
                "title": "Finance & Accounts",
                "modules": [("🏠 Financial Overview", "Home"), ("🧮 Calculations", "Workspace"), ("📊 Revenue Analytics", "Analytics"), ("⚙️ Settings", "Settings")],
                "home_cards": [("Monthly Revenue", "$4.2M", "🟢 +12% vs last month"), ("Pending Invoices", "24", "🔴 $142,000 pending"), ("Q3 Expenses", "$1.1M", "🔵 On Budget")],
                "log_feed": "INV_GEN {id}: Invoice sent to client.\nTXN_CLEAR {id}: Payment of $14,000 received and reconciled."
            },
            "MANAGEMENT": {
                "title": "Executive Management",
                "modules": [("🏠 Executive Overview", "Home"), ("✅ Approvals", "Workspace"), ("📊 Global KPI", "Analytics"), ("⚙️ Settings", "Settings")],
                "home_cards": [("Global Growth", "18%", "🟢 Exceeding Target"), ("Strategic Tasks", "5", "🔴 Require Sign-off"), ("Market Share", "24%", "🔵 Stable")],
                "log_feed": "STRATEGY_UPDATE {id}: Regional report compiled.\nEXEC_ACTION {id}: Budget allocation approved."
            },
            "SALES": {
                "title": "Sales Operations",
                "modules": [("🏠 Sales Dashboard", "Home"), ("🎯 CRM Pipeline", "Workspace"), ("📊 Conversion Data", "Analytics"), ("⚙️ Settings", "Settings")],
                "home_cards": [("Active Leads", "850", "🟢 High volume"), ("Deals Closed", "45", "🔵 This Week"), ("Revenue Target", "78%", "🔴 Needs Push")],
                "log_feed": "CRM_UPDATE {id}: Deal moved to negotiation stage.\nCALL_LOG {id}: Outbound call completed (14m)."
            },
            "GENERAL": {
                "title": f"{self.department} Department",
                "modules": [("🏠 Home Workspace", "Home"), ("📊 General Analytics", "Analytics"), ("⚙️ Settings", "Settings")],
                "home_cards": [("Active Users", "1,248", "🟢 +12% this week"), ("System Load", "42%", "🔵 Stable"), ("Pending Tasks", "7", "🔴 Needs action")],
                "log_feed": "SYS_EVENT {id}: Routine synchronization completed.\nUSER_ACTION {id}: Profile updated."
            }
        }
        
        # Return the matching config, or fallback to GENERAL if it's a niche department
        return configs.get(self.department, configs["GENERAL"])


    # ------------------ UI GENERATION ------------------
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) 

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="CoreDash v2.0", font=ctk.CTkFont(size=22, weight="bold"), text_color="#3b8ed0")
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        profile_text = f"👤 {self.username}\nRole: [{self.role}]\nDept: {self.config['title']}"
        self.profile_label = ctk.CTkLabel(self.sidebar_frame, text=profile_text, font=ctk.CTkFont(size=12), justify="left", anchor="w")
        self.profile_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Dynamically spawn sidebar buttons based on Department Config
        for i, (btn_text, frame_name) in enumerate(self.config["modules"], start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=btn_text, corner_radius=8, height=40, anchor="w",
                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                command=lambda n=frame_name: self.select_frame(n)
            )
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[frame_name] = btn

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"], command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="ew")

    def create_main_frames(self):
        """Dynamically creates frames matching the configured modules for this department."""
        for _, frame_name in self.config["modules"]:
            frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
            self.frames[frame_name] = frame
            
            # Route to the appropriate builder function
            if frame_name == "Home":
                self.setup_home_view(frame)
            elif frame_name == "Analytics":
                self.setup_analytics_view(frame)
            elif frame_name == "Settings":
                self.setup_settings_view(frame)
            elif frame_name == "Workspace":
                self.setup_dynamic_workspace(frame)

    # ------------------ FRAME BUILDERS ------------------
    def setup_home_view(self, frame):
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Greeting
        greeting = self.get_greeting()
        title = ctk.CTkLabel(frame, text=f"{greeting}, {self.username}!", font=ctk.CTkFont(size=28, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 5), columnspan=3, sticky="w")
        
        sub_title = ctk.CTkLabel(frame, text=f"📍 {self.config['title']} Operations Center", font=ctk.CTkFont(size=16), text_color="gray")
        sub_title.grid(row=1, column=0, padx=20, pady=(0, 20), columnspan=3, sticky="w")

        # Dynamic Cards populated from the Config Dictionary
        for i, (head, val, sub) in enumerate(self.config["home_cards"]):
            card = ctk.CTkFrame(frame, corner_radius=12, border_width=1)
            card.grid(row=2, column=i, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(card, text=head, font=ctk.CTkFont(size=14, weight="bold"), text_color="#3b8ed0").grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
            ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=32, weight="bold")).grid(row=1, column=0, padx=15, pady=5, sticky="w")
            ctk.CTkLabel(card, text=sub, font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=15, pady=(5, 15), sticky="w")

        # Quick Actions Strip below the cards
        ctk.CTkLabel(frame, text="Quick Actions", font=ctk.CTkFont(size=18, weight="bold")).grid(row=3, column=0, padx=20, pady=(30, 10), sticky="w")
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=3, padx=20, sticky="ew")
        ctk.CTkButton(btn_frame, text="Generate Report", width=150, fg_color="#003F6F").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Request Support", width=150, fg_color="#2BA9B2").pack(side="left")


    def setup_analytics_view(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(frame, text=f"{self.department} Real-Time Feed", font=ctk.CTkFont(size=26, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        data_display = ctk.CTkTextbox(frame, height=450, font=("Courier", 12))
        data_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Populate text box dynamically based on config feed
        logs = "\n\n".join([self.config["log_feed"].format(id=1000+x) for x in range(15)])
        data_display.insert("0.0", f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SECURE CONNECTION ESTABLISHED]\n\n{logs}")
        data_display.configure(state="disabled")


    def setup_dynamic_workspace(self, frame):
        """This function completely changes the interface layout based on the department!"""
        frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(frame, text=f"{self.department} Integrated Tools", font=ctk.CTkFont(size=26, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        tool_frame = ctk.CTkFrame(frame, corner_radius=15)
        tool_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # --- IT WORKSPACE (System Toggles & Terminal) ---
        if self.department == "IT":
            ctk.CTkLabel(tool_frame, text="System Parameter Controls", font=ctk.CTkFont(weight="bold")).pack(pady=20)
            ctk.CTkSwitch(tool_frame, text="Enable Backup Node Clustering").pack(pady=10, anchor="w", padx=50)
            ctk.CTkSwitch(tool_frame, text="Restrict Outbound SMTP Traffic").pack(pady=10, anchor="w", padx=50)
            ctk.CTkSwitch(tool_frame, text="Force Secure SSH Connections", border_color="red").pack(pady=10, anchor="w", padx=50)
            ctk.CTkButton(tool_frame, text="Flush System Cache", fg_color="#dc2626", hover_color="#b91c1c").pack(pady=30)
            
        # --- HR WORKSPACE (Recruitment Pipeline) ---
        elif self.department == "HR":
            ctk.CTkLabel(tool_frame, text="Active Recruitment Pipeline", font=ctk.CTkFont(weight="bold")).pack(pady=20)
            for role, status in [("Sr. Data Scientist", "Interviewing (3)"), ("Frontend Developer", "Sourcing"), ("Accountant", "Offer Extended")]:
                row = ctk.CTkFrame(tool_frame, fg_color="transparent")
                row.pack(fill="x", padx=40, pady=5)
                ctk.CTkLabel(row, text=f"📌 {role}", font=ctk.CTkFont(size=14)).pack(side="left")
                ctk.CTkButton(row, text=status, width=120, fg_color="#2b2b2b").pack(side="right")
            ctk.CTkButton(tool_frame, text="Create New Job Posting", fg_color="#2BA9B2").pack(pady=40)
            
        # --- ACCOUNTS WORKSPACE (Calculations & Invoicing) ---
        elif self.department == "ACCOUNTS":
            ctk.CTkLabel(tool_frame, text="Quick Invoice Generation", font=ctk.CTkFont(weight="bold")).pack(pady=20)
            ctk.CTkEntry(tool_frame, placeholder_text="Client Name", width=300).pack(pady=10)
            ctk.CTkEntry(tool_frame, placeholder_text="Amount ($)", width=300).pack(pady=10)
            ctk.CTkEntry(tool_frame, placeholder_text="Tax Rate (%)", width=300).pack(pady=10)
            ctk.CTkButton(tool_frame, text="Calculate & Generate PDF", fg_color="#003F6F").pack(pady=20)
            
        # --- MANAGEMENT WORKSPACE (Approvals) ---
        elif self.department == "MANAGEMENT":
            ctk.CTkLabel(tool_frame, text="Pending Executive Approvals", font=ctk.CTkFont(weight="bold")).pack(pady=20)
            for req, amt in [("Q3 Marketing Budget", "$45,000"), ("New IT Hardware", "$12,400"), ("Vendor Contract Renewal", "$110,000")]:
                row = ctk.CTkFrame(tool_frame, fg_color="transparent")
                row.pack(fill="x", padx=40, pady=10)
                ctk.CTkLabel(row, text=f"📄 {req} ({amt})", font=ctk.CTkFont(size=14)).pack(side="left")
                ctk.CTkButton(row, text="Reject", width=80, fg_color="#dc2626").pack(side="right", padx=5)
                ctk.CTkButton(row, text="Approve", width=80, fg_color="green").pack(side="right", padx=5)

        # --- SALES WORKSPACE ---
        elif self.department == "SALES":
            ctk.CTkLabel(tool_frame, text="Lead Management Entry", font=ctk.CTkFont(weight="bold")).pack(pady=20)
            ctk.CTkEntry(tool_frame, placeholder_text="Client Company", width=300).pack(pady=10)
            ctk.CTkEntry(tool_frame, placeholder_text="Estimated Deal Size ($)", width=300).pack(pady=10)
            ctk.CTkOptionMenu(tool_frame, values=["Cold Call", "Follow-up", "Negotiation", "Closed"]).pack(pady=10)
            ctk.CTkButton(tool_frame, text="Add to Pipeline", fg_color="#129A61").pack(pady=20)


    def setup_settings_view(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        title = ctk.CTkLabel(frame, text="Security & Preferences", font=ctk.CTkFont(size=26, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        chk_1 = ctk.CTkCheckBox(frame, text="Enable Email Notifications for Department Updates")
        chk_1.grid(row=1, column=0, padx=30, pady=15, sticky="w")
        chk_1.select()
        
        chk_2 = ctk.CTkCheckBox(frame, text="Two-Factor Authentication (2FA) Enforced")
        chk_2.grid(row=2, column=0, padx=30, pady=15, sticky="w")
        chk_2.select()
        chk_2.configure(state="disabled") # Enforced by system

        btn_save = ctk.CTkButton(frame, text="Save Configurations", width=200)
        btn_save.grid(row=3, column=0, padx=30, pady=30, sticky="w")

    # ------------------ UTILITY METHODS ------------------
    def select_frame(self, name):
        """Switches visible modules and manages button highlight state."""
        for btn_name, btn_obj in self.nav_buttons.items():
            btn_obj.configure(fg_color="transparent")

        if name in self.nav_buttons:
            self.nav_buttons[name].configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

        for f in self.frames.values():
            f.grid_forget()

        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        
    def get_greeting(self):
        hour = datetime.now().hour
        if hour < 12: return "Good Morning"
        elif 12 <= hour < 17: return "Good Afternoon"
        else: return "Good Evening"
        
    def on_closing(self):
        """Logs the logout event and restores the main window."""
        try:
            log_activity(
                self.user_info.get('user_id', 'Unknown'),
                self.user_info.get('Name', 'User'),
                self.user_info.get('Department', 'GENERAL'),
                self.user_info.get('Contact', 'N/A'),
                "Logout"
            )
        except Exception as e:
            print(f"Failed to log logout activity: {e}")
            
        if self.master:
            self.master.deiconify() 
        self.destroy()