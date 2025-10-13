"""
GUI components for FileMover application
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox


class FileMoverGUI:
    """Main GUI window for FileMover"""
    
    def __init__(self, app):
        self.app = app
        self.root = None
        self.is_visible = False
        
        # GUI elements
        self.source_folder = None
        self.target_folder = None
        self.extensions = None
        self.delay_var = None
        self.rule_listbox = None
        self.log_text = None
        self.status_bar = None
    
    def create_window(self):
        """Create the GUI window"""
        if self.root is not None:
            return
        
        self.root = tk.Tk()
        self.root.title("File Mover")
        self.root.resizable(True, True)
        self.root.minsize(800, 600)  # Minimum size
        
        # Don't destroy on close, just hide
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._create_widgets()
        self.update_rule_list()
        self.update_delay_display()
        
        # Force initial rendering
        self.root.update_idletasks()
        self.root.update()
    
    def _on_close(self):
        """Handle window close button"""
        self.hide_window()
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Configure DPI awareness
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        row = 0
        
        # ==================== SECTION: Add New Rule ====================
        section1 = tk.LabelFrame(self.root, text="📁 Add New Rule", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        section1.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        row += 1
        
        # Source folder
        tk.Label(section1, text="Source Folder:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.source_folder = tk.Entry(section1, width=45, font=('Segoe UI', 9))
        self.source_folder.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        tk.Button(section1, text="Browse...", command=lambda: self._select_folder(self.source_folder), font=('Segoe UI', 9)).grid(
            row=0, column=2, padx=5, pady=5)
        
        # Target folder
        tk.Label(section1, text="Target Folder:", font=('Segoe UI', 10)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.target_folder = tk.Entry(section1, width=45, font=('Segoe UI', 9))
        self.target_folder.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        tk.Button(section1, text="Browse...", command=lambda: self._select_folder(self.target_folder), font=('Segoe UI', 9)).grid(
            row=1, column=2, padx=5, pady=5)
        
        # File extensions
        tk.Label(section1, text="File Extensions:", font=('Segoe UI', 10)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.extensions = tk.Entry(section1, width=45, font=('Segoe UI', 9))
        self.extensions.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        tk.Label(section1, text="(e.g. .pdf, .jpg)", font=('Segoe UI', 8), fg='gray').grid(
            row=2, column=2, sticky="w", padx=5, pady=5)
        
        # Buttons
        button_frame = tk.Frame(section1)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="Add Rule", command=self._add_rule, width=15, font=('Segoe UI', 10), bg='#2196F3', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self._remove_rule, width=18, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        
        section1.grid_columnconfigure(1, weight=1)
        
        # ==================== SECTION: Active Rules ====================
        section2 = tk.LabelFrame(self.root, text="📋 Active Rules", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        section2.grid(row=row, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.root.grid_rowconfigure(row, weight=1)  # Make this section expandable
        row += 1
        
        listbox_frame = tk.Frame(section2)
        listbox_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        section2.grid_rowconfigure(0, weight=1)
        section2.grid_columnconfigure(0, weight=1)
        
        scrollbar_y = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.rule_listbox = tk.Listbox(listbox_frame, width=80, height=5, yscrollcommand=scrollbar_y.set, font=('Segoe UI', 9))
        self.rule_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=self.rule_listbox.yview)
        self.rule_listbox.bind("<Double-Button-1>", self._edit_rule)
        
        tk.Label(section2, text="💡 Tip: Double-click a rule to edit it", font=('Segoe UI', 8), fg='gray').grid(
            row=1, column=0, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        
        # ==================== SECTION: Settings & Actions ====================
        section3 = tk.LabelFrame(self.root, text="⚙️ Settings & Actions", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        section3.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        row += 1
        
        # Settings row
        settings_frame = tk.Frame(section3)
        settings_frame.grid(row=0, column=0, columnspan=3, pady=5)
        
        tk.Label(settings_frame, text="Wait Time:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.delay_var = tk.IntVar(value=self.app.delay_minutes)
        delay_spinbox = tk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.delay_var, width=5, font=('Segoe UI', 9))
        delay_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(settings_frame, text="minutes", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(settings_frame, text="Update", command=self._update_delay, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        # Auto-move toggle
        self.auto_move_button = tk.Button(settings_frame, text="🟢 Auto-Move: ON", command=self._toggle_auto_move, 
                                         width=20, font=('Segoe UI', 9, 'bold'), bg='#4CAF50', fg='white')
        self.auto_move_button.pack(side=tk.LEFT, padx=10)
        
        # Autostart toggle
        autostart_text = "✓ Autostart: ON" if self.app.is_autostart_enabled() else "Autostart: OFF"
        self.autostart_button = tk.Button(settings_frame, text=autostart_text, command=self._toggle_autostart, 
                                         width=18, font=('Segoe UI', 9))
        self.autostart_button.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = tk.Frame(section3)
        action_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        tk.Button(action_frame, text="🚀 Move Now (Skip Wait)", command=self._move_now, width=25, font=('Segoe UI', 10, 'bold'), bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
        
        self.dry_run_var = tk.BooleanVar()
        tk.Checkbutton(action_frame, text="Dry Run (Test Mode)", variable=self.dry_run_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📊 Show Waiting Files", command=self._refresh_queue, width=22, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        # ==================== SECTION: Activity Log ====================
        section4 = tk.LabelFrame(self.root, text="📝 Activity Log", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        section4.grid(row=row, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.root.grid_rowconfigure(row, weight=2)  # Make this section more expandable
        row += 1
        
        log_frame = tk.Frame(section4)
        log_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        section4.grid_rowconfigure(0, weight=1)
        section4.grid_columnconfigure(0, weight=1)
        
        scrollbar_log = tk.Scrollbar(log_frame, orient=tk.VERTICAL)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, yscrollcommand=scrollbar_log.set, font=('Consolas', 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log.config(command=self.log_text.yview)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="✓ Ready - Files will wait {} minute(s) before moving".format(self.app.delay_minutes), 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, font=('Segoe UI', 9), bg='#E8F5E9')
        self.status_bar.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
    
    def _select_folder(self, entry):
        """Open folder selection dialog"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry.delete(0, tk.END)
            entry.insert(0, folder_path)
    
    def _add_rule(self):
        """Add a new move rule"""
        source = self.source_folder.get().strip()
        target = self.target_folder.get().strip()
        exts = self.extensions.get().strip()
        
        if not source or not target or not exts:
            self.status_bar.config(text="Error: Please fill in all fields")
            return
        
        if not os.path.exists(source):
            self.status_bar.config(text="Error: Source folder does not exist")
            return
        
        # Parse extensions
        ext_list = [ext.strip() for ext in exts.split(",")]
        
        # Add rule
        try:
            self.app.add_rule(source, target, ext_list)
            self.update_rule_list()
            self.target_folder.delete(0, tk.END)
            self.extensions.delete(0, tk.END)
            self.status_bar.config(text=f"Rule added: {source} -> {target}")
        except Exception as e:
            self.status_bar.config(text=f"Error: {e}")
    
    def _remove_rule(self):
        """Remove selected rule"""
        selection = self.rule_listbox.curselection()
        if not selection:
            self.status_bar.config(text="Please select a rule to remove")
            return
        
        index = selection[0]
        try:
            self.app.remove_rule(index)
            self.update_rule_list()
            self.status_bar.config(text="Rule removed")
        except Exception as e:
            self.status_bar.config(text=f"Error: {e}")
    
    def _edit_rule(self, event):
        """Load selected rule for editing"""
        selection = self.rule_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        rule_data = self.app.get_rule(index)
        
        self.source_folder.delete(0, tk.END)
        self.source_folder.insert(0, rule_data['source_folder'])
        self.target_folder.delete(0, tk.END)
        self.target_folder.insert(0, rule_data['target_folder'])
        self.extensions.delete(0, tk.END)
        self.extensions.insert(0, ", ".join(rule_data['extensions']))
        
        self._remove_rule()
    
    def _move_now(self):
        """Manually trigger file moving for all rules"""
        dry_run = self.dry_run_var.get()
        if dry_run:
            self.log("=== DRY RUN MODE - No files will be moved ===")
        self.app.move_now(dry_run=dry_run)
        if dry_run:
            self.status_bar.config(text="Dry run completed - check log")
        else:
            self.status_bar.config(text="Files moved immediately")
    
    def _update_delay(self):
        """Update the delay setting"""
        try:
            new_delay = self.delay_var.get()
            self.app.update_delay(new_delay)
            self.status_bar.config(text=f"✓ Wait time updated to {new_delay} minute(s)", bg='#E8F5E9')
        except Exception as e:
            self.status_bar.config(text=f"❌ Error: {e}", bg='#FFEBEE')
    
    def _toggle_auto_move(self):
        """Toggle auto-move on/off"""
        enabled = self.app.toggle_auto_move()
        if enabled:
            self.auto_move_button.config(text="🟢 Auto-Move: ON", bg='#4CAF50')
            self.status_bar.config(text="✓ Automatic file moving enabled", bg='#E8F5E9')
        else:
            self.auto_move_button.config(text="🔴 Auto-Move: OFF", bg='#F44336')
            self.status_bar.config(text="⚠ Automatic file moving disabled - files won't be moved automatically", bg='#FFF3E0')
    
    def _toggle_autostart(self):
        """Toggle Windows autostart on/off"""
        try:
            enabled = self.app.toggle_autostart()
            self.update_autostart_button()
            if enabled:
                self.status_bar.config(text="✓ Windows autostart enabled - FileMover will start with Windows", bg='#E8F5E9')
            else:
                self.status_bar.config(text="✓ Windows autostart disabled", bg='#E8F5E9')
        except Exception as e:
            self.status_bar.config(text=f"❌ Error toggling autostart: {e}", bg='#FFEBEE')
    
    def update_autostart_button(self):
        """Update autostart button to reflect current status"""
        if hasattr(self, 'autostart_button'):
            enabled = self.app.is_autostart_enabled()
            if enabled:
                self.autostart_button.config(text="✓ Autostart: ON", bg='#4CAF50', fg='white')
            else:
                self.autostart_button.config(text="Autostart: OFF", bg='#E0E0E0', fg='black')
    
    def _refresh_queue(self):
        """Refresh queue status display"""
        queue_status = self.app.get_queue_status()
        if queue_status:
            self.log("=== Files Waiting to be Moved ===")
            for item in queue_status:
                mins = item['remaining_seconds'] // 60
                secs = item['remaining_seconds'] % 60
                self.log(f"  • {item['filename']} → {item['target_folder']} (in {mins}m {secs}s)")
            self.log(f"Total: {len(queue_status)} file(s) waiting to be moved")
            self.log("These files will be moved automatically when the timer expires.")
        else:
            self.log("✓ No files waiting - all clear!")
    
    def update_rule_list(self):
        """Update the rule listbox"""
        if self.rule_listbox is None:
            return
        
        self.rule_listbox.delete(0, tk.END)
        for i, rule_data in enumerate(self.app.get_all_rules(), start=1):
            text = f"Rule {i}: {rule_data['source_folder']} -> {rule_data['target_folder']} ({', '.join(rule_data['extensions'])})"
            self.rule_listbox.insert(tk.END, text)
    
    def update_delay_display(self):
        """Update delay display"""
        if self.delay_var is not None:
            self.delay_var.set(self.app.delay_minutes)
    
    def log(self, message):
        """Add message to log"""
        if self.log_text is None:
            return
        
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def show_window(self):
        """Show the GUI window (must be called from main thread)"""
        try:
            if self.root is None:
                self.create_window()
            
            if not self.is_visible:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                # Temporarily make topmost to ensure it shows
                self.root.attributes('-topmost', True)
                self.root.after(100, lambda: self.root.attributes('-topmost', False))
                self.is_visible = True
                # Update autostart button status
                self.update_autostart_button()
        except Exception:
            pass
    
    def hide_window(self):
        """Hide the GUI window"""
        if self.root is not None:
            self.root.withdraw()
        self.is_visible = False
    
    def destroy(self):
        """Destroy the GUI window"""
        if self.root is not None:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None
