"""
Configuration management using Windows Registry
"""
import sys
import json
import winreg


REG_PATH = r"Software\FileMover\Config"
REG_AUTOSTART_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_NAME = "FileMover"


class ConfigManager:
    """Manages application configuration in Windows Registry"""
    
    @staticmethod
    def test_registry_access():
        """Test if we can read/write to registry"""
        try:
            # Try to create and write to test key
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                winreg.SetValueEx(key, "_test", 0, winreg.REG_SZ, "test")
                winreg.DeleteValue(key, "_test")
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def load_rules():
        """Load move rules from registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                move_rules_data, _ = winreg.QueryValueEx(key, "move_rules")
                return json.loads(move_rules_data)
        except (FileNotFoundError, OSError):
            return []
    
    @staticmethod
    def save_rules(rules):
        """Save move rules to registry"""
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                move_rules_data = json.dumps([{
                    "source_folder": rule["source_folder"],
                    "target_folder": rule["target_folder"],
                    "extensions": rule["extensions"]
                } for rule in rules])
                winreg.SetValueEx(key, "move_rules", 0, winreg.REG_SZ, move_rules_data)
        except Exception as e:
            raise Exception(f"Error saving configuration: {e}")
    
    @staticmethod
    def load_delay():
        """Load delay in minutes from registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                delay, _ = winreg.QueryValueEx(key, "delay_minutes")
                return int(delay)
        except (FileNotFoundError, OSError, ValueError):
            return 5  # Default: 5 minutes
    
    @staticmethod
    def save_delay(delay_minutes):
        """Save delay in minutes to registry"""
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                winreg.SetValueEx(key, "delay_minutes", 0, winreg.REG_DWORD, int(delay_minutes))
        except Exception as e:
            raise Exception(f"Error saving delay: {e}")
    
    @staticmethod
    def load_auto_move():
        """Load auto-move enabled status from registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                auto_move, _ = winreg.QueryValueEx(key, "auto_move_enabled")
                return bool(auto_move)
        except (FileNotFoundError, OSError, ValueError):
            return True  # Default: enabled
    
    @staticmethod
    def save_auto_move(enabled):
        """Save auto-move enabled status to registry"""
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                winreg.SetValueEx(key, "auto_move_enabled", 0, winreg.REG_DWORD, int(enabled))
        except Exception as e:
            raise Exception(f"Error saving auto-move status: {e}")
    
    @staticmethod
    def is_autostart_enabled():
        """Check if autostart is enabled"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_AUTOSTART_PATH) as key:
                winreg.QueryValueEx(key, AUTOSTART_NAME)
                return True
        except (FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def enable_autostart():
        """Enable autostart by adding registry entry"""
        try:
            # Get the path to the executable or script
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - always quote the path for spaces
                app_path = f'"{sys.executable}"'
            else:
                # Running as Python script
                app_path = f'"{sys.executable}" "{sys.argv[0]}"'
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_AUTOSTART_PATH) as key:
                winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, app_path)
            return True
        except Exception as e:
            raise Exception(f"Error enabling autostart: {e}")
    
    @staticmethod
    def disable_autostart():
        """Disable autostart by removing registry entry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_AUTOSTART_PATH, 0, 
                               winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, AUTOSTART_NAME)
            return True
        except (FileNotFoundError, OSError):
            return False
        except Exception as e:
            raise Exception(f"Error disabling autostart: {e}")

