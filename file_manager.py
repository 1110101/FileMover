"""
File management, queue system, and watchdog event handling
"""
import os
import shutil
import threading
import time
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MoveRule:
    """Represents a file move rule"""
    
    def __init__(self, source_folder, target_folder, extensions, log_callback=None):
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.extensions = extensions
        self.log_callback = log_callback or (lambda msg: None)
    
    def move_file(self, src_path, filename):
        """Move a single file according to this rule"""
        try:
            # Check if file matches extensions
            matches = False
            for ext in self.extensions:
                if filename.lower().endswith(ext.lower()):
                    matches = True
                    break
            
            if not matches:
                return False
            
            # Create target folder if needed
            if not os.path.exists(self.target_folder):
                os.makedirs(self.target_folder)
                self.log_callback(f"Created folder: {self.target_folder}")
            
            dst_path = os.path.join(self.target_folder, filename)
            
            # Check if destination already exists
            if os.path.exists(dst_path):
                self.log_callback(f"Skipped (already exists): {filename}")
                return False
            
            # Check if file is locked
            if not self._is_file_unlocked(src_path):
                self.log_callback(f"Skipped (file locked): {filename}")
                return False
            
            # Move the file
            shutil.move(src_path, dst_path)
            self.log_callback(f"Moved: {filename} -> {self.target_folder}")
            return True
            
        except PermissionError as e:
            self.log_callback(f"Permission error: {filename} - {e}")
            return False
        except Exception as e:
            self.log_callback(f"Error moving {filename}: {e}")
            return False
    
    def _is_file_unlocked(self, filepath):
        """Check if file is not locked by another process"""
        try:
            # Try to open the file in exclusive mode
            with open(filepath, 'a'):
                pass
            return True
        except (IOError, OSError):
            return False


class FileQueueManager:
    """Manages queued files with individual timers"""
    
    def __init__(self, delay_minutes, log_callback=None):
        self.delay_minutes = delay_minutes
        self.log_callback = log_callback or (lambda msg: None)
        self.queue = {}  # {file_path: (timer_thread, target_time, rule)}
        self.lock = threading.Lock()
    
    def add_file(self, file_path, rule):
        """Add a file to the queue with a timer"""
        with self.lock:
            # Check if file is already queued
            if file_path in self.queue:
                return
            
            # Calculate target time
            target_time = datetime.now() + timedelta(minutes=self.delay_minutes)
            
            # Create and start timer thread
            timer = threading.Timer(self.delay_minutes * 60, self._process_file, args=(file_path,))
            timer.daemon = True
            timer.start()
            
            self.queue[file_path] = (timer, target_time, rule)
            
            filename = os.path.basename(file_path)
            self.log_callback(f"Queued: {filename} (will move in {self.delay_minutes} min)")
    
    def _process_file(self, file_path):
        """Process a file after timer expires"""
        with self.lock:
            if file_path not in self.queue:
                return
            
            _, _, rule = self.queue[file_path]
            del self.queue[file_path]
        
        # Check if file still exists
        if not os.path.exists(file_path):
            self.log_callback(f"File no longer exists: {os.path.basename(file_path)}")
            return
        
        # Move the file
        filename = os.path.basename(file_path)
        rule.move_file(file_path, filename)
    
    def get_queue_status(self):
        """Get list of files currently in queue with remaining time"""
        with self.lock:
            status = []
            now = datetime.now()
            for file_path, (timer, target_time, rule) in self.queue.items():
                remaining = target_time - now
                remaining_seconds = max(0, int(remaining.total_seconds()))
                status.append({
                    'filename': os.path.basename(file_path),
                    'remaining_seconds': remaining_seconds,
                    'target_folder': rule.target_folder
                })
            return status
    
    def update_delay(self, new_delay_minutes):
        """Update the delay time for new files"""
        self.delay_minutes = new_delay_minutes
    
    def clear_queue(self):
        """Cancel all pending timers"""
        with self.lock:
            for timer, _, _ in self.queue.values():
                timer.cancel()
            self.queue.clear()


class FileEventHandler(FileSystemEventHandler):
    """Handles file system events for watchdog"""
    
    def __init__(self, rule, queue_manager, is_enabled_callback):
        super().__init__()
        self.rule = rule
        self.queue_manager = queue_manager
        self.is_enabled_callback = is_enabled_callback
    
    def on_created(self, event):
        """Handle file creation event"""
        if event.is_directory or not self.is_enabled_callback():
            return
        
        self._handle_file(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification event"""
        if event.is_directory or not self.is_enabled_callback():
            return
        
        # Only queue if not already queued
        self._handle_file(event.src_path)
    
    def _handle_file(self, file_path):
        """Check if file matches rule and add to queue"""
        try:
            filename = os.path.basename(file_path)
            
            # Check if file extension matches
            for ext in self.rule.extensions:
                if filename.lower().endswith(ext.lower()):
                    # Add to queue with timer
                    self.queue_manager.add_file(file_path, self.rule)
                    break
        except Exception as e:
            pass  # Silently ignore errors during event handling


class FileObserverManager:
    """Manages watchdog observers for multiple rules"""
    
    def __init__(self, queue_manager, is_enabled_callback):
        self.queue_manager = queue_manager
        self.is_enabled_callback = is_enabled_callback
        self.observers = {}  # {source_folder: observer}
    
    def add_rule(self, rule):
        """Add a rule and start observing its source folder"""
        source_folder = rule.source_folder
        
        # Stop existing observer if present
        if source_folder in self.observers:
            self.observers[source_folder].stop()
        
        # Create new observer
        observer = Observer()
        event_handler = FileEventHandler(rule, self.queue_manager, self.is_enabled_callback)
        observer.schedule(event_handler, source_folder, recursive=False)
        observer.start()
        
        self.observers[source_folder] = observer
    
    def remove_rule(self, source_folder):
        """Remove a rule and stop observing its source folder"""
        if source_folder in self.observers:
            self.observers[source_folder].stop()
            del self.observers[source_folder]
    
    def stop_all(self):
        """Stop all observers"""
        for observer in self.observers.values():
            observer.stop()
        self.observers.clear()

