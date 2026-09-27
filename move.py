"""
FileMover - Automatic file organizer with system tray integration.
"""

import contextlib
import os
import sys
import threading
from datetime import datetime
from typing import Any

import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

from config import ConfigManager
from file_manager import FileObserverManager, FileQueueManager, MoveRule
from gui import FileMoverGUI


def setup_dpi_awareness() -> None:
    """Configure Windows DPI awareness on main thread before GUI initialization."""
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        with contextlib.suppress(AttributeError, OSError):
            ctypes.windll.user32.SetProcessDPIAware()


class FileMoverApp:
    """Main application class coordinating configuration, GUI, file queue, and tray icon."""

    def __init__(self, test_mode: bool = False):
        self.config = ConfigManager()
        if test_mode and not ConfigManager.is_test_mode():
            ConfigManager.set_test_mode(True)

        registry_ok, registry_error = self.config.test_registry_access()
        if not registry_ok:
            raise RuntimeError(
                f"Cannot access Windows Registry for configuration storage.\n\n"
                f"Error: {registry_error}\n\n"
                f"FileMover requires registry access under:\n"
                f"HKEY_CURRENT_USER\\Software\\FileMover\\Config\n\n"
                f"Please check your Windows permissions."
            )

        self.delay_minutes = self.config.load_delay()
        self.queue_manager = FileQueueManager(self.delay_minutes, self._log)
        self.observer_manager = FileObserverManager(
            self.queue_manager, lambda: self._auto_move_enabled
        )
        self.rules: list[MoveRule] = []
        self._auto_move_enabled = self.config.load_auto_move()
        self.gui = FileMoverGUI(self)
        self.icon: pystray.Icon | None = None
        self._running = False
        self._is_moving = False

        self._load_rules()

    def _load_rules(self) -> None:
        """Load rules from configuration."""
        rules_data = self.config.load_rules()
        for rule_data in rules_data:
            rule = MoveRule(
                rule_data["source_folder"],
                rule_data["target_folder"],
                rule_data["extensions"],
                self._log,
            )
            self.rules.append(rule)
            if os.path.exists(rule.source_folder):
                self.observer_manager.add_rule(rule)

    def _save_rules(self) -> None:
        """Save rules to configuration."""
        rules_data = [
            {
                "source_folder": rule.source_folder,
                "target_folder": rule.target_folder,
                "extensions": rule.extensions,
            }
            for rule in self.rules
        ]
        self.config.save_rules(rules_data)

    def add_rule(
        self, source_folder: str, target_folder: str, extensions: list[str]
    ) -> None:
        """Add a new move rule."""
        norm_source = os.path.abspath(source_folder)
        norm_target = os.path.abspath(target_folder)

        if norm_source == norm_target:
            raise ValueError("Source folder and target folder cannot be identical")

        rule = MoveRule(norm_source, norm_target, extensions, self._log)

        for existing in self.rules:
            if (
                existing.source_folder == rule.source_folder
                and existing.target_folder == rule.target_folder
                and existing.extensions == rule.extensions
            ):
                raise ValueError("Rule already exists")

        self.rules.append(rule)
        if os.path.exists(rule.source_folder):
            self.observer_manager.add_rule(rule)
        self._save_rules()
        self._log(f"Added rule: {rule.source_folder} -> {rule.target_folder}")

    def remove_rule(self, index: int) -> None:
        """Remove a rule by index."""
        if 0 <= index < len(self.rules):
            rule = self.rules[index]
            self.observer_manager.remove_rule(rule)
            del self.rules[index]
            self._save_rules()
            self._log(f"Removed rule: {rule.source_folder} -> {rule.target_folder}")

    def get_rule(self, index: int) -> dict[str, Any] | None:
        """Get rule data by index."""
        if 0 <= index < len(self.rules):
            rule = self.rules[index]
            return {
                "source_folder": rule.source_folder,
                "target_folder": rule.target_folder,
                "extensions": list(rule.extensions),
            }
        return None

    def get_all_rules(self) -> list[dict[str, Any]]:
        """Get all rules data."""
        return [
            {
                "source_folder": rule.source_folder,
                "target_folder": rule.target_folder,
                "extensions": list(rule.extensions),
            }
            for rule in self.rules
        ]

    def move_now(self, dry_run: bool = False, async_mode: bool = False) -> None:
        """Trigger file move immediately for all configured rules."""
        if async_mode:
            threading.Thread(
                target=self._execute_move_now,
                args=(dry_run,),
                daemon=True,
            ).start()
        else:
            self._execute_move_now(dry_run)

    def _execute_move_now(self, dry_run: bool = False) -> None:
        """Internal execution of file moving across all rules."""
        if self._is_moving:
            self._log("Move operation is already running")
            return

        self._is_moving = True
        try:
            mode_label = "DRY RUN - Test" if dry_run else "Immediate Move"
            self._log(f"=== Starting {mode_label} ===")

            total_moved = 0
            total_found = 0

            for rule in list(self.rules):
                if not os.path.exists(rule.source_folder):
                    continue

                try:
                    for filename in os.listdir(rule.source_folder):
                        src_path = os.path.join(rule.source_folder, filename)
                        if os.path.isfile(src_path) and rule.matches_filename(filename):
                            total_found += 1
                            if dry_run:
                                self._log(
                                    f"[Dry Run] Would move: {filename} -> {rule.target_folder}"
                                )
                            else:
                                if rule.move_file(src_path, filename):
                                    total_moved += 1
                except OSError as e:
                    self._log(f"Error scanning {rule.source_folder}: {e}")

            if dry_run:
                self._log(
                    f"=== Dry Run complete: {total_found} matching file(s) found ==="
                )
            else:
                self._log(f"=== Complete: {total_moved} file(s) moved immediately ===")
        finally:
            self._is_moving = False

    def update_delay(self, new_delay_minutes: int) -> None:
        """Update the wait time delay."""
        self.delay_minutes = new_delay_minutes
        self.queue_manager.update_delay(new_delay_minutes)
        self.config.save_delay(new_delay_minutes)
        self._log(f"Wait time updated to {new_delay_minutes} minute(s)")

    def get_queue_status(self) -> list[dict[str, Any]]:
        """Get current status of queued files."""
        return self.queue_manager.get_queue_status()

    def _log(self, message: str) -> None:
        """Log message to GUI if initialized."""
        if self.gui:
            self.gui.log(message)

    def toggle_autostart(self) -> bool:
        """Toggle Windows startup registration."""
        try:
            if self.config.is_autostart_enabled():
                self.config.disable_autostart()
                self._log("Autostart disabled")
                return False
            else:
                self.config.enable_autostart()
                self._log("Autostart enabled")
                return True
        except Exception as e:  # noqa: BLE001 - UI boundary, error goes to the activity log
            self._log(f"Error toggling autostart: {e}")
            return self.config.is_autostart_enabled()

    def is_autostart_enabled(self) -> bool:
        """Check whether autostart is active."""
        return self.config.is_autostart_enabled()

    def toggle_auto_move(self) -> bool:
        """Toggle automatic file moving."""
        self._auto_move_enabled = not self._auto_move_enabled
        self.config.save_auto_move(self._auto_move_enabled)
        status = "enabled" if self._auto_move_enabled else "disabled"
        self._log(f"Automatic file moving {status}")
        return self._auto_move_enabled

    def is_auto_move_enabled(self) -> bool:
        """Check whether auto-move is active."""
        return self._auto_move_enabled

    def show_gui(self) -> None:
        """Display the main GUI window in a thread-safe manner."""
        if self.gui and self.gui.root:
            self.gui.root.after(0, self.gui.show_window)

    def quit_app(self) -> None:
        """Cleanly terminate observers, timers, tray icon, and GUI."""
        self._running = False
        self._log("Shutting down FileMover...")
        self.observer_manager.stop_all()
        self.queue_manager.clear_queue()

        if self.icon:
            with contextlib.suppress(Exception):
                self.icon.stop()

        if self.gui and self.gui.root:
            with contextlib.suppress(Exception):
                self.gui.root.quit()
                self.gui.root.destroy()
            self.gui.root = None

    def run(self) -> None:
        """Run application with system tray and standard event loop."""
        self._running = True
        self.gui.create_window()

        show_at_start = not self.rules
        if show_at_start:
            self.gui.show_window()
        else:
            self.gui.hide_window()

        self.icon = self._create_tray_icon()
        tray_thread = threading.Thread(target=self._run_tray_icon, daemon=True)
        tray_thread.start()

        # Main thread runs Tkinter event loop without CPU-polling
        try:
            self.gui.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

    def _run_tray_icon(self) -> None:
        """Run system tray icon in background thread."""
        try:
            if self.icon:
                self.icon.run()
        except Exception as e:  # noqa: BLE001 - tray thread must not die silently
            self._log(f"System tray error: {e}")

    def _create_tray_icon(self) -> pystray.Icon:
        """Create system tray icon and context menu."""
        image = self._create_icon_image()
        menu = pystray.Menu(
            item("Open", self._on_tray_open, default=True),
            item("Quit", self._on_tray_quit),
        )
        return pystray.Icon("FileMover", image, "FileMover", menu)

    def _create_icon_image(self) -> Image.Image:
        """Create a folder-shaped icon."""
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), color=(33, 150, 243))
        dc = ImageDraw.Draw(image)
        dc.rectangle([10, 20, 54, 50], fill=(100, 181, 246))
        dc.rectangle([10, 15, 30, 20], fill=(100, 181, 246))
        return image

    def _on_tray_open(self, icon, item) -> None:
        """Handle Open click from system tray menu."""
        if self.gui and self.gui.root:
            self.gui.root.after(0, self.gui.show_window)

    def _on_tray_quit(self, icon, item) -> None:
        """Handle Quit click from system tray menu."""
        if self.gui and self.gui.root:
            self.gui.root.after(0, self.quit_app)


def write_crash_log(exception: Exception, exc_traceback) -> str | None:
    """Write crash information to a log file."""
    try:
        import traceback

        if getattr(sys, "frozen", False):
            log_dir = os.path.dirname(sys.executable)
        else:
            log_dir = os.path.dirname(os.path.abspath(__file__))

        log_file = os.path.join(log_dir, "filemover_crash.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(
                f"FileMover Crash Report: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("=" * 80 + "\n\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write(f"Executable: {sys.executable}\n\n")
            f.write(f"Exception Type: {type(exception).__name__}\n")
            f.write(f"Exception Message: {exception}\n\n")
            f.write("Traceback:\n")
            f.write(
                "".join(
                    traceback.format_exception(
                        type(exception), exception, exc_traceback
                    )
                )
            )
            f.write("\n\n")
        return log_file
    except Exception:  # noqa: BLE001 - crash logging is best effort
        return None


def main() -> None:
    """Main application entry point."""
    setup_dpi_awareness()
    try:
        app = FileMoverApp()
        app.run()
    except Exception as e:  # noqa: BLE001 - last resort handler before exit
        log_file = write_crash_log(e, sys.exc_info()[2])
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            msg = f"FileMover encountered an unexpected error:\n\n{e}"
            if log_file:
                msg += f"\n\nDetails were written to:\n{log_file}"
            messagebox.showerror("FileMover Error", msg)
        except Exception:  # noqa: BLE001, S110 - no UI left to report to
            pass


if __name__ == "__main__":
    main()
