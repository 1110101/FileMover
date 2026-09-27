"""
GUI components for FileMover application.
"""

import contextlib
import os
import tkinter as tk
from tkinter import filedialog, ttk


class FileMoverGUI:
    """Main GUI window for FileMover."""

    def __init__(self, app):
        self.app = app
        self.root: tk.Tk | None = None
        self.is_visible = False
        self._editing_index: int | None = None

        self.source_folder: ttk.Entry | None = None
        self.target_folder: ttk.Entry | None = None
        self.extensions: ttk.Entry | None = None
        self.delay_var: tk.IntVar | None = None
        self.rule_listbox: tk.Listbox | None = None
        self.log_text: tk.Text | None = None
        self.status_bar: ttk.Label | None = None
        self.add_button: ttk.Button | None = None
        self.cancel_button: ttk.Button | None = None
        self.auto_move_button: tk.Button | None = None
        self.autostart_button: tk.Button | None = None
        self.move_now_button: ttk.Button | None = None
        self.test_run_button: ttk.Button | None = None

    def create_window(self) -> None:
        """Create the GUI window and initialize widgets."""
        if self.root is not None:
            return

        self.root = tk.Tk()
        self.root.title("FileMover")
        self.root.resizable(True, True)
        self.root.minsize(800, 620)

        style = ttk.Style(self.root)
        with contextlib.suppress(tk.TclError):
            style.theme_use("vista")

        # Hide window on close instead of destroying application
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_widgets()
        self.update_rule_list()
        self.update_delay_display()

        self.root.update_idletasks()

    def _on_close(self) -> None:
        """Handle window close button by hiding to system tray."""
        self.hide_window()

    def _create_widgets(self) -> None:
        """Construct GUI sections and controls without decorative emojis."""
        row = 0
        container = ttk.Frame(self.root, padding="10 10 10 10")
        container.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.rule_frame_label = tk.StringVar(value="Add Rule")
        section1 = ttk.LabelFrame(container, text="Add Rule", padding="10 10 10 10")
        section1.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        section1.grid_columnconfigure(1, weight=1)
        row += 1

        ttk.Label(section1, text="Source Folder:", font=("Segoe UI", 9)).grid(
            row=0, column=0, sticky="w", padx=5, pady=4
        )
        self.source_folder = ttk.Entry(section1, font=("Segoe UI", 9))
        self.source_folder.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        ttk.Button(
            section1,
            text="Browse...",
            command=lambda: self._select_folder(self.source_folder),
        ).grid(row=0, column=2, padx=5, pady=4)

        ttk.Label(section1, text="Target Folder:", font=("Segoe UI", 9)).grid(
            row=1, column=0, sticky="w", padx=5, pady=4
        )
        self.target_folder = ttk.Entry(section1, font=("Segoe UI", 9))
        self.target_folder.grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        ttk.Button(
            section1,
            text="Browse...",
            command=lambda: self._select_folder(self.target_folder),
        ).grid(row=1, column=2, padx=5, pady=4)

        ttk.Label(section1, text="File Extensions:", font=("Segoe UI", 9)).grid(
            row=2, column=0, sticky="w", padx=5, pady=4
        )
        self.extensions = ttk.Entry(section1, font=("Segoe UI", 9))
        self.extensions.grid(row=2, column=1, sticky="ew", padx=5, pady=4)
        ttk.Label(
            section1,
            text="Example: .pdf, .jpg or pdf, jpg",
            font=("Segoe UI", 8),
            foreground="#666666",
        ).grid(row=2, column=2, sticky="w", padx=5, pady=4)

        button_frame = ttk.Frame(section1)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(8, 0))

        self.add_button = ttk.Button(
            button_frame,
            text="Add Rule",
            command=self._save_or_add_rule,
            width=16,
        )
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_edit,
            width=12,
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        self.cancel_button.pack_forget()

        ttk.Button(
            button_frame,
            text="Remove Selected",
            command=self._remove_rule,
            width=18,
        ).pack(side=tk.LEFT, padx=5)

        section2 = ttk.LabelFrame(container, text="Active Rules", padding="10 10 10 10")
        section2.grid(row=row, column=0, sticky="nsew", pady=(0, 10))
        section2.grid_rowconfigure(0, weight=1)
        section2.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(row, weight=1)
        row += 1

        listbox_frame = ttk.Frame(section2)
        listbox_frame.grid(row=0, column=0, sticky="nsew")
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)

        scrollbar_y = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.rule_listbox = tk.Listbox(
            listbox_frame,
            width=80,
            height=5,
            yscrollcommand=scrollbar_y.set,
            font=("Segoe UI", 9),
            selectmode=tk.SINGLE,
        )
        self.rule_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=self.rule_listbox.yview)
        self.rule_listbox.bind("<Double-Button-1>", self._edit_rule)

        ttk.Label(
            section2,
            text="Tip: Double click a rule to edit its configuration safely.",
            font=("Segoe UI", 8),
            foreground="#666666",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        section3 = ttk.LabelFrame(
            container, text="Settings and Actions", padding="10 10 10 10"
        )
        section3.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        section3.grid_columnconfigure(0, weight=1)
        row += 1

        settings_frame = ttk.Frame(section3)
        settings_frame.pack(fill=tk.X, pady=(0, 8))

        wait_group = ttk.LabelFrame(settings_frame, text="Wait Time", padding="6 6 6 6")
        wait_group.pack(side=tk.LEFT, padx=(0, 15))

        self.delay_var = tk.IntVar(value=self.app.delay_minutes)
        delay_spinbox = ttk.Spinbox(
            wait_group,
            from_=1,
            to=60,
            textvariable=self.delay_var,
            width=4,
            font=("Segoe UI", 9),
        )
        delay_spinbox.pack(side=tk.LEFT, padx=(0, 4))
        ttk.Label(wait_group, text="Minutes", font=("Segoe UI", 9)).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(wait_group, text="Save", command=self._update_delay).pack(
            side=tk.LEFT
        )

        toggles_frame = ttk.Frame(settings_frame)
        toggles_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.auto_move_button = tk.Button(
            toggles_frame,
            text="AutoMove: ON",
            command=self._toggle_auto_move,
            width=16,
            font=("Segoe UI", 9),
            bg="#2e7d32",
            fg="white",
            relief=tk.GROOVE,
        )
        self.auto_move_button.pack(side=tk.LEFT, padx=5, pady=4)

        autostart_text = (
            "Autostart: ON" if self.app.is_autostart_enabled() else "Autostart: OFF"
        )
        self.autostart_button = tk.Button(
            toggles_frame,
            text=autostart_text,
            command=self._toggle_autostart,
            width=16,
            font=("Segoe UI", 9),
            relief=tk.GROOVE,
        )
        self.autostart_button.pack(side=tk.LEFT, padx=5, pady=4)
        self.update_autostart_button()

        action_frame = ttk.Frame(section3)
        action_frame.pack(fill=tk.X)

        self.move_now_button = ttk.Button(
            action_frame,
            text="Move Now",
            command=self._move_now,
            width=16,
        )
        self.move_now_button.pack(side=tk.LEFT, padx=5)

        self.test_run_button = ttk.Button(
            action_frame,
            text="Test Run",
            command=self._test_run,
            width=16,
        )
        self.test_run_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="Show Waiting Files",
            command=self._refresh_queue,
            width=20,
        ).pack(side=tk.LEFT, padx=5)

        section4 = ttk.LabelFrame(container, text="Activity Log", padding="10 10 10 10")
        section4.grid(row=row, column=0, sticky="nsew", pady=(0, 5))
        section4.grid_rowconfigure(0, weight=1)
        section4.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(row, weight=2)
        row += 1

        log_frame = ttk.Frame(section4)
        log_frame.grid(row=0, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        scrollbar_log = ttk.Scrollbar(log_frame, orient=tk.VERTICAL)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            log_frame,
            height=7,
            wrap=tk.WORD,
            yscrollcommand=scrollbar_log.set,
            font=("Consolas", 9),
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log.config(command=self.log_text.yview)

        self.status_bar = ttk.Label(
            container,
            text=f"Ready. Wait time: {self.app.delay_minutes} minute(s)",
            font=("Segoe UI", 9),
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="4 4 4 4",
        )
        self.status_bar.grid(row=row, column=0, sticky="ew", pady=(5, 0))

    def _select_folder(self, entry: ttk.Entry) -> None:
        """Open folder selection dialog."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry.delete(0, tk.END)
            entry.insert(0, os.path.normpath(folder_path))

    def _save_or_add_rule(self) -> None:
        """Add new rule or save changes to currently edited rule safely."""
        source = self.source_folder.get().strip().strip("'\"")
        target = self.target_folder.get().strip().strip("'\"")
        exts = self.extensions.get().strip()

        if not source or not target or not exts:
            self._set_status("Please fill in all rule fields", error=True)
            return

        if os.path.abspath(source) == os.path.abspath(target):
            self._set_status(
                "Source folder and target folder cannot be identical", error=True
            )
            return

        if not os.path.exists(source):
            self._set_status("Source folder does not exist", error=True)
            return

        ext_list = [ext.strip() for ext in exts.split(",") if ext.strip()]

        try:
            if self._editing_index is not None:
                index = self._editing_index
                self.app.remove_rule(index)
                self.app.add_rule(source, target, ext_list)
                self._set_status(f"Updated rule: {source} -> {target}")
                self._cancel_edit()
            else:
                self.app.add_rule(source, target, ext_list)
                self.target_folder.delete(0, tk.END)
                self.extensions.delete(0, tk.END)
                self._set_status(f"Rule added: {source} -> {target}")

            self.update_rule_list()
        except Exception as e:  # noqa: BLE001 - UI boundary, error is shown in the status bar
            self._set_status(f"Error saving rule: {e}", error=True)

    def _edit_rule(self, event=None) -> None:
        """Load selected rule into fields for safe editing without immediate deletion."""
        if not self.rule_listbox:
            return

        selection = self.rule_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        rule_data = self.app.get_rule(index)
        if not rule_data:
            return

        self._editing_index = index
        self.source_folder.delete(0, tk.END)
        self.source_folder.insert(0, rule_data["source_folder"])
        self.target_folder.delete(0, tk.END)
        self.target_folder.insert(0, rule_data["target_folder"])
        self.extensions.delete(0, tk.END)
        self.extensions.insert(0, ", ".join(rule_data["extensions"]))

        self.add_button.config(text="Save Changes")
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        self._set_status(f"Editing Rule {index + 1}. Click Save Changes to apply.")

    def _cancel_edit(self) -> None:
        """Cancel current editing mode."""
        self._editing_index = None
        self.source_folder.delete(0, tk.END)
        self.target_folder.delete(0, tk.END)
        self.extensions.delete(0, tk.END)
        self.add_button.config(text="Add Rule")
        self.cancel_button.pack_forget()
        self._set_status("Editing cancelled")

    def _remove_rule(self) -> None:
        """Remove selected rule from list."""
        if not self.rule_listbox:
            return

        selection = self.rule_listbox.curselection()
        if not selection:
            self._set_status("Please select a rule to remove", error=True)
            return

        index = selection[0]
        try:
            self.app.remove_rule(index)
            if self._editing_index == index:
                self._cancel_edit()
            elif self._editing_index is not None and self._editing_index > index:
                self._editing_index -= 1
            self.update_rule_list()
            self._set_status("Rule removed")
        except Exception as e:  # noqa: BLE001 - UI boundary, error is shown in the status bar
            self._set_status(f"Error removing rule: {e}", error=True)

    def _move_now(self) -> None:
        """Trigger move now asynchronously so the GUI stays responsive."""
        self._set_status("Moving matching files immediately...")
        if self.move_now_button:
            self.move_now_button.config(state=tk.DISABLED)

        def run_move():
            self.app.move_now(dry_run=False)
            if self.root:
                self.root.after(
                    0, lambda: self._on_move_complete("Files moved immediately")
                )

        import threading

        threading.Thread(target=run_move, daemon=True).start()

    def _test_run(self) -> None:
        """Run move in dry run mode asynchronously."""
        self._set_status("Running test check without moving files...")
        if self.test_run_button:
            self.test_run_button.config(state=tk.DISABLED)

        def run_test():
            self.app.move_now(dry_run=True)
            if self.root:
                self.root.after(
                    0,
                    lambda: self._on_test_complete(
                        "Test run complete. Check Activity Log."
                    ),
                )

        import threading

        threading.Thread(target=run_test, daemon=True).start()

    def _on_move_complete(self, message: str) -> None:
        if self.move_now_button:
            self.move_now_button.config(state=tk.NORMAL)
        self._set_status(message)

    def _on_test_complete(self, message: str) -> None:
        if self.test_run_button:
            self.test_run_button.config(state=tk.NORMAL)
        self._set_status(message)

    def _update_delay(self) -> None:
        """Update wait time setting."""
        try:
            new_delay = self.delay_var.get()
            self.app.update_delay(new_delay)
            self._set_status(f"Wait time updated to {new_delay} minute(s)")
        except Exception as e:  # noqa: BLE001 - UI boundary, error is shown in the status bar
            self._set_status(f"Error updating delay: {e}", error=True)

    def _toggle_auto_move(self) -> None:
        """Toggle auto-move active state."""
        try:
            enabled = self.app.toggle_auto_move()
            if enabled:
                self.auto_move_button.config(
                    text="AutoMove: ON", bg="#2e7d32", fg="white"
                )
                self._set_status("Automatic file moving enabled")
            else:
                self.auto_move_button.config(
                    text="AutoMove: OFF", bg="#c62828", fg="white"
                )
                self._set_status("Automatic file moving paused")
        except Exception as e:  # noqa: BLE001 - UI boundary, error is shown in the status bar
            self._set_status(f"Error toggling auto-move: {e}", error=True)

    def _toggle_autostart(self) -> None:
        """Toggle Windows autostart state."""
        try:
            enabled = self.app.toggle_autostart()
            self.update_autostart_button()
            if enabled:
                self._set_status("Windows autostart enabled")
            else:
                self._set_status("Windows autostart disabled")
        except Exception as e:  # noqa: BLE001 - UI boundary, error is shown in the status bar
            self._set_status(f"Error toggling autostart: {e}", error=True)

    def update_autostart_button(self) -> None:
        """Update autostart button text and color."""
        if hasattr(self, "autostart_button") and self.autostart_button:
            enabled = self.app.is_autostart_enabled()
            if enabled:
                self.autostart_button.config(
                    text="Autostart: ON", bg="#2e7d32", fg="white"
                )
            else:
                self.autostart_button.config(
                    text="Autostart: OFF", bg="#e0e0e0", fg="black"
                )

    def _refresh_queue(self) -> None:
        """Display files currently waiting in queue."""
        queue_status = self.app.get_queue_status()
        if queue_status:
            self.log("=== Files Waiting in Queue ===")
            for item in queue_status:
                mins = item["remaining_seconds"] // 60
                secs = item["remaining_seconds"] % 60
                retry_info = f", retry {item['retries']}" if item.get("retries") else ""
                self.log(
                    f"  File: {item['filename']} -> {item['target_folder']} (in {mins}m {secs}s{retry_info})"
                )
            self.log(f"Total: {len(queue_status)} file(s) waiting")
        else:
            self.log("Queue is currently empty.")

    def update_rule_list(self) -> None:
        """Update the rule listbox display."""
        if self.rule_listbox is None:
            return

        self.rule_listbox.delete(0, tk.END)
        for i, rule_data in enumerate(self.app.get_all_rules(), start=1):
            text = f"Rule {i}: {rule_data['source_folder']} -> {rule_data['target_folder']} ({', '.join(rule_data['extensions'])})"
            self.rule_listbox.insert(tk.END, text)

    def update_delay_display(self) -> None:
        """Update delay display value."""
        if self.delay_var is not None:
            self.delay_var.set(self.app.delay_minutes)

    def log(self, message: str) -> None:
        """Thread-safe logging to activity text area."""

        def append():
            if self.log_text:
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)

        if self.root:
            self.root.after(0, append)

    def _set_status(self, text: str, error: bool = False) -> None:
        """Update status bar text."""
        if self.status_bar:
            self.status_bar.config(text=text)

    def show_window(self) -> None:
        """Display the GUI window."""
        if self.root is None:
            self.create_window()

        if self.root:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.is_visible = True
            self.update_autostart_button()

    def hide_window(self) -> None:
        """Hide GUI window to system tray."""
        if self.root is not None:
            self.root.withdraw()
        self.is_visible = False

    def destroy(self) -> None:
        """Destroy the GUI window."""
        if self.root is not None:
            with contextlib.suppress(tk.TclError):
                self.root.destroy()
            self.root = None
