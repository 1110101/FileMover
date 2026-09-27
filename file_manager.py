"""
File management, queue system, retry handling, and watchdog event observers.
"""

import contextlib
import os
import shutil
import threading
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def normalize_extension(ext: str) -> str:
    """Normalize file extension with leading dot and lowercase, stripping wildcards."""
    clean = ext.strip().lower()
    clean = clean.lstrip("*").strip()
    if clean and not clean.startswith("."):
        clean = f".{clean}"
    return clean


def resolve_collision_path(target_folder: str, filename: str) -> str:
    """Generate a non-colliding file path in the target folder by appending an index."""
    dst_path = os.path.join(target_folder, filename)
    if not os.path.exists(dst_path):
        return dst_path

    stem, ext = os.path.splitext(filename)
    counter = 1
    while True:
        candidate_name = f"{stem} ({counter}){ext}"
        candidate_path = os.path.join(target_folder, candidate_name)
        if not os.path.exists(candidate_path):
            return candidate_path
        counter += 1


class MoveRule:
    """Represents a file move rule."""

    def __init__(
        self,
        source_folder: str,
        target_folder: str,
        extensions: list[str],
        log_callback: Callable[[str], None] | None = None,
    ):
        self.source_folder = os.path.abspath(source_folder)
        self.target_folder = os.path.abspath(target_folder)
        self.extensions = [
            normalize_extension(ext) for ext in extensions if normalize_extension(ext)
        ]
        self.log_callback = log_callback or (lambda msg: None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MoveRule):
            return False
        return (
            os.path.normcase(self.source_folder)
            == os.path.normcase(other.source_folder)
            and os.path.normcase(self.target_folder)
            == os.path.normcase(other.target_folder)
            and sorted(self.extensions) == sorted(other.extensions)
        )

    def __hash__(self) -> int:
        return hash(
            (
                os.path.normcase(self.source_folder),
                os.path.normcase(self.target_folder),
                tuple(sorted(self.extensions)),
            )
        )

    def matches_filename(self, filename: str) -> bool:
        """Check if a filename matches any of the rule extensions."""
        lower_name = filename.lower()
        return any(lower_name.endswith(ext) for ext in self.extensions)

    def move_file(self, src_path: str, filename: str) -> bool:
        """Move a single file according to this rule with collision handling and lock check."""
        try:
            if not os.path.exists(src_path):
                self.log_callback(f"File no longer exists: {filename}")
                return False

            if os.path.abspath(self.source_folder) == os.path.abspath(
                self.target_folder
            ):
                self.log_callback(
                    f"Skipped (source and target are identical): {filename}"
                )
                return False

            if not self.matches_filename(filename):
                return False

            if not os.path.exists(self.target_folder):
                os.makedirs(self.target_folder, exist_ok=True)
                self.log_callback(f"Created folder: {self.target_folder}")

            if not self._is_file_unlocked(src_path):
                self.log_callback(f"Skipped (file locked): {filename}")
                return False

            dst_path = resolve_collision_path(self.target_folder, filename)
            final_name = os.path.basename(dst_path)

            shutil.move(src_path, dst_path)
            if final_name != filename:
                self.log_callback(
                    f"Moved with rename: {filename} -> {self.target_folder} as {final_name}"
                )
            else:
                self.log_callback(f"Moved: {filename} -> {self.target_folder}")
            return True

        except PermissionError as e:
            self.log_callback(f"Permission error: {filename} - {e}")
            return False
        except OSError as e:
            self.log_callback(f"Error moving {filename}: {e}")
            return False

    def _is_file_unlocked(self, filepath: str) -> bool:
        """Check if file is ready and not exclusively locked by another process."""
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "rb+"):
                pass
            return True
        except PermissionError:
            # File may be marked read-only on Windows; check if read-only handle succeeds
            try:
                with open(filepath, "rb"):
                    pass
                return True
            except OSError:
                return False
        except OSError:
            return False


@dataclass
class QueueEntry:
    timer: threading.Timer
    target_time: datetime
    rule: MoveRule
    retries: int = 0


class FileQueueManager:
    """Manages queued files with individual timers and retry logic for locked files."""

    def __init__(
        self,
        delay_minutes: int,
        log_callback: Callable[[str], None] | None = None,
        max_retries: int = 3,
        retry_delay_seconds: int = 15,
    ):
        self.delay_minutes = delay_minutes
        self.log_callback = log_callback or (lambda msg: None)
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.queue: dict[str, QueueEntry] = {}
        self.lock = threading.Lock()

    def add_file(self, file_path: str, rule: MoveRule) -> None:
        """Add a file to the queue with a timer."""
        norm_path = os.path.abspath(file_path)
        with self.lock:
            if norm_path in self.queue:
                return

            delay_secs = max(0, self.delay_minutes * 60)
            target_time = datetime.now().astimezone() + timedelta(seconds=delay_secs)

            timer = threading.Timer(delay_secs, self._process_file, args=(norm_path,))
            timer.daemon = True
            timer.start()

            self.queue[norm_path] = QueueEntry(
                timer=timer,
                target_time=target_time,
                rule=rule,
                retries=0,
            )

            filename = os.path.basename(norm_path)
            self.log_callback(
                f"Queued: {filename} (will move in {self.delay_minutes} min)"
            )

    def _process_file(self, file_path: str) -> None:
        """Process a file after timer expires with retry backoff."""
        with self.lock:
            if file_path not in self.queue:
                return
            entry = self.queue[file_path]

        filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            with self.lock:
                self.queue.pop(file_path, None)
            self.log_callback(f"File no longer exists: {filename}")
            return

        success = entry.rule.move_file(file_path, filename)

        if success:
            with self.lock:
                self.queue.pop(file_path, None)
            return

        with self.lock:
            if file_path not in self.queue:
                return

            if entry.retries < self.max_retries:
                entry.retries += 1
                entry.target_time = datetime.now().astimezone() + timedelta(
                    seconds=self.retry_delay_seconds
                )
                entry.timer = threading.Timer(
                    self.retry_delay_seconds,
                    self._process_file,
                    args=(file_path,),
                )
                entry.timer.daemon = True
                entry.timer.start()
                self.log_callback(
                    f"Retry {entry.retries}/{self.max_retries} scheduled for {filename} in {self.retry_delay_seconds}s"
                )
            else:
                self.queue.pop(file_path, None)
                self.log_callback(
                    f"Gave up moving {filename} after {self.max_retries} attempts (file locked or inaccessible)"
                )

    def get_queue_status(self) -> list[dict[str, object]]:
        """Get list of files currently in queue with remaining time."""
        with self.lock:
            status = []
            now = datetime.now().astimezone()
            for file_path, entry in self.queue.items():
                remaining = entry.target_time - now
                remaining_seconds = max(0, int(remaining.total_seconds()))
                status.append(
                    {
                        "filename": os.path.basename(file_path),
                        "remaining_seconds": remaining_seconds,
                        "target_folder": entry.rule.target_folder,
                        "retries": entry.retries,
                    }
                )
            return status

    def update_delay(self, new_delay_minutes: int) -> None:
        """Update the delay time for new files."""
        self.delay_minutes = new_delay_minutes

    def clear_queue(self) -> None:
        """Cancel all pending timers and clear the queue."""
        with self.lock:
            for entry in self.queue.values():
                entry.timer.cancel()
            self.queue.clear()


class FileEventHandler(FileSystemEventHandler):
    """Handles file system events for watchdog across multiple rules."""

    def __init__(
        self,
        rules: list[MoveRule],
        queue_manager: FileQueueManager,
        is_enabled_callback: Callable[[], bool],
    ):
        super().__init__()
        self.rules = rules
        self.queue_manager = queue_manager
        self.is_enabled_callback = is_enabled_callback

    def on_created(self, event) -> None:
        """Handle file creation event."""
        if event.is_directory or not self.is_enabled_callback():
            return
        self._handle_file(event.src_path)

    def on_modified(self, event) -> None:
        """Handle file modification event."""
        if event.is_directory or not self.is_enabled_callback():
            return
        self._handle_file(event.src_path)

    def on_moved(self, event) -> None:
        """Handle file moved or renamed event (e.g. browser downloads finishing)."""
        if event.is_directory or not self.is_enabled_callback():
            return
        dest_path = getattr(event, "dest_path", None)
        if dest_path:
            self._handle_file(dest_path)

    def _handle_file(self, file_path: str) -> None:
        """Check if file matches any rule for this folder and add to queue."""
        try:
            filename = os.path.basename(file_path)
            for rule in self.rules:
                if rule.matches_filename(filename):
                    self.queue_manager.add_file(file_path, rule)
                    break
        except Exception as e:  # noqa: BLE001 - a failing event must not kill the watchdog thread
            self.queue_manager.log_callback(f"Error handling {file_path}: {e}")


class FileObserverManager:
    """Manages watchdog observers for multiple rules, supporting multiple rules per directory."""

    def __init__(
        self,
        queue_manager: FileQueueManager,
        is_enabled_callback: Callable[[], bool],
    ):
        self.queue_manager = queue_manager
        self.is_enabled_callback = is_enabled_callback
        self.folder_rules: dict[str, list[MoveRule]] = defaultdict(list)
        self.observers: dict[str, Observer] = {}
        self.handlers: dict[str, FileEventHandler] = {}
        self.lock = threading.Lock()

    def _norm_folder(self, folder: str) -> str:
        return os.path.normcase(os.path.abspath(folder))

    def add_rule(self, rule: MoveRule) -> None:
        """Add a rule and start or update the observer for its source folder."""
        norm_source = self._norm_folder(rule.source_folder)

        with self.lock:
            existing_rules = self.folder_rules[norm_source]
            if rule not in existing_rules:
                existing_rules.append(rule)

            # If observer is already running, the handler's rule list is automatically updated
            if norm_source in self.observers:
                return

            if not os.path.exists(rule.source_folder):
                return

            observer = Observer()
            handler = FileEventHandler(
                existing_rules,
                self.queue_manager,
                self.is_enabled_callback,
            )
            observer.schedule(handler, rule.source_folder, recursive=False)
            observer.start()

            self.observers[norm_source] = observer
            self.handlers[norm_source] = handler

    def remove_rule(self, rule: MoveRule) -> None:
        """Remove a specific rule and stop observer if no rules remain for that directory."""
        norm_source = self._norm_folder(rule.source_folder)

        with self.lock:
            if norm_source in self.folder_rules:
                self.folder_rules[norm_source] = [
                    r for r in self.folder_rules[norm_source] if r != rule
                ]

                if not self.folder_rules[norm_source]:
                    self._stop_observer_locked(norm_source)
                    self.folder_rules.pop(norm_source, None)

    def remove_rule_by_source(self, source_folder: str) -> None:
        """Remove all rules and stop observer for a given source folder."""
        norm_source = self._norm_folder(source_folder)
        with self.lock:
            self._stop_observer_locked(norm_source)
            self.folder_rules.pop(norm_source, None)

    def _stop_observer_locked(self, norm_source: str) -> None:
        """Stop and remove observer for a normalized folder path."""
        if norm_source in self.observers:
            obs = self.observers.pop(norm_source)
            self.handlers.pop(norm_source, None)
            obs.stop()
            with contextlib.suppress(RuntimeError):
                obs.join(timeout=1.0)

    def stop_all(self) -> None:
        """Stop all running observers."""
        with self.lock:
            for obs in self.observers.values():
                obs.stop()
                with contextlib.suppress(RuntimeError):
                    obs.join(timeout=1.0)
            self.observers.clear()
            self.handlers.clear()
            self.folder_rules.clear()
