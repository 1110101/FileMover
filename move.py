"""
FileMover - Automatic file organizer with system tray integration
"""
import os
import sys
import threading
import tkinter as tk
import traceback
from datetime import datetime

import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

from config import ConfigManager
from file_manager import FileObserverManager, FileQueueManager, MoveRule
from gui import FileMoverGUI


class FileMoverApp:
    """Main application class"""
    
    def __init__(self):
        self.config = ConfigManager()
        
        # Test registry access
        registry_ok, registry_error = self.config.test_registry_access()
        if not registry_ok:
            raise Exception(
                f"Cannot access Windows Registry for configuration storage.\n\n"
                f"Error: {registry_error}\n\n"
                f"FileMover requires registry access under:\n"
                f"HKEY_CURRENT_USER\\Software\\FileMover\\Config\n\n"
                f"Please check your Windows permissions."
            )
        
        self.delay_minutes = self.config.load_delay()
        self.queue_manager = FileQueueManager(self.delay_minutes, self._log)
        self.observer_manager = FileObserverManager(self.queue_manager, lambda: self._auto_move_enabled)
        self.rules = []
        self.gui = FileMoverGUI(self)
        self.icon = None
        
        # Flags for thread-safe GUI control
        self._show_gui_flag = False
        self._hide_gui_flag = False
        self._auto_move_enabled = self.config.load_auto_move()  # Load from registry
        
        # Load configuration
        self._load_rules()
    
    def _load_rules(self):
        """Load rules from configuration"""
        rules_data = self.config.load_rules()
        for rule_data in rules_data:
            rule = MoveRule(
                rule_data['source_folder'],
                rule_data['target_folder'],
                rule_data['extensions'],
                self._log
            )
            self.rules.append(rule)
            
            # Start observing if folder exists
            if os.path.exists(rule.source_folder):
                self.observer_manager.add_rule(rule)
    
    def _save_rules(self):
        """Save rules to configuration"""
        rules_data = [{
            'source_folder': rule.source_folder,
            'target_folder': rule.target_folder,
            'extensions': rule.extensions
        } for rule in self.rules]
        self.config.save_rules(rules_data)
    
    def add_rule(self, source_folder, target_folder, extensions):
        """Add a new move rule"""
        if os.path.abspath(source_folder) == os.path.abspath(target_folder):
            raise Exception("Source folder and target folder cannot be identical")
            
        # Check for duplicates
        for rule in self.rules:
            if (rule.source_folder == source_folder and 
                rule.target_folder == target_folder and 
                rule.extensions == extensions):
                raise Exception("Rule already exists")
        
        # Create and add rule
        rule = MoveRule(source_folder, target_folder, extensions, self._log)
        self.rules.append(rule)
        self.observer_manager.add_rule(rule)
        self._save_rules()
        self._log(f"Added rule: {source_folder} -> {target_folder}")
    
    def remove_rule(self, index):
        """Remove a rule by index"""
        if 0 <= index < len(self.rules):
            rule = self.rules[index]
            self.observer_manager.remove_rule(rule.source_folder)
            del self.rules[index]
            self._save_rules()
            self._log(f"Removed rule: {rule.source_folder}")
    
    def get_rule(self, index):
        """Get rule data by index"""
        if 0 <= index < len(self.rules):
            rule = self.rules[index]
            return {
                'source_folder': rule.source_folder,
                'target_folder': rule.target_folder,
                'extensions': rule.extensions
            }
        return None
    
    def get_all_rules(self):
        """Get all rules data"""
        return [{
            'source_folder': rule.source_folder,
            'target_folder': rule.target_folder,
            'extensions': rule.extensions
        } for rule in self.rules]
    
    def move_now(self, dry_run=False):
        """Manually move files for all rules immediately"""
        if dry_run:
            self._log("=== DRY RUN - Testing what would be moved ===")
        else:
            self._log("=== Moving Files Now (Skip Wait Time) ===")
        
        total_moved = 0
        total_found = 0
        
        for rule in self.rules:
            if not os.path.exists(rule.source_folder):
                continue
            
            try:
                for filename in os.listdir(rule.source_folder):
                    src_path = os.path.join(rule.source_folder, filename)
                    if os.path.isfile(src_path):
                        # Check if matches extension
                        matches = any(filename.lower().endswith(ext.lower()) for ext in rule.extensions)
                        if matches:
                            total_found += 1
                            if dry_run:
                                self._log(f"[DRY RUN] Would move: {filename} → {rule.target_folder}")
                            else:
                                if rule.move_file(src_path, filename):
                                    total_moved += 1
            except Exception as e:
                self._log(f"Error scanning {rule.source_folder}: {e}")
        
        if dry_run:
            self._log(f"=== DRY RUN Complete: Found {total_found} file(s) that would be moved ===")
        else:
            self._log(f"=== Complete: {total_moved} file(s) moved immediately ===")
    
    def update_delay(self, new_delay_minutes):
        """Update the delay setting"""
        self.delay_minutes = new_delay_minutes
        self.queue_manager.update_delay(new_delay_minutes)
        self.config.save_delay(new_delay_minutes)
        self._log(f"Delay updated to {new_delay_minutes} minutes")
    
    def get_queue_status(self):
        """Get current queue status"""
        return self.queue_manager.get_queue_status()
    
    def _log(self, message):
        """Log message to GUI"""
        if self.gui:
            self.gui.log(message)
    
    def toggle_autostart(self):
        """Toggle autostart on/off"""
        try:
            if self.config.is_autostart_enabled():
                self.config.disable_autostart()
                self._log("Autostart disabled")
                return False
            else:
                self.config.enable_autostart()
                self._log("Autostart enabled")
                return True
        except Exception as e:
            self._log(f"Error toggling autostart: {e}")
            return self.config.is_autostart_enabled()
    
    def is_autostart_enabled(self):
        """Check if autostart is enabled"""
        return self.config.is_autostart_enabled()
    
    def toggle_auto_move(self):
        """Toggle automatic file moving"""
        self._auto_move_enabled = not self._auto_move_enabled
        self.config.save_auto_move(self._auto_move_enabled)  # Save to registry
        status = "enabled" if self._auto_move_enabled else "disabled"
        self._log(f"Automatic file moving {status}")
        return self._auto_move_enabled
    
    def is_auto_move_enabled(self):
        """Check if auto-move is enabled"""
        return self._auto_move_enabled
    
    def show_gui(self):
        """Show the GUI window"""
        def show():
            self.gui.show_window()
        
        # If called from icon thread, we need to be careful
        if threading.current_thread() != threading.main_thread():
            # Schedule in main thread if root exists
            if self.gui.root is not None:
                self.gui.root.after(0, show)
            else:
                # Create in main thread using a different approach
                # We can't safely create tkinter windows from threads
                # So we'll set a flag and let the main thread handle it
                pass
        else:
            show()
    
    def quit_app(self):
        """Quit the application"""
        self._log("Shutting down...")
        self._running = False
        self.observer_manager.stop_all()
        self.queue_manager.clear_queue()
        if self.icon:
            self.icon.stop()
        if self.gui.root:
            try:
                self.gui.root.quit()
            except Exception:
                pass
        self.gui.destroy()
    
    def run(self):
        """Run the application with system tray"""
        try:
            # Only create GUI if no rules (first run)
            show_at_start = not self.rules
            if show_at_start:
                self.gui.create_window()
                self.gui.show_window()
            
            # Create and run system tray icon in a separate thread
            self.icon = self._create_tray_icon()
            
            # Run icon in background thread
            self._icon_thread = threading.Thread(target=self._run_icon, daemon=False)
            self._icon_thread.start()
            
            # Run GUI update loop in main thread (without mainloop)
            self._running = True
            while self._running and self._icon_thread.is_alive():
                try:
                    # Check for GUI show/hide requests
                    if self._show_gui_flag:
                        self._show_gui_flag = False
                        # Create GUI if it doesn't exist yet
                        if self.gui.root is None:
                            self.gui.create_window()
                        self.gui.show_window()
                    if self._hide_gui_flag:
                        self._hide_gui_flag = False
                        self.gui.hide_window()
                    
                    # Update GUI only if it exists
                    if self.gui.root:
                        self.gui.root.update()
                except tk.TclError:
                    # Window was destroyed
                    break
                except Exception:
                    pass
                import time
                time.sleep(0.01)  # 10ms delay
            
            # Clean up after loop ends (runs on main thread)
            self.quit_app()
        except KeyboardInterrupt:
            self.quit_app()
        except Exception:
            raise
    
    def _schedule_gui_show(self):
        """Schedule GUI to show (thread-safe)"""
        if self.gui.root is not None:
            self.gui.root.after(0, self.gui.show_window)
    
    def _run_icon(self):
        """Run pystray icon in a thread (Windows-specific workaround)"""
        try:
            # For Windows, we need to ensure thread has message loop
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
            self.icon.run()
        except Exception:
            pass
    
    
    def _create_tray_icon(self):
        """Create system tray icon"""
        # Create a simple icon
        image = self._create_icon_image()
        
        # Create menu
        menu = pystray.Menu(
            item('Open', self._on_open, default=True),
            item('Quit', self._on_quit)
        )
        
        # Create icon
        icon = pystray.Icon("FileMover", image, "FileMover", menu)
        return icon
    
    def _create_icon_image(self):
        """Create icon image"""
        # Create a simple icon with blue background and white "FM" text
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color=(33, 150, 243))
        dc = ImageDraw.Draw(image)
        
        # Draw a simple folder-like shape
        dc.rectangle([10, 20, 54, 50], fill=(100, 181, 246))
        dc.rectangle([10, 15, 30, 20], fill=(100, 181, 246))
        
        return image
    
    def _on_open(self, icon, item):
        """Handle open menu item"""
        # Set flag for main thread to show GUI
        self._show_gui_flag = True
    
    
    def _on_quit(self, icon, item):
        """Handle quit menu item"""
        # Signal main thread to quit cleanly
        self._running = False


def write_crash_log(exception, exc_traceback):
    """Write crash information to a log file"""
    try:
        # Get executable/script directory
        if getattr(sys, 'frozen', False):
            log_dir = os.path.dirname(sys.executable)
        else:
            log_dir = os.path.dirname(os.path.abspath(__file__))
        
        log_file = os.path.join(log_dir, 'filemover_crash.log')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"FileMover Crash Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # System info
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write(f"Executable: {sys.executable}\n\n")
            
            # Exception info
            f.write(f"Exception Type: {type(exception).__name__}\n")
            f.write(f"Exception Message: {exception!s}\n\n")
            
            # Full traceback
            f.write("Traceback:\n")
            f.write(''.join(traceback.format_exception(type(exception), exception, exc_traceback)))
            f.write("\n\n")
        
        return log_file
    except Exception:
        # If we can't write the crash log, silently fail
        pass
    return None


def main():
    """Main entry point"""
    try:
        app = FileMoverApp()
        app.run()
    except Exception as e:
        # Write crash log
        log_file = write_crash_log(e, sys.exc_info()[2])
        
        # Try to show error dialog if tkinter is available
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            if log_file:
                messagebox.showerror(
                    "FileMover Crash",
                    f"FileMover has encountered an error and needs to close.\n\n"
                    f"Error details have been saved to:\n{log_file}\n\n"
                    f"Error: {e!s}"
                )
            else:
                messagebox.showerror(
                    "FileMover Crash",
                    f"FileMover has encountered an error and needs to close.\n\n"
                    f"Error: {e!s}"
                )
        except Exception:
            pass


if __name__ == "__main__":
    main()
