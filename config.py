"""
Configuration management using Windows Registry with optional test isolation.
"""

import json
import os
import sys
from typing import Any, ClassVar

try:
    import winreg
except ImportError:
    winreg = None  # Non-Windows fallback for static analysis and testing

REG_PATH = r"Software\FileMover\Config"
REG_AUTOSTART_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_NAME = "FileMover"


class ConfigError(Exception):
    """Base exception for configuration errors."""


class ConfigManager:
    """Manages application configuration in Windows Registry or in-memory for testing."""

    _test_mode: bool = False
    _test_storage: ClassVar[dict[str, Any]] = {}

    @classmethod
    def set_test_mode(
        cls, enabled: bool = True, initial_data: dict[str, Any] | None = None
    ) -> None:
        """Enable or disable test mode with an isolated in-memory configuration store."""
        cls._test_mode = enabled
        if initial_data is not None:
            cls._test_storage = dict(initial_data)
        elif not enabled:
            cls._test_storage = {}

    @classmethod
    def is_test_mode(cls) -> bool:
        """Check whether test isolation is currently active."""
        return cls._test_mode

    @classmethod
    def test_registry_access(cls) -> tuple[bool, str | None]:
        """Test read and write permissions in the registry."""
        if cls._test_mode:
            return True, None
        if winreg is None:
            return False, "winreg module is not available on this platform."

        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                winreg.SetValueEx(key, "_test", 0, winreg.REG_SZ, "test")
                winreg.DeleteValue(key, "_test")
            return True, None
        except OSError as e:
            return False, str(e)

    @classmethod
    def load_rules(cls) -> list[dict[str, Any]]:
        """Load move rules from registry or test store."""
        if cls._test_mode:
            raw_rules = cls._test_storage.get("move_rules", [])
            return [dict(item) for item in raw_rules]
        if winreg is None:
            return []

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                move_rules_data, _ = winreg.QueryValueEx(key, "move_rules")
                return json.loads(move_rules_data)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return []

    @classmethod
    def save_rules(cls, rules: list[dict[str, Any]]) -> None:
        """Save move rules to registry or test store."""
        sanitized = [
            {
                "source_folder": rule["source_folder"],
                "target_folder": rule["target_folder"],
                "extensions": list(rule["extensions"]),
            }
            for rule in rules
        ]

        if cls._test_mode:
            cls._test_storage["move_rules"] = sanitized
            return
        if winreg is None:
            raise ConfigError("winreg module is not available.")

        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                move_rules_data = json.dumps(sanitized)
                winreg.SetValueEx(key, "move_rules", 0, winreg.REG_SZ, move_rules_data)
        except OSError as e:
            raise ConfigError(f"Error saving rules configuration: {e}") from e

    @classmethod
    def load_delay(cls) -> int:
        """Load delay in minutes."""
        if cls._test_mode:
            return int(cls._test_storage.get("delay_minutes", 5))
        if winreg is None:
            return 5

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                delay, _ = winreg.QueryValueEx(key, "delay_minutes")
                return int(delay)
        except (FileNotFoundError, OSError, ValueError):
            return 5

    @classmethod
    def save_delay(cls, delay_minutes: int) -> None:
        """Save delay in minutes."""
        delay_val = int(delay_minutes)
        if cls._test_mode:
            cls._test_storage["delay_minutes"] = delay_val
            return
        if winreg is None:
            raise ConfigError("winreg module is not available.")

        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                winreg.SetValueEx(key, "delay_minutes", 0, winreg.REG_DWORD, delay_val)
        except OSError as e:
            raise ConfigError(f"Error saving delay: {e}") from e

    @classmethod
    def load_auto_move(cls) -> bool:
        """Load auto-move status."""
        if cls._test_mode:
            return bool(cls._test_storage.get("auto_move_enabled", True))
        if winreg is None:
            return True

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                auto_move, _ = winreg.QueryValueEx(key, "auto_move_enabled")
                return bool(auto_move)
        except (FileNotFoundError, OSError, ValueError):
            return True

    @classmethod
    def save_auto_move(cls, enabled: bool) -> None:
        """Save auto-move status."""
        val = 1 if enabled else 0
        if cls._test_mode:
            cls._test_storage["auto_move_enabled"] = bool(enabled)
            return
        if winreg is None:
            raise ConfigError("winreg module is not available.")

        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                winreg.SetValueEx(key, "auto_move_enabled", 0, winreg.REG_DWORD, val)
        except OSError as e:
            raise ConfigError(f"Error saving auto-move status: {e}") from e

    @classmethod
    def is_autostart_enabled(cls) -> bool:
        """Check if autostart is enabled."""
        if cls._test_mode:
            return bool(cls._test_storage.get("autostart_enabled", False))
        if winreg is None:
            return False

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_AUTOSTART_PATH) as key:
                winreg.QueryValueEx(key, AUTOSTART_NAME)
                return True
        except (FileNotFoundError, OSError):
            return False

    @classmethod
    def enable_autostart(cls) -> bool:
        """Enable autostart by registering absolute executable or script path."""
        if cls._test_mode:
            cls._test_storage["autostart_enabled"] = True
            return True
        if winreg is None:
            raise ConfigError("winreg module is not available.")

        try:
            if getattr(sys, "frozen", False):
                app_path = f'"{os.path.abspath(sys.executable)}"'
            else:
                script_path = os.path.abspath(sys.argv[0])
                app_path = f'"{os.path.abspath(sys.executable)}" "{script_path}"'

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_AUTOSTART_PATH) as key:
                winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, app_path)
            return True
        except OSError as e:
            raise ConfigError(f"Error enabling autostart: {e}") from e

    @classmethod
    def disable_autostart(cls) -> bool:
        """Disable autostart by removing registry entry."""
        if cls._test_mode:
            cls._test_storage["autostart_enabled"] = False
            return True
        if winreg is None:
            raise ConfigError("winreg module is not available.")

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                REG_AUTOSTART_PATH,
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                winreg.DeleteValue(key, AUTOSTART_NAME)
            return True
        except (FileNotFoundError, OSError):
            return False
        except Exception as e:
            raise ConfigError(f"Error disabling autostart: {e}") from e
