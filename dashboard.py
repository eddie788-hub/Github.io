# A+ Electric & Air Business Management Dashboard
# Company: A+ Electric & Air | Phone: 318-307-7349
# Uses SQLite database for data storage

import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import platform
import webbrowser

class BusinessDashboard:
    def __init__(self, app_root):
        self.root = app_root
        self.root.title("A+ Electric & Air - Business Management System")
        self.root.geometry("1980x800")
        
    
        # Company Information
        self.company_name = "A+ Electric & Air"
        self.company_phone = "318-307-7349"
        self.company_email = "info@apluselectricair.com"
        
        # Initialize database
        self.init_database()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create all tabs
        self.create_dashboard_tab()
        self.create_client_tab()
        self.create_employee_tab()
        self.create_work_order_tab()
        self.create_invoice_tab()
        self.create_calls_tab()
        self.create_reports_tab()
        
        # Auto-refresh every 30 seconds
        self.auto_refresh()
        
        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self.save_and_exit)
    
    def init_database(self):
        """Initialize SQLite database with all tables"""
        self.conn = sqlite3.connect('aplus_business.db')
        self.cursor = self.conn.cursor()
        
        # Clients table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                client_type TEXT,
                notes TEXT,
                created_date TEXT,
                last_contact TEXT,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Employees table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT,
                hourly_rate REAL,
                phone TEXT,
                email TEXT,
                hire_date TEXT,
                skills TEXT,
                active INTEGER DEFAULT 1,
                hours_ytd REAL DEFAULT 0,
                emergency_contact TEXT,
                emergency_phone TEXT
            )
        ''')
        
        # Work orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wo_number TEXT UNIQUE,
                title TEXT NOT NULL,
                client_id INTEGER,
                job_type TEXT,
                assigned_to INTEGER,
                status TEXT,
                priority TEXT,
                scheduled_date TEXT,
                completed_date TEXT,
                estimated_hours REAL,
                actual_hours REAL DEFAULT 0,
                labor_cost REAL DEFAULT 0,
                materials_cost REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                description TEXT,
                special_instructions TEXT,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (client_id) REFERENCES clients(id),
                FOREIGN KEY (assigned_to) REFERENCES employees(id)
            )
        ''')
        
        # Invoices table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_order_id INTEGER,
                client_id INTEGER,
                invoice_number TEXT UNIQUE,
                subtotal REAL,
                tax_rate REAL DEFAULT 0.09,
                tax_amount REAL,
                total_amount REAL,
                status TEXT,
                issue_date TEXT,
                due_date TEXT,
                paid_date TEXT,
                payment_method TEXT,
                notes TEXT,
                FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        ''')
        
        # Service calls table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                work_order_id INTEGER,
                issue TEXT,
                status TEXT,
                priority TEXT,
                call_date TEXT,
                scheduled_date TEXT,
                resolved_date TEXT,
                notes TEXT,
                call_duration INTEGER,
                call_back_needed INTEGER DEFAULT 0,
                FOREIGN KEY (client_id) REFERENCES clients(id),
                FOREIGN KEY (work_order_id) REFERENCES work_orders(id)
            )
        ''')
        
        self.conn.commit()
        
        # Insert sample data if tables are empty
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insert sample data if tables are empty"""
        # Check if clients exist
        self.cursor.execute("SELECT COUNT(*) FROM clients")
        if self.cursor.fetchone()[0] == 0:
            # Sample clients
            sample_clients = [
                ("ABC Corporation", "318-555-0101", "contact@abccorp.com", "123 Business Ave", "Shreveport", "LA", "71101", "Commercial", "Regular HVAC maintenance client", datetime.now().strftime("%Y-%m-%d"), "", 1),
                ("XYZ Services", "318-555-0102", "info@xyzservices.com", "456 Industrial Park", "Bossier City", "LA", "71111", "Commercial", "Electrical panel upgrades", datetime.now().strftime("%Y-%m-%d"), "", 1),
                ("Johnson Residence", "318-555-0103", "johnson@email.com", "789 Oak Street", "Shreveport", "LA", "71105", "Residential", "Homeowner - AC replacement", datetime.now().strftime("%Y-%m-%d"), "", 1),
                ("Smith Properties", "318-555-0104", "smith@property.com", "321 Maple Drive", "Bossier City", "LA", "71112", "Property Management", "Multiple rental properties", datetime.now().strftime("%Y-%m-%d"), "", 1),
                ("Green Energy Solutions", "318-555-0105", "green@energy.com", "654 Solar Way", "Shreveport", "LA", "71108", "Commercial", "Solar panel installations", datetime.now().strftime("%Y-%m-%d"), "", 1),
            ]
            self.cursor.executemany('''INSERT INTO clients 
                (name, phone, email, address, city, state, zip_code, client_type, notes, created_date, last_contact, active) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', sample_clients)
            
            # Sample employees
            sample_employees = [
                ("John Smith", "Senior Electrician", 55, "318-555-0201", "john@apluselectric.com", "2023-01-15", "Electrical,Panel Upgrades,Lighting", 1, 320, "Jane Smith", "318-555-0301"),
                ("Mike Johnson", "HVAC Technician", 50, "318-555-0202", "mike@apluselectric.com", "2023-02-01", "HVAC,AC Repair,Installation", 1, 280, "Sarah Johnson", "318-555-0302"),
                ("Sarah Williams", "Office Manager", 35, "318-555-0203", "sarah@apluselectric.com", "2023-01-10", "Administration,Scheduling,Billing", 1, 180, "Tom Williams", "318-555-0303"),
                ("Robert Chen", "Apprentice Electrician", 35, "318-555-0204", "robert@apluselectric.com", "2023-06-01", "Electrical,Helper", 1, 120, "Lisa Chen", "318-555-0304"),
                ("David Miller", "HVAC Specialist", 60, "318-555-0205", "david@apluselectric.com", "2023-03-15", "HVAC,Commercial Systems,Boilers", 1, 310, "Emma Miller", "318-555-0305"),
            ]
            self.cursor.executemany('''INSERT INTO employees 
                (name, role, hourly_rate, phone, email, hire_date, skills, active, hours_ytd, emergency_contact, emergency_phone) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?)''', sample_employees)
            
            # Get client and employee IDs
            self.cursor.execute("SELECT id FROM clients")
            client_ids = [row[0] for row in self.cursor.fetchall()]
            self.cursor.execute("SELECT id FROM employees")
            employee_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Sample work orders
            sample_work_orders = [
                ("WO-2024-001", "AC Installation - ABC Corp", client_ids[0], "HVAC", employee_ids[1], "In Progress", "High", 
                 datetime.now().strftime("%Y-%m-%d"), "", 8, 4, 320, 1200, 1520, "Install new commercial AC unit", "Need crane for rooftop unit", 0),
                ("WO-2024-002", "Panel Upgrade - XYZ Services", client_ids[1], "Electrical", employee_ids[0], "Scheduled", "Medium",
                 (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), "", 6, 0, 0, 800, 800, "Upgrade to 200A panel", "Permit required", 0),
                ("WO-2024-003", "Maintenance Check - Johnson", client_ids[2], "HVAC", employee_ids[4], "Completed", "Low",
                 (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"), 2, 2, 150, 50, 200, "Routine maintenance and filter change", "Customer satisfied", 1),
                ("WO-2024-004", "Solar Panel Installation", client_ids[4], "Electrical", employee_ids[0], "Scheduled", "High",
                 (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), "", 16, 0, 0, 5000, 5000, "Install 5kW solar system", "Requires roof inspection", 0),
            ]
            self.cursor.executemany('''INSERT INTO work_orders 
                (wo_number, title, client_id, job_type, assigned_to, status, priority, scheduled_date, completed_date, 
                 estimated_hours, actual_hours, labor_cost, materials_cost, total_cost, description, special_instructions, completed) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', sample_work_orders)
            
            # Sample invoices
            sample_invoices = [
                (1, client_ids[0], "INV-2024-001", 1520, 0.09, 136.80, 1656.80, "Paid", "2024-01-15", "2024-02-14", "2024-01-20", "Credit Card", "AC Installation"),
                (2, client_ids[1], "INV-2024-002", 800, 0.09, 72.00, 872.00, "Pending", "2024-01-20", "2024-02-19", "", "", "Panel Upgrade - awaiting payment"),
                (3, client_ids[2], "INV-2024-003", 200, 0.09, 18.00, 218.00, "Paid", "2024-01-18", "2024-02-17", "2024-01-19", "Cash", "Maintenance service"),
            ]
            self.cursor.executemany('''INSERT INTO invoices 
                (work_order_id, client_id, invoice_number, subtotal, tax_rate, tax_amount, total_amount, 
                 status, issue_date, due_date, paid_date, payment_method, notes) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', sample_invoices)
            
            self.conn.commit()
    
    def save_and_exit(self):
        """Save and close application"""
        self.conn.close()
        self.root.destroy()
    
    def auto_refresh(self):
        """Auto-refresh dashboard every 30 seconds"""
        self.update_dashboard()
        self.root.after(30000, self.auto_refresh)
    
    def get_next_wo_number(self):
        """Generate next work order number"""
        self.cursor.execute("SELECT MAX(wo_number) FROM work_orders")
        last_wo = self.cursor.fetchone()[0]
        if last_wo:
            try:
                num = int(last_wo.split('-')[2]) + 1
                return f"WO-2024-{num:03d}"
            except:
                return "WO-2024-001"
        return "WO-2024-001"
    
    def get_next_invoice_number(self):
        """Generate next invoice number"""
        self.cursor.execute("SELECT MAX(invoice_number) FROM invoices")
        last_inv = self.cursor.fetchone()[0]
        if last_inv:
            try:
                num = int(last_inv.split('-')[2]) + 1
                return f"INV-2024-{num:03d}"
            except:
                return "INV-2024-001"
        return "INV-2024-001"
    
    def get_client_name(self, client_id):
        """Get client name by ID"""
        self.cursor.execute("SELECT name FROM clients WHERE id=?", (client_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "Unknown"
    
    def get_employee_name(self, employee_id):
        """Get employee name by ID"""
        self.cursor.execute("SELECT name FROM employees WHERE id=?", (employee_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "Unassigned"
    
    # ============= DASHBOARD TAB =============
    def create_dashboard_tab(self):
        """Create overview dashboard"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Dashboard")
        
        # Company Header
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill='x', pady=10)
        
        company_title = ttk.Label(header_frame, text=self.company_name, font=('Arial', 24, 'bold'))
        company_title.pack()
        
        company_phone_label = ttk.Label(header_frame, text=f"📞 {self.company_phone}", font=('Arial', 12))
        company_phone_label.pack()
        
        # Stats frames
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(pady=20)
        
        # Client stats
        client_frame = ttk.LabelFrame(stats_frame, text="👥 Clients", padding=15, width=200)
        client_frame.grid(row=0, column=0, padx=10, pady=10)
        client_frame.grid_propagate(False)
        self.dash_client_count = ttk.Label(client_frame, text="", font=('Arial', 14, 'bold'))
        self.dash_client_count.pack()
        self.dash_active_clients = ttk.Label(client_frame, text="", font=('Arial', 14))
        self.dash_active_clients.pack()
        
        # Employee stats
        emp_frame = ttk.LabelFrame(stats_frame, text="👷 Employees", padding=15, width=200)
        emp_frame.grid(row=0, column=1, padx=10, pady=10)
        emp_frame.grid_propagate(False)
        self.dash_emp_count = ttk.Label(emp_frame, text="", font=('Arial', 14, 'bold'))
        self.dash_emp_count.pack()
        self.dash_active_emp = ttk.Label(emp_frame, text="", font=('Arial', 14))
        self.dash_active_emp.pack()
        
        # Work order stats
        wo_frame = ttk.LabelFrame(stats_frame, text="🔧 Work Orders", padding=15, width=200)
        wo_frame.grid(row=0, column=2, padx=10, pady=10)
        wo_frame.grid_propagate(False)
        self.dash_wo_total = ttk.Label(wo_frame, text="", font=('Arial', 14, 'bold'))
        self.dash_wo_total.pack()
        self.dash_wo_active = ttk.Label(wo_frame, text="", font=('Arial', 14))
        self.dash_wo_active.pack()
        
        # Revenue stats
        revenue_frame = ttk.LabelFrame(stats_frame, text="💰 Revenue", padding=15, width=200)
        revenue_frame.grid(row=1, column=0, padx=10, pady=10)
        revenue_frame.grid_propagate(False)
        self.dash_revenue_month = ttk.Label(revenue_frame, text="", font=('Arial', 12))
        self.dash_revenue_month.pack()
        self.dash_revenue_year = ttk.Label(revenue_frame, text="", font=('Arial', 12))
        self.dash_revenue_year.pack()
        
        # Service calls stats
        calls_frame = ttk.LabelFrame(stats_frame, text="📞 Service Calls", padding=15, width=200)
        calls_frame.grid(row=1, column=1, padx=10, pady=10)
        calls_frame.grid_propagate(False)
        self.dash_calls_active = ttk.Label(calls_frame, text="", font=('Arial', 12))
        self.dash_calls_active.pack()
        self.dash_calls_resolved = ttk.Label(calls_frame, text="", font=('Arial', 12))
        self.dash_calls_resolved.pack()
        
        # Quick actions
        actions_frame = ttk.LabelFrame(stats_frame, text="⚡ Quick Actions", padding=15, width=200)
        actions_frame.grid(row=1, column=2, padx=10, pady=10)
        actions_frame.grid_propagate(False)
        
        ttk.Button(actions_frame, text="New Work Order", command=lambda: self.notebook.select(3)).pack(pady=5)
        ttk.Button(actions_frame, text="New Invoice", command=lambda: self.notebook.select(4)).pack(pady=5)
        ttk.Button(actions_frame, text="Log Service Call", command=lambda: self.notebook.select(5)).pack(pady=5)
        ttk.Button(actions_frame, text="Add Client", command=lambda: self.notebook.select(1)).pack(pady=5)
        
        # Recent activity
        recent_frame = ttk.LabelFrame(tab, text="Recent Activity", padding=10)
        recent_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.recent_text = scrolledtext.ScrolledText(recent_frame, height=12, width=100, font=('Courier', 9))
        self.recent_text.pack(fill='both', expand=True)
        
        # Refresh button
        ttk.Button(tab, text="⟳ Refresh Dashboard", command=self.update_dashboard).pack(pady=10)
        
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update dashboard statistics"""
        # Client stats
        self.cursor.execute("SELECT COUNT(*), SUM(CASE WHEN active=1 THEN 1 ELSE 0 END) FROM clients")
        total_clients, active_clients = self.cursor.fetchone()
        self.dash_client_count.config(text=str(total_clients))
        self.dash_active_clients.config(text=f"Active: {active_clients or 0}")
        
        # Employee stats
        self.cursor.execute("SELECT COUNT(*), SUM(CASE WHEN active=1 THEN 1 ELSE 0 END) FROM employees")
        total_emp, active_emp = self.cursor.fetchone()
        self.dash_emp_count.config(text=str(total_emp))
        self.dash_active_emp.config(text=f"Active: {active_emp or 0}")
        
        # Work order stats
        self.cursor.execute("SELECT COUNT(*), SUM(CASE WHEN completed=0 THEN 1 ELSE 0 END) FROM work_orders")
        total_wo, active_wo = self.cursor.fetchone()
        self.dash_wo_total.config(text=str(total_wo))
        self.dash_wo_active.config(text=f"Active: {active_wo or 0}")
        
        # Revenue stats
        current_month = datetime.now().strftime("%Y-%m")
        self.cursor.execute(f"SELECT SUM(total_amount) FROM invoices WHERE status='Paid' AND strftime('%Y-%m', paid_date)='{current_month}'")
        month_revenue = self.cursor.fetchone()[0] or 0
        self.cursor.execute("SELECT SUM(total_amount) FROM invoices WHERE status='Paid' AND strftime('%Y', paid_date)=strftime('%Y', 'now')")
        year_revenue = self.cursor.fetchone()[0] or 0
        self.dash_revenue_month.config(text=f"This Month: ${month_revenue:,.2f}")
        self.dash_revenue_year.config(text=f"This Year: ${year_revenue:,.2f}")
        
        # Service calls
        self.cursor.execute("SELECT SUM(CASE WHEN status NOT IN ('Resolved','Closed') THEN 1 ELSE 0 END), COUNT(*) FROM service_calls")
        active_calls, total_calls = self.cursor.fetchone()
        self.dash_calls_active.config(text=f"Active: {active_calls or 0}")
        self.dash_calls_resolved.config(text=f"Total: {total_calls or 0}")
        
        # Recent activity
        self.recent_text.delete(1.0, tk.END)
        self.recent_text.insert(tk.END, "="*80 + "\n")
        self.recent_text.insert(tk.END, f"{self.company_name} - RECENT ACTIVITY\n")
        self.recent_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.recent_text.insert(tk.END, "="*80 + "\n\n")
        
        # Get recent work orders
        self.recent_text.insert(tk.END, "📋 RECENT WORK ORDERS:\n")
        self.recent_text.insert(tk.END, "-"*60 + "\n")
        self.cursor.execute("SELECT wo_number, title, status, scheduled_date FROM work_orders ORDER BY scheduled_date DESC LIMIT 5")
        for wo in self.cursor.fetchall():
            self.recent_text.insert(tk.END, f"  {wo[0]}: {wo[1][:40]} - {wo[2]} - {wo[3]}\n")
        
        # Get recent invoices
        self.recent_text.insert(tk.END, "\n💰 RECENT INVOICES:\n")
        self.recent_text.insert(tk.END, "-"*60 + "\n")
        self.cursor.execute("SELECT invoice_number, total_amount, status, issue_date FROM invoices ORDER BY issue_date DESC LIMIT 5")
        for inv in self.cursor.fetchall():
            self.recent_text.insert(tk.END, f"  {inv[0]}: ${inv[1]:,.2f} - {inv[2]} - {inv[3]}\n")
        
        # Get recent service calls
        self.recent_text.insert(tk.END, "\n📞 RECENT SERVICE CALLS:\n")
        self.recent_text.insert(tk.END, "-"*60 + "\n")
        self.cursor.execute("SELECT issue, status, priority, call_date FROM service_calls ORDER BY call_date DESC LIMIT 5")
        for call in self.cursor.fetchall():
            self.recent_text.insert(tk.END, f"  {call[0][:40]} - {call[1]} - Priority: {call[2]} - {call[3]}\n")
    
    # ============= CLIENT TAB =============
    def create_client_tab(self):
        """Create client management tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 Clients")
        
        # Top frame
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(top_frame, text="🔍 Search:").pack(side='left', padx=5)
        self.client_search = ttk.Entry(top_frame, width=30)
        self.client_search.pack(side='left', padx=5)
        self.client_search.bind('<KeyRelease>', lambda e: self.refresh_client_list())
        
        ttk.Label(top_frame, text="Filter:").pack(side='left', padx=5)
        self.client_type_filter = ttk.Combobox(top_frame, values=['All', 'Residential', 'Commercial', 'Property Management'], width=18)
        self.client_type_filter.set('All')
        self.client_type_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_client_list())
        self.client_type_filter.pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="Export Clients", command=self.export_clients).pack(side='right', padx=5)
        
        # Main container
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Client list
        list_frame = ttk.LabelFrame(main_frame, text="Client Directory", padding=10)
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        columns = ('ID', 'Name', 'Phone', 'Email', 'Type', 'Status', 'Last Contact')
        self.client_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18)
        
        for col in columns:
            self.client_tree.heading(col, text=col)
            widths = {'ID': 50, 'Name': 150, 'Phone': 110, 'Email': 150, 'Type': 100, 'Status': 80, 'Last Contact': 100}
            self.client_tree.column(col, width=widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.client_tree.yview)
        self.client_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.client_tree.pack(side='left', fill='both', expand=True)
        
        self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)
        
        # Client form
        form_frame = ttk.LabelFrame(main_frame, text="Client Information", padding=10)
        form_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Basic info
        ttk.Label(form_frame, text="Name:*").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.client_name = ttk.Entry(form_frame, width=30)
        self.client_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.client_phone = ttk.Entry(form_frame, width=30)
        self.client_phone.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="📞 Call", command=self.call_client).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.client_email = ttk.Entry(form_frame, width=30)
        self.client_email.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Address:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.client_address = ttk.Entry(form_frame, width=30)
        self.client_address.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="City:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.client_city = ttk.Entry(form_frame, width=20)
        self.client_city.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="State:").grid(row=4, column=2, sticky='w', padx=5, pady=5)
        self.client_state = ttk.Entry(form_frame, width=5)
        self.client_state.grid(row=4, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="ZIP:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        self.client_zip = ttk.Entry(form_frame, width=10)
        self.client_zip.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Type:").grid(row=6, column=0, sticky='w', padx=5, pady=5)
        self.client_type = ttk.Combobox(form_frame, values=['Residential', 'Commercial', 'Property Management'], width=20)
        self.client_type.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Status:").grid(row=7, column=0, sticky='w', padx=5, pady=5)
        self.client_status = ttk.Combobox(form_frame, values=['Active', 'Inactive'], width=20)
        self.client_status.set('Active')
        self.client_status.grid(row=7, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Notes:").grid(row=8, column=0, sticky='nw', padx=5, pady=5)
        self.client_notes = tk.Text(form_frame, height=5, width=40)
        self.client_notes.grid(row=8, column=1, columnspan=2, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Client", command=self.add_client).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Update Client", command=self.update_client).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete Client", command=self.delete_client).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Clear Form", command=self.clear_client_form).pack(side='left', padx=5)
        
        self.refresh_client_list()
    
    def refresh_client_list(self):
        """Refresh client treeview"""
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        search_term = self.client_search.get()
        client_type = self.client_type_filter.get()
        
        query = "SELECT id, name, phone, email, client_type, active, last_contact FROM clients WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        if client_type != 'All':
            query += " AND client_type = ?"
            params.append(client_type)
        
        query += " ORDER BY name"
        
        self.cursor.execute(query, params)
        for client in self.cursor.fetchall():
            status = "✓ Active" if client[5] else "✗ Inactive"
            last_contact = client[6] if client[6] else "Never"
            self.client_tree.insert('', 'end', values=(client[0], client[1], client[2], client[3], client[4], status, last_contact))
    
    def on_client_select(self, event):
        """Handle client selection"""
        selected = self.client_tree.selection()
        if not selected:
            return
        
        item = self.client_tree.item(selected[0])
        client_id = item['values'][0]
        
        self.cursor.execute("SELECT * FROM clients WHERE id=?", (client_id,))
        client = self.cursor.fetchone()
        
        if client:
            self.client_name.delete(0, tk.END)
            self.client_name.insert(0, client[1])
            self.client_phone.delete(0, tk.END)
            self.client_phone.insert(0, client[2] or '')
            self.client_email.delete(0, tk.END)
            self.client_email.insert(0, client[3] or '')
            self.client_address.delete(0, tk.END)
            self.client_address.insert(0, client[4] or '')
            self.client_city.delete(0, tk.END)
            self.client_city.insert(0, client[5] or '')
            self.client_state.delete(0, tk.END)
            self.client_state.insert(0, client[6] or '')
            self.client_zip.delete(0, tk.END)
            self.client_zip.insert(0, client[7] or '')
            self.client_type.set(client[8] or '')
            self.client_notes.delete(1.0, tk.END)
            self.client_notes.insert(1.0, client[9] or '')
            self.client_status.set('Active' if client[12] else 'Inactive')
    
    def add_client(self):
        """Add new client"""
        name = self.client_name.get()
        if not name:
            messagebox.showwarning("Warning", "Client name is required")
            return
        
        phone = self.client_phone.get()
        email = self.client_email.get()
        address = self.client_address.get()
        city = self.client_city.get()
        state = self.client_state.get()
        zip_code = self.client_zip.get()
        client_type = self.client_type.get()
        notes = self.client_notes.get(1.0, tk.END).strip()
        active = 1 if self.client_status.get() == 'Active' else 0
        created_date = datetime.now().strftime("%Y-%m-%d")
        
        self.cursor.execute('''INSERT INTO clients 
            (name, phone, email, address, city, state, zip_code, client_type, notes, created_date, active) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (name, phone, email, address, city, state, zip_code, client_type, notes, created_date, active))
        
        self.conn.commit()
        self.clear_client_form()
        self.refresh_client_list()
        messagebox.showinfo("Success", f"Client {name} added")
    
    def update_client(self):
        """Update selected client"""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a client")
            return
        
        item = self.client_tree.item(selected[0])
        client_id = item['values'][0]
        
        name = self.client_name.get()
        if not name:
            messagebox.showwarning("Warning", "Client name is required")
            return
        
        phone = self.client_phone.get()
        email = self.client_email.get()
        address = self.client_address.get()
        city = self.client_city.get()
        state = self.client_state.get()
        zip_code = self.client_zip.get()
        client_type = self.client_type.get()
        notes = self.client_notes.get(1.0, tk.END).strip()
        active = 1 if self.client_status.get() == 'Active' else 0
        
        self.cursor.execute('''UPDATE clients SET 
            name=?, phone=?, email=?, address=?, city=?, state=?, zip_code=?, client_type=?, notes=?, active=?, last_contact=?
            WHERE id=?''',
            (name, phone, email, address, city, state, zip_code, client_type, notes, active, datetime.now().strftime("%Y-%m-%d"), client_id))
        
        self.conn.commit()
        self.refresh_client_list()
        messagebox.showinfo("Success", "Client updated")
    
    def delete_client(self):
        """Delete selected client"""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a client")
            return
        
        item = self.client_tree.item(selected[0])
        client_name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete client '{client_name}'?"):
            client_id = item['values'][0]
            self.cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
            self.conn.commit()
            self.clear_client_form()
            self.refresh_client_list()
            messagebox.showinfo("Success", "Client deleted")
    
    def clear_client_form(self):
        """Clear client form"""
        self.client_name.delete(0, tk.END)
        self.client_phone.delete(0, tk.END)
        self.client_email.delete(0, tk.END)
        self.client_address.delete(0, tk.END)
        self.client_city.delete(0, tk.END)
        self.client_state.delete(0, tk.END)
        self.client_zip.delete(0, tk.END)
        self.client_type.set('')
        self.client_notes.delete(1.0, tk.END)
        self.client_status.set('Active')
    
    def call_client(self):
        """Open phone app to call client"""
        phone = self.client_phone.get()
        if not phone:
            messagebox.showwarning("Warning", "No phone number for this client")
            return
        
        if messagebox.askyesno("Call Client", f"Call {phone}?"):
            try:
                if platform.system() == 'Windows':
                    webbrowser.open('https://www.textnow.com/messaging')
                    messagebox.showinfo("Info", f"Opening TextNow to call {phone}")
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', f'tel://{phone}'])
                else:
                    subprocess.run(['xdg-open', f'tel://{phone}'])
            except:
                messagebox.showinfo("Info", f"Please call {phone} using your phone")
    
    def export_clients(self):
        """Export clients to CSV"""
        try:
            import csv
            filename = f"clients_export_{datetime.now().strftime('%Y%m%d')}.csv"
            self.cursor.execute("SELECT * FROM clients")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([description[0] for description in self.cursor.description])
                writer.writerows(self.cursor.fetchall())
            messagebox.showinfo("Success", f"Clients exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    # ============= EMPLOYEE TAB =============
    def create_employee_tab(self):
        """Create employee tracking tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👷 Employees")
        
        # Employee list
        list_frame = ttk.LabelFrame(tab, text="Employee Roster", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Name', 'Role', 'Rate', 'Phone', 'Hours YTD', 'Status')
        self.employee_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.employee_tree.heading(col, text=col)
            widths = {'ID': 50, 'Name': 120, 'Role': 120, 'Rate': 80, 'Phone': 110, 'Hours YTD': 80, 'Status': 80}
            self.employee_tree.column(col, width=widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.employee_tree.pack(side='left', fill='both', expand=True)
        
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)
        
        # Employee form
        form_frame = ttk.LabelFrame(tab, text="Employee Management", padding=10)
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Left column
        left_col = ttk.Frame(form_frame)
        left_col.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(left_col, text="Name:*").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.emp_name = ttk.Entry(left_col, width=25)
        self.emp_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(left_col, text="Role:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.emp_role = ttk.Combobox(left_col, values=['Electrician', 'HVAC Tech', 'Apprentice', 'Senior Electrician', 'HVAC Specialist', 'Office Manager'], width=23)
        self.emp_role.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(left_col, text="Hourly Rate ($):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.emp_rate = ttk.Entry(left_col, width=25)
        self.emp_rate.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(left_col, text="Phone:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.emp_phone = ttk.Entry(left_col, width=25)
        self.emp_phone.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(left_col, text="Email:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.emp_email = ttk.Entry(left_col, width=25)
        self.emp_email.grid(row=4, column=1, padx=5, pady=5)
        
        # Right column
        right_col = ttk.Frame(form_frame)
        right_col.pack(side='right', fill='both', expand=True, padx=5)
        
        ttk.Label(right_col, text="Skills:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.emp_skills = ttk.Entry(right_col, width=30)
        self.emp_skills.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(right_col, text="Emergency Contact:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.emp_emergency = ttk.Entry(right_col, width=30)
        self.emp_emergency.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(right_col, text="Emergency Phone:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.emp_emergency_phone = ttk.Entry(right_col, width=30)
        self.emp_emergency_phone.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(right_col, text="Status:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.emp_status = ttk.Combobox(right_col, values=['Active', 'Inactive'], width=28)
        self.emp_status.set('Active')
        self.emp_status.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(side='bottom', fill='x', pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Employee", command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Update Employee", command=self.update_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete Employee", command=self.delete_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Clear Form", command=self.clear_employee_form).pack(side='left', padx=5)
        
        self.refresh_employee_list()
    
    def refresh_employee_list(self):
        """Refresh employee treeview"""
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        self.cursor.execute("SELECT id, name, role, hourly_rate, phone, hours_ytd, active FROM employees ORDER BY name")
        for emp in self.cursor.fetchall():
            status = "✓ Active" if emp[6] else "✗ Inactive"
            self.employee_tree.insert('', 'end', values=(emp[0], emp[1], emp[2], f"${emp[3]:.2f}", emp[4], f"{emp[5]:.1f}", status))
    
    def on_employee_select(self, event):
        """Handle employee selection"""
        selected = self.employee_tree.selection()
        if not selected:
            return
        
        item = self.employee_tree.item(selected[0])
        emp_id = item['values'][0]
        
        self.cursor.execute("SELECT * FROM employees WHERE id=?", (emp_id,))
        emp = self.cursor.fetchone()
        
        if emp:
            self.emp_name.delete(0, tk.END)
            self.emp_name.insert(0, emp[1])
            self.emp_role.set(emp[2] or '')
            self.emp_rate.delete(0, tk.END)
            self.emp_rate.insert(0, str(emp[3]) if emp[3] else '')
            self.emp_phone.delete(0, tk.END)
            self.emp_phone.insert(0, emp[4] or '')
            self.emp_email.delete(0, tk.END)
            self.emp_email.insert(0, emp[5] or '')
            self.emp_skills.delete(0, tk.END)
            self.emp_skills.insert(0, emp[7] or '')
            self.emp_emergency.delete(0, tk.END)
            self.emp_emergency.insert(0, emp[10] or '')
            self.emp_emergency_phone.delete(0, tk.END)
            self.emp_emergency_phone.insert(0, emp[11] or '')
            self.emp_status.set('Active' if emp[8] else 'Inactive')
    
    def add_employee(self):
        """Add new employee"""
        name = self.emp_name.get()
        if not name:
            messagebox.showwarning("Warning", "Employee name is required")
            return
        
        try:
            rate = float(self.emp_rate.get()) if self.emp_rate.get() else 0
        except:
            messagebox.showerror("Error", "Invalid hourly rate")
            return
        
        role = self.emp_role.get()
        phone = self.emp_phone.get()
        email = self.emp_email.get()
        skills = self.emp_skills.get()
        emergency = self.emp_emergency.get()
        emergency_phone = self.emp_emergency_phone.get()
        active = 1 if self.emp_status.get() == 'Active' else 0
        hire_date = datetime.now().strftime("%Y-%m-%d")
        
        self.cursor.execute('''INSERT INTO employees 
            (name, role, hourly_rate, phone, email, hire_date, skills, active, emergency_contact, emergency_phone) 
            VALUES (?,?,?,?,?,?,?,?,?,?)''',
            (name, role, rate, phone, email, hire_date, skills, active, emergency, emergency_phone))
        
        self.conn.commit()
        self.clear_employee_form()
        self.refresh_employee_list()
        messagebox.showinfo("Success", f"Employee {name} added")
    
    def update_employee(self):
        """Update selected employee"""
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an employee")
            return
        
        item = self.employee_tree.item(selected[0])
        emp_id = item['values'][0]
        
        name = self.emp_name.get()
        if not name:
            messagebox.showwarning("Warning", "Employee name is required")
            return
        
        try:
            rate = float(self.emp_rate.get()) if self.emp_rate.get() else 0
        except:
            messagebox.showerror("Error", "Invalid hourly rate")
            return
        
        role = self.emp_role.get()
        phone = self.emp_phone.get()
        email = self.emp_email.get()
        skills = self.emp_skills.get()
        emergency = self.emp_emergency.get()
        emergency_phone = self.emp_emergency_phone.get()
        active = 1 if self.emp_status.get() == 'Active' else 0
        
        self.cursor.execute('''UPDATE employees SET 
            name=?, role=?, hourly_rate=?, phone=?, email=?, skills=?, active=?, emergency_contact=?, emergency_phone=?
            WHERE id=?''',
            (name, role, rate, phone, email, skills, active, emergency, emergency_phone, emp_id))
        
        self.conn.commit()
        self.refresh_employee_list()
        messagebox.showinfo("Success", "Employee updated")
    
    def delete_employee(self):
        """Delete selected employee"""
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an employee")
            return
        
        item = self.employee_tree.item(selected[0])
        emp_name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete employee '{emp_name}'?"):
            emp_id = item['values'][0]
            self.cursor.execute("DELETE FROM employees WHERE id=?", (emp_id,))
            self.conn.commit()
            self.clear_employee_form()
            self.refresh_employee_list()
            messagebox.showinfo("Success", "Employee deleted")
    
    def clear_employee_form(self):
        """Clear employee form"""
        self.emp_name.delete(0, tk.END)
        self.emp_role.set('')
        self.emp_rate.delete(0, tk.END)
        self.emp_phone.delete(0, tk.END)
        self.emp_email.delete(0, tk.END)
        self.emp_skills.delete(0, tk.END)
        self.emp_emergency.delete(0, tk.END)
        self.emp_emergency_phone.delete(0, tk.END)
        self.emp_status.set('Active')
    
    # ============= WORK ORDER TAB =============
    def create_work_order_tab(self):
        """Create work order management tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔧 Work Orders")
        
        # Top frame
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(top_frame, text="Filter Status:").pack(side='left', padx=5)
        self.wo_status_filter = ttk.Combobox(top_frame, values=['All', 'Scheduled', 'In Progress', 'Completed', 'On Hold'], width=15)
        self.wo_status_filter.set('All')
        self.wo_status_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_work_orders())
        self.wo_status_filter.pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="➕ New Work Order", command=self.new_work_order).pack(side='right', padx=5)
        
        # Work order list
        list_frame = ttk.LabelFrame(tab, text="Work Orders", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('WO#', 'Title', 'Client', 'Type', 'Assigned To', 'Status', 'Priority', 'Date', 'Cost')
        self.wo_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.wo_tree.heading(col, text=col)
            widths = {'WO#': 80, 'Title': 150, 'Client': 120, 'Type': 80, 'Assigned To': 100, 'Status': 100, 'Priority': 80, 'Date': 90, 'Cost': 80}
            self.wo_tree.column(col, width=widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.wo_tree.yview)
        self.wo_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.wo_tree.pack(side='left', fill='both', expand=True)
        
        # Work order form
        form_frame = ttk.LabelFrame(tab, text="Work Order Details", padding=10)
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Row 1
        ttk.Label(form_frame, text="WO Number:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.wo_number = ttk.Entry(form_frame, width=15)
        self.wo_number.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Title:*").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.wo_title = ttk.Entry(form_frame, width=30)
        self.wo_title.grid(row=0, column=3, padx=5, pady=5)
        
        # Row 2
        ttk.Label(form_frame, text="Client:*").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.wo_client = ttk.Combobox(form_frame, width=25)
        self.wo_client.grid(row=1, column=1, padx=5, pady=5)
        self.populate_client_combo()
        
        ttk.Label(form_frame, text="Job Type:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.wo_job_type = ttk.Combobox(form_frame, values=['HVAC', 'Electrical', 'Plumbing', 'General'], width=20)
        self.wo_job_type.grid(row=1, column=3, padx=5, pady=5)
        
        # Row 3
        ttk.Label(form_frame, text="Assigned To:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.wo_assigned = ttk.Combobox(form_frame, width=25)
        self.wo_assigned.grid(row=2, column=1, padx=5, pady=5)
        self.populate_employee_combo()
        
        ttk.Label(form_frame, text="Status:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.wo_status = ttk.Combobox(form_frame, values=['Scheduled', 'In Progress', 'On Hold', 'Completed', 'Cancelled'], width=20)
        self.wo_status.grid(row=2, column=3, padx=5, pady=5)
        
        # Row 4
        ttk.Label(form_frame, text="Priority:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.wo_priority = ttk.Combobox(form_frame, values=['Low', 'Medium', 'High', 'Emergency'], width=20)
        self.wo_priority.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Scheduled Date:").grid(row=3, column=2, sticky='w', padx=5, pady=5)
        self.wo_date = ttk.Entry(form_frame, width=20)
        self.wo_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.wo_date.grid(row=3, column=3, padx=5, pady=5)
        
        # Row 5
        ttk.Label(form_frame, text="Est. Hours:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.wo_est_hours = ttk.Entry(form_frame, width=15)
        self.wo_est_hours.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Materials Cost ($):").grid(row=4, column=2, sticky='w', padx=5, pady=5)
        self.wo_materials = ttk.Entry(form_frame, width=15)
        self.wo_materials.grid(row=4, column=3, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=5, column=0, sticky='nw', padx=5, pady=5)
        self.wo_description = tk.Text(form_frame, height=4, width=80)
        self.wo_description.grid(row=5, column=1, columnspan=3, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="💾 Save Work Order", command=self.save_work_order).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete Work Order", command=self.delete_work_order).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📄 Create Invoice", command=self.create_invoice_from_wo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Clear Form", command=self.clear_work_order_form).pack(side='left', padx=5)
        
        self.refresh_work_orders()
    
    def populate_client_combo(self):
        """Populate client combobox"""
        self.cursor.execute("SELECT id, name FROM clients WHERE active=1 ORDER BY name")
        clients = [f"{c[0]}: {c[1]}" for c in self.cursor.fetchall()]
        self.wo_client['values'] = clients
    
    def populate_employee_combo(self):
        """Populate employee combobox"""
        self.cursor.execute("SELECT id, name FROM employees WHERE active=1 ORDER BY name")
        employees = [f"{e[0]}: {e[1]}" for e in self.cursor.fetchall()]
        self.wo_assigned['values'] = employees
    
    def refresh_work_orders(self):
        """Refresh work orders list"""
        for item in self.wo_tree.get_children():
            self.wo_tree.delete(item)
        
        filter_status = self.wo_status_filter.get()
        
        query = "SELECT wo_number, title, client_id, job_type, assigned_to, status, priority, scheduled_date, total_cost FROM work_orders"
        params = []
        
        if filter_status != 'All':
            query += " WHERE status=?"
            params.append(filter_status)
        
        query += " ORDER BY scheduled_date DESC"
        
        self.cursor.execute(query, params)
        for wo in self.cursor.fetchall():
            client_name = self.get_client_name(wo[2])
            emp_name = self.get_employee_name(wo[4])
            self.wo_tree.insert('', 'end', values=(wo[0], wo[1][:30], client_name, wo[3], emp_name, wo[5], wo[6], wo[7], f"${wo[8]:,.2f}"))
    
    def new_work_order(self):
        """Create new work order"""
        self.clear_work_order_form()
        self.wo_number.delete(0, tk.END)
        self.wo_number.insert(0, self.get_next_wo_number())
    
    def save_work_order(self):
        """Save work order"""
        wo_number = self.wo_number.get()
        title = self.wo_title.get()
        client_text = self.wo_client.get()
        job_type = self.wo_job_type.get()
        assigned_text = self.wo_assigned.get()
        status = self.wo_status.get()
        priority = self.wo_priority.get()
        scheduled_date = self.wo_date.get()
        
        try:
            est_hours = float(self.wo_est_hours.get()) if self.wo_est_hours.get() else 0
            materials_cost = float(self.wo_materials.get()) if self.wo_materials.get() else 0
        except:
            messagebox.showerror("Error", "Invalid numeric values")
            return
        
        description = self.wo_description.get(1.0, tk.END).strip()
        
        # Parse client ID
        client_id = None
        if client_text and ':' in client_text:
            client_id = int(client_text.split(':')[0])
        
        # Parse employee ID
        assigned_id = None
        if assigned_text and ':' in assigned_text:
            assigned_id = int(assigned_text.split(':')[0])
        
        if not title or not client_id:
            messagebox.showwarning("Warning", "Title and Client are required")
            return
        
        # Calculate costs
        labor_cost = est_hours * 75
        total_cost = labor_cost + materials_cost
        completed = 1 if status == 'Completed' else 0
        
        # Check if updating existing
        self.cursor.execute("SELECT id FROM work_orders WHERE wo_number=?", (wo_number,))
        existing = self.cursor.fetchone()
        
        if existing:
            # Update existing
            self.cursor.execute('''UPDATE work_orders SET 
                title=?, client_id=?, job_type=?, assigned_to=?, status=?, priority=?, 
                scheduled_date=?, estimated_hours=?, materials_cost=?, labor_cost=?, total_cost=?, 
                description=?, completed=?
                WHERE wo_number=?''',
                (title, client_id, job_type, assigned_id, status, priority, scheduled_date,
                 est_hours, materials_cost, labor_cost, total_cost, description, completed, wo_number))
        else:
            # Insert new
            self.cursor.execute('''INSERT INTO work_orders 
                (wo_number, title, client_id, job_type, assigned_to, status, priority, scheduled_date,
                 estimated_hours, materials_cost, labor_cost, total_cost, description, completed)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (wo_number, title, client_id, job_type, assigned_id, status, priority, scheduled_date,
                 est_hours, materials_cost, labor_cost, total_cost, description, completed))
        
        self.conn.commit()
        self.refresh_work_orders()
        messagebox.showinfo("Success", f"Work Order {wo_number} saved")
    
    def delete_work_order(self):
        """Delete selected work order"""
        selected = self.wo_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a work order")
            return
        
        item = self.wo_tree.item(selected[0])
        wo_number = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete Work Order {wo_number}?"):
            self.cursor.execute("DELETE FROM work_orders WHERE wo_number=?", (wo_number,))
            self.conn.commit()
            self.refresh_work_orders()
            self.clear_work_order_form()
            messagebox.showinfo("Success", "Work Order deleted")
    
    def create_invoice_from_wo(self):
        """Create invoice from selected work order"""
        selected = self.wo_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a work order")
            return
        
        item = self.wo_tree.item(selected[0])
        wo_number = item['values'][0]
        
        # Get work order details
        self.cursor.execute("SELECT id, client_id, total_cost FROM work_orders WHERE wo_number=?", (wo_number,))
        wo = self.cursor.fetchone()
        
        if wo:
            wo_id, client_id, total = wo
            
            # Check if invoice already exists
            self.cursor.execute("SELECT invoice_number FROM invoices WHERE work_order_id=?", (wo_id,))
            if self.cursor.fetchone():
                messagebox.showinfo("Info", "Invoice already exists for this work order")
                return
            
            # Create invoice
            invoice_number = self.get_next_invoice_number()
            tax_rate = 0.09
            tax_amount = total * tax_rate
            total_amount = total + tax_amount
            
            self.cursor.execute('''INSERT INTO invoices 
                (work_order_id, client_id, invoice_number, subtotal, tax_rate, tax_amount, total_amount, 
                 status, issue_date, due_date)
                VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (wo_id, client_id, invoice_number, total, tax_rate, tax_amount, total_amount,
                 'Pending', datetime.now().strftime("%Y-%m-%d"), 
                 (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")))
            
            self.conn.commit()
            messagebox.showinfo("Success", f"Invoice {invoice_number} created for ${total_amount:,.2f}")
            self.notebook.select(4)
    
    def clear_work_order_form(self):
        """Clear work order form"""
        self.wo_number.delete(0, tk.END)
        self.wo_title.delete(0, tk.END)
        self.wo_client.set('')
        self.wo_job_type.set('')
        self.wo_assigned.set('')
        self.wo_status.set('')
        self.wo_priority.set('')
        self.wo_date.delete(0, tk.END)
        self.wo_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.wo_est_hours.delete(0, tk.END)
        self.wo_materials.delete(0, tk.END)
        self.wo_description.delete(1.0, tk.END)
    
    # ============= INVOICE TAB =============
    def create_invoice_tab(self):
        """Create invoice management tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💰 Invoices")
        
        # Top frame
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(top_frame, text="Filter:").pack(side='left', padx=5)
        self.inv_filter = ttk.Combobox(top_frame, values=['All', 'Paid', 'Pending', 'Overdue'], width=15)
        self.inv_filter.set('All')
        self.inv_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_invoices())
        self.inv_filter.pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="📊 Summary", command=self.show_invoice_summary).pack(side='right', padx=5)
        
        # Invoice list
        list_frame = ttk.LabelFrame(tab, text="Invoice Register", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('Invoice #', 'Client', 'Subtotal', 'Tax', 'Total', 'Status', 'Issue Date', 'Due Date')
        self.invoice_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.invoice_tree.heading(col, text=col)
            widths = {'Invoice #': 100, 'Client': 150, 'Subtotal': 100, 'Tax': 80, 'Total': 100, 
                     'Status': 100, 'Issue Date': 90, 'Due Date': 90}
            self.invoice_tree.column(col, width=widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.invoice_tree.pack(side='left', fill='both', expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="✅ Mark as Paid", command=self.mark_invoice_paid).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📧 Send Reminder", command=self.send_reminder).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🖨️ Print Invoice", command=self.print_invoice).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_invoices).pack(side='left', padx=5)
        
        self.refresh_invoices()
    
    def refresh_invoices(self):
        """Refresh invoice list"""
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        filter_status = self.inv_filter.get()
        
        query = """SELECT i.invoice_number, c.name, i.subtotal, i.tax_amount, i.total_amount, 
                          i.status, i.issue_date, i.due_date
                   FROM invoices i
                   JOIN clients c ON i.client_id = c.id"""
        
        if filter_status != 'All':
            query += f" WHERE i.status = '{filter_status}'"
        
        query += " ORDER BY i.issue_date DESC"
        
        self.cursor.execute(query)
        for inv in self.cursor.fetchall():
            status = inv[5]
            if status == 'Pending' and inv[7] < datetime.now().strftime("%Y-%m-%d"):
                status = "⚠️ OVERDUE"
            
            self.invoice_tree.insert('', 'end', values=(
                inv[0], inv[1][:25], f"${inv[2]:,.2f}", f"${inv[3]:,.2f}", 
                f"${inv[4]:,.2f}", status, inv[6], inv[7]))
    
    def mark_invoice_paid(self):
        """Mark selected invoice as paid"""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice")
            return
        
        item = self.invoice_tree.item(selected[0])
        inv_number = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Mark invoice {inv_number} as paid?"):
            self.cursor.execute('''UPDATE invoices SET 
                status='Paid', paid_date=? WHERE invoice_number=?''',
                (datetime.now().strftime("%Y-%m-%d"), inv_number))
            self.conn.commit()
            self.refresh_invoices()
            messagebox.showinfo("Success", f"Invoice {inv_number} marked as paid")
    
    def show_invoice_summary(self):
        """Show invoice summary"""
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Invoice Summary")
        summary_window.geometry("500x400")
        
        self.cursor.execute("SELECT SUM(total_amount) FROM invoices WHERE status='Paid'")
        total_paid = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT SUM(total_amount) FROM invoices WHERE status='Pending'")
        total_pending = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT COUNT(*) FROM invoices WHERE status='Pending' AND due_date < date('now')")
        overdue_count = self.cursor.fetchone()[0] or 0
        
        text_widget = scrolledtext.ScrolledText(summary_window, font=('Courier', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "="*50 + "\n")
        text_widget.insert(tk.END, f"{self.company_name}\n")
        text_widget.insert(tk.END, "INVOICE SUMMARY\n")
        text_widget.insert(tk.END, "="*50 + "\n\n")
        text_widget.insert(tk.END, f"Total Paid:     ${total_paid:,.2f}\n")
        text_widget.insert(tk.END, f"Total Pending:  ${total_pending:,.2f}\n")
        text_widget.insert(tk.END, f"Overdue:        {overdue_count} invoices\n")
    
    def send_reminder(self):
        """Send payment reminder"""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice")
            return
        
        item = self.invoice_tree.item(selected[0])
        inv_number = item['values'][0]
        client_name = item['values'][1]
        amount = item['values'][4]
        
        messagebox.showinfo("Reminder Sent", 
            f"Payment reminder sent for {inv_number}\n"
            f"Client: {client_name}\n"
            f"Amount: {amount}")
    
    def print_invoice(self):
        """Print invoice"""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice")
            return
        
        item = self.invoice_tree.item(selected[0])
        inv_number = item['values'][0]
        
        messagebox.showinfo("Print", f"Printing invoice {inv_number}...\n(Would open print dialog in production)")
    
    # ============= SERVICE CALLS TAB =============
    def create_calls_tab(self):
        """Create service calls tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📞 Service Calls")
        
        # Top frame
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(top_frame, text="Filter:").pack(side='left', padx=5)
        self.call_filter = ttk.Combobox(top_frame, values=['All', 'New', 'In Progress', 'Resolved', 'Closed'], width=15)
        self.call_filter.set('All')
        self.call_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_calls())
        self.call_filter.pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="📞 Call Client", command=self.call_from_call).pack(side='right', padx=5)
        ttk.Button(top_frame, text="➕ New Call", command=self.new_service_call).pack(side='right', padx=5)
        
        # Calls list
        list_frame = ttk.LabelFrame(tab, text="Service Call Log", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Client', 'Issue', 'Status', 'Priority', 'Date', 'Call Back')
        self.calls_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.calls_tree.heading(col, text=col)
            widths = {'ID': 50, 'Client': 150, 'Issue': 200, 'Status': 100, 'Priority': 80, 'Date': 90, 'Call Back': 80}
            self.calls_tree.column(col, width=widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.calls_tree.yview)
        self.calls_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.calls_tree.pack(side='left', fill='both', expand=True)
        
        self.calls_tree.bind('<<TreeviewSelect>>', self.on_call_select)
        
        # Call form
        form_frame = ttk.LabelFrame(tab, text="Call Details", padding=10)
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Client:*").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.call_client = ttk.Combobox(form_frame, width=30)
        self.call_client.grid(row=0, column=1, padx=5, pady=5)
        self.populate_client_combo_call()
        
        ttk.Label(form_frame, text="Issue:*").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.call_issue = ttk.Entry(form_frame, width=40)
        self.call_issue.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Status:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.call_status = ttk.Combobox(form_frame, values=['New', 'In Progress', 'Resolved', 'Closed'], width=20)
        self.call_status.set('New')
        self.call_status.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Priority:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.call_priority = ttk.Combobox(form_frame, values=['Low', 'Medium', 'High', 'Emergency'], width=20)
        self.call_priority.set('Medium')
        self.call_priority.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Notes:").grid(row=2, column=0, sticky='nw', padx=5, pady=5)
        self.call_notes = tk.Text(form_frame, height=4, width=80)
        self.call_notes.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Call Back:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.call_back = ttk.Combobox(form_frame, values=['No', 'Yes'], width=10)
        self.call_back.set('No')
        self.call_back.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="💾 Save Call", command=self.save_service_call).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete Call", command=self.delete_service_call).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📞 Call Now", command=self.call_from_call).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✅ Resolve", command=self.mark_resolved).pack(side='left', padx=5)
        
        self.refresh_calls()
    
    def populate_client_combo_call(self):
        """Populate client combo for calls"""
        self.cursor.execute("SELECT id, name, phone FROM clients WHERE active=1 ORDER BY name")
        clients = [f"{c[0]}: {c[1]} - {c[2]}" for c in self.cursor.fetchall()]
        self.call_client['values'] = clients
    
    def refresh_calls(self):
        """Refresh calls list"""
        for item in self.calls_tree.get_children():
            self.calls_tree.delete(item)
        
        filter_status = self.call_filter.get()
        
        query = """SELECT sc.id, c.name, sc.issue, sc.status, sc.priority, sc.call_date, sc.call_back_needed
                   FROM service_calls sc
                   JOIN clients c ON sc.client_id = c.id"""
        
        if filter_status != 'All':
            query += f" WHERE sc.status = '{filter_status}'"
        
        query += " ORDER BY sc.call_date DESC"
        
        self.cursor.execute(query)
        for call in self.cursor.fetchall():
            call_back = "Yes" if call[6] else "No"
            self.calls_tree.insert('', 'end', values=(call[0], call[1][:25], call[2][:40], call[3], call[4], call[5], call_back))
    
    def on_call_select(self, event):
        """Handle call selection"""
        selected = self.calls_tree.selection()
        if not selected:
            return
        
        item = self.calls_tree.item(selected[0])
        call_id = item['values'][0]
        
        self.cursor.execute("SELECT * FROM service_calls WHERE id=?", (call_id,))
        call = self.cursor.fetchone()
        
        if call:
            self.call_client.set(f"{call[1]}: {self.get_client_name(call[1])}")
            self.call_issue.delete(0, tk.END)
            self.call_issue.insert(0, call[3])
            self.call_status.set(call[4])
            self.call_priority.set(call[5])
            self.call_notes.delete(1.0, tk.END)
            self.call_notes.insert(1.0, call[9] or '')
            self.call_back.set('Yes' if call[11] else 'No')
    
    def new_service_call(self):
        """Clear form for new call"""
        self.call_client.set('')
        self.call_issue.delete(0, tk.END)
        self.call_status.set('New')
        self.call_priority.set('Medium')
        self.call_notes.delete(1.0, tk.END)
        self.call_back.set('No')
    
    def save_service_call(self):
        """Save service call"""
        client_text = self.call_client.get()
        issue = self.call_issue.get()
        status = self.call_status.get()
        priority = self.call_priority.get()
        notes = self.call_notes.get(1.0, tk.END).strip()
        call_back = 1 if self.call_back.get() == 'Yes' else 0
        
        if not client_text or not issue:
            messagebox.showwarning("Warning", "Client and Issue are required")
            return
        
        # Parse client ID
        client_id = int(client_text.split(':')[0]) if ':' in client_text else None
        
        if not client_id:
            messagebox.showwarning("Warning", "Please select a valid client")
            return
        
        # Check if updating existing
        selected = self.calls_tree.selection()
        if selected:
            item = self.calls_tree.item(selected[0])
            call_id = item['values'][0]
            
            self.cursor.execute('''UPDATE service_calls SET 
                client_id=?, issue=?, status=?, priority=?, notes=?, call_back_needed=?
                WHERE id=?''',
                (client_id, issue, status, priority, notes, call_back, call_id))
        else:
            # Insert new
            call_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''INSERT INTO service_calls 
                (client_id, issue, status, priority, call_date, notes, call_back_needed)
                VALUES (?,?,?,?,?,?,?)''',
                (client_id, issue, status, priority, call_date, notes, call_back))
        
        self.conn.commit()
        self.refresh_calls()
        messagebox.showinfo("Success", "Service call saved")
    
    def delete_service_call(self):
        """Delete selected service call"""
        selected = self.calls_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a call")
            return
        
        if messagebox.askyesno("Confirm", "Delete this service call?"):
            item = self.calls_tree.item(selected[0])
            call_id = item['values'][0]
            self.cursor.execute("DELETE FROM service_calls WHERE id=?", (call_id,))
            self.conn.commit()
            self.refresh_calls()
            messagebox.showinfo("Success", "Service call deleted")
    
    def call_from_call(self):
        """Call client using TextNow"""
        selected = self.calls_tree.selection()
        if not selected:
            client_text = self.call_client.get()
            if client_text and ':' in client_text:
                client_id = int(client_text.split(':')[0])
                self.cursor.execute("SELECT phone FROM clients WHERE id=?", (client_id,))
                result = self.cursor.fetchone()
                if result and result[0]:
                    self.initiate_call(result[0])
            return
        
        item = self.calls_tree.item(selected[0])
        client_name = item['values'][1]
        
        self.cursor.execute("SELECT phone FROM clients WHERE name LIKE ?", (f"%{client_name}%",))
        result = self.cursor.fetchone()
        
        if result and result[0]:
            self.initiate_call(result[0])
        else:
            messagebox.showwarning("Warning", "No phone number found")
    
    def initiate_call(self, phone):
        """Initiate call"""
        if messagebox.askyesno("Call Client", f"Call {phone}?"):
            try:
                if platform.system() == 'Windows':
                    webbrowser.open('https://www.textnow.com/messaging')
                    messagebox.showinfo("TextNow", f"Open TextNow and dial: {phone}")
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', f'tel://{phone}'])
                else:
                    subprocess.run(['xdg-open', f'tel://{phone}'])
            except:
                messagebox.showinfo("Info", f"Please call {phone}")
    
    def mark_resolved(self):
        """Mark selected call as resolved"""
        selected = self.calls_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a call")
            return
        
        item = self.calls_tree.item(selected[0])
        call_id = item['values'][0]
        
        resolved_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''UPDATE service_calls SET 
            status='Resolved', resolved_date=? WHERE id=?''',
            (resolved_date, call_id))
        
        self.conn.commit()
        self.refresh_calls()
        messagebox.showinfo("Success", "Call marked as resolved")
    
    # ============= REPORTS TAB =============
    def create_reports_tab(self):
        """Create reports tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 Reports")
        
        # Report options
        options_frame = ttk.LabelFrame(tab, text="Generate Report", padding=10)
        options_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(options_frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5)
        self.report_type = ttk.Combobox(options_frame, values=[
            'Revenue Summary',
            'Work Order Status',
            'Employee Performance',
            'Client List',
            'Service Call Analysis'
        ], width=25)
        self.report_type.set('Revenue Summary')
        self.report_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Period:").grid(row=0, column=2, padx=5, pady=5)
        self.report_period = ttk.Combobox(options_frame, values=['This Month', 'Last Month', 'This Year', 'All Time'], width=15)
        self.report_period.set('This Month')
        self.report_period.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(options_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=4, padx=10, pady=5)
        
        # Report display
        report_frame = ttk.LabelFrame(tab, text="Report Output", padding=10)
        report_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.report_text = scrolledtext.ScrolledText(report_frame, font=('Courier', 10), height=25)
        self.report_text.pack(fill='both', expand=True)
    
    def generate_report(self):
        """Generate selected report"""
        report_type = self.report_type.get()
        
        self.report_text.delete(1.0, tk.END)
        
        if report_type == 'Revenue Summary':
            self.generate_revenue_report()
        elif report_type == 'Work Order Status':
            self.generate_workorder_report()
        elif report_type == 'Employee Performance':
            self.generate_employee_report()
        elif report_type == 'Client List':
            self.generate_client_report()
        elif report_type == 'Service Call Analysis':
            self.generate_service_call_report()
    
    def generate_revenue_report(self):
        """Generate revenue report"""
        self.report_text.insert(tk.END, "="*70 + "\n")
        self.report_text.insert(tk.END, f"{self.company_name} - REVENUE REPORT\n")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*70 + "\n\n")
        
        self.cursor.execute("SELECT SUM(total_amount) FROM invoices WHERE status='Paid'")
        total_paid = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT SUM(total_amount) FROM invoices WHERE status='Pending'")
        total_pending = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT COUNT(*) FROM invoices WHERE status='Paid' AND strftime('%m', paid_date)=strftime('%m', 'now')")
        paid_this_month = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT SUM(total_amount) FROM invoices WHERE status='Paid' AND strftime('%m', paid_date)=strftime('%m', 'now')")
        month_revenue = self.cursor.fetchone()[0] or 0
        
        self.report_text.insert(tk.END, "REVENUE SUMMARY\n")
        self.report_text.insert(tk.END, "-"*40 + "\n")
        self.report_text.insert(tk.END, f"Total Revenue (All Time):  ${total_paid:,.2f}\n")
        self.report_text.insert(tk.END, f"Revenue This Month:       ${month_revenue:,.2f}\n")
        self.report_text.insert(tk.END, f"Invoices Paid This Month: {paid_this_month}\n\n")
        self.report_text.insert(tk.END, f"Outstanding Invoices:     ${total_pending:,.2f}\n")
    
    def generate_workorder_report(self):
        """Generate work order report"""
        self.report_text.insert(tk.END, "="*70 + "\n")
        self.report_text.insert(tk.END, f"{self.company_name} - WORK ORDER REPORT\n")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*70 + "\n\n")
        
        self.cursor.execute("SELECT status, COUNT(*) FROM work_orders GROUP BY status")
        self.report_text.insert(tk.END, "STATUS SUMMARY\n")
        self.report_text.insert(tk.END, "-"*40 + "\n")
        for status in self.cursor.fetchall():
            self.report_text.insert(tk.END, f"{status[0]}: {status[1]}\n")
        
        self.report_text.insert(tk.END, "\nACTIVE WORK ORDERS\n")
        self.report_text.insert(tk.END, "-"*70 + "\n")
        self.cursor.execute('''SELECT wo_number, title, c.name, status, priority, scheduled_date
                               FROM work_orders wo
                               JOIN clients c ON wo.client_id = c.id
                               WHERE completed=0
                               ORDER BY priority DESC''')
        for wo in self.cursor.fetchall():
            self.report_text.insert(tk.END, f"{wo[0]} | {wo[1][:25]} | {wo[2][:20]} | {wo[3]} | {wo[4]} | {wo[5]}\n")
    
    def generate_employee_report(self):
        """Generate employee report"""
        self.report_text.insert(tk.END, "="*70 + "\n")
        self.report_text.insert(tk.END, f"{self.company_name} - EMPLOYEE REPORT\n")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*70 + "\n\n")
        
        self.cursor.execute('''SELECT name, role, hourly_rate, hours_ytd, 
                                      (hours_ytd * hourly_rate) as ytd_earnings
                               FROM employees 
                               WHERE active=1
                               ORDER BY name''')
        
        self.report_text.insert(tk.END, f"{'Name':20} {'Role':20} {'Rate':8} {'Hours YTD':10} {'YTD Earnings':12}\n")
        self.report_text.insert(tk.END, "-"*70 + "\n")
        
        for emp in self.cursor.fetchall():
            self.report_text.insert(tk.END, f"{emp[0]:20} {emp[1]:20} ${emp[2]:6.2f} {emp[3]:10.1f} ${emp[4]:11,.2f}\n")
    
    def generate_client_report(self):
        """Generate client report"""
        self.report_text.insert(tk.END, "="*70 + "\n")
        self.report_text.insert(tk.END, f"{self.company_name} - CLIENT REPORT\n")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*70 + "\n\n")
        
        self.cursor.execute('''SELECT name, phone, email, client_type, 
                                      CASE WHEN active=1 THEN 'Active' ELSE 'Inactive' END
                               FROM clients
                               ORDER BY name''')
        
        self.report_text.insert(tk.END, f"{'Name':30} {'Phone':15} {'Email':25} {'Type':15} {'Status':10}\n")
        self.report_text.insert(tk.END, "-"*95 + "\n")
        
        for client in self.cursor.fetchall():
            self.report_text.insert(tk.END, f"{client[0][:30]:30} {client[1]:15} {client[2][:25]:25} {client[3]:15} {client[4]:10}\n")
    
    def generate_service_call_report(self):
        """Generate service call report"""
        self.report_text.insert(tk.END, "="*70 + "\n")
        self.report_text.insert(tk.END, f"{self.company_name} - SERVICE CALL REPORT\n")
        self.report_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*70 + "\n\n")
        
        self.cursor.execute("SELECT status, COUNT(*) FROM service_calls GROUP BY status")
        self.report_text.insert(tk.END, "STATUS SUMMARY\n")
        self.report_text.insert(tk.END, "-"*40 + "\n")
        for status in self.cursor.fetchall():
            self.report_text.insert(tk.END, f"{status[0]}: {status[1]}\n")
        
        self.report_text.insert(tk.END, "\nOPEN CALLS\n")
        self.report_text.insert(tk.END, "-"*70 + "\n")
        self.cursor.execute('''SELECT c.name, sc.issue, sc.priority, sc.call_date
                               FROM service_calls sc
                               JOIN clients c ON sc.client_id = c.id
                               WHERE sc.status NOT IN ('Resolved', 'Closed')
                               ORDER BY sc.priority DESC''')
        for call in self.cursor.fetchall():
            self.report_text.insert(tk.END, f"{call[0][:25]} | {call[1][:35]} | {call[2]} | {call[3]}\n")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessDashboard(root)
    root.mainloop()