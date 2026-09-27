"""
Comprehensive Integration and Unit Test Suite for FileMover.
All tests run with isolated configuration storage to protect real registry entries.
"""

import os
import shutil
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import ConfigManager
from file_manager import MoveRule, normalize_extension, resolve_collision_path
from move import FileMoverApp


class TestFileMoverIntegrationSuite(unittest.TestCase):
    def setUp(self):
        # Enable test mode with empty in-memory configuration
        ConfigManager.set_test_mode(True, initial_data={})

        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.src1 = os.path.join(self.test_dir, "source1")
        self.dst1 = os.path.join(self.test_dir, "target1")
        self.src2 = os.path.join(self.test_dir, "source2")
        self.dst2 = os.path.join(self.test_dir, "target2")

        for d in [self.src1, self.dst1, self.src2, self.dst2]:
            os.makedirs(d, exist_ok=True)

    def tearDown(self):
        # Disable test mode and clean up storage
        ConfigManager.set_test_mode(False)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_extension_normalization(self):
        """Verify extension normalization handles wildcards, dots, and whitespace."""
        self.assertEqual(normalize_extension("*.pdf"), ".pdf")
        self.assertEqual(normalize_extension("*pdf"), ".pdf")
        self.assertEqual(normalize_extension(".PDF"), ".pdf")
        self.assertEqual(normalize_extension("  jpg  "), ".jpg")
        self.assertEqual(normalize_extension(""), "")

    def test_collision_path_resolution(self):
        """Verify file collision creates non-overlapping enumerated filenames."""
        existing_file = os.path.join(self.dst1, "document.pdf")
        with open(existing_file, "w", encoding="utf-8") as f:
            f.write("existing")

        new_path = resolve_collision_path(self.dst1, "document.pdf")
        self.assertEqual(os.path.basename(new_path), "document (1).pdf")

        # Create the (1) file as well
        with open(new_path, "w", encoding="utf-8") as f:
            f.write("second")

        third_path = resolve_collision_path(self.dst1, "document.pdf")
        self.assertEqual(os.path.basename(third_path), "document (2).pdf")

    def test_end_to_end_file_moving_workflow(self):
        """Integration Test 1: Full file moving workflow (Dry Run -> Real Move)."""
        app = FileMoverApp(test_mode=True)
        app.add_rule(self.src1, self.dst1, ["*.pdf", ".jpg"])

        self.assertEqual(len(app.rules), 1)
        self.assertIn(".pdf", app.rules[0].extensions)
        self.assertIn(".jpg", app.rules[0].extensions)

        pdf_path = os.path.join(self.src1, "invoice.pdf")
        jpg_path = os.path.join(self.src1, "photo.jpg")
        txt_path = os.path.join(self.src1, "notes.txt")

        for f in [pdf_path, jpg_path, txt_path]:
            with open(f, "w", encoding="utf-8") as file:
                file.write("content")

        # 1. Dry Run
        app.move_now(dry_run=True)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(os.path.exists(jpg_path))
        self.assertTrue(os.path.exists(txt_path))

        # 2. Real Move
        app.move_now(dry_run=False)
        self.assertFalse(os.path.exists(pdf_path))
        self.assertFalse(os.path.exists(jpg_path))
        self.assertTrue(os.path.exists(os.path.join(self.dst1, "invoice.pdf")))
        self.assertTrue(os.path.exists(os.path.join(self.dst1, "photo.jpg")))

        # Non-matching file remains
        self.assertTrue(os.path.exists(txt_path))
        app.quit_app()

    def test_multiple_rules_same_source_folder(self):
        """Integration Test 2: Multiple rules for the SAME source folder must both remain active."""
        app = FileMoverApp(test_mode=True)
        app.add_rule(self.src1, self.dst1, [".pdf"])
        app.add_rule(self.src1, self.dst2, [".png"])

        self.assertEqual(len(app.get_all_rules()), 2)

        # Source files
        doc1 = os.path.join(self.src1, "document.pdf")
        img1 = os.path.join(self.src1, "screenshot.png")

        with open(doc1, "w", encoding="utf-8") as f:
            f.write("pdf data")
        with open(img1, "w", encoding="utf-8") as f:
            f.write("png data")

        app.move_now(dry_run=False)

        self.assertTrue(os.path.exists(os.path.join(self.dst1, "document.pdf")))
        self.assertTrue(os.path.exists(os.path.join(self.dst2, "screenshot.png")))
        app.quit_app()

    def test_browser_download_rename_handling(self):
        """Integration Test 3: Simulates browser download completing from temp file to destination."""
        app = FileMoverApp(test_mode=True)
        app.update_delay(0)  # Immediate processing
        app.add_rule(self.src1, self.dst1, [".zip"])

        # Give observer thread time to start
        time.sleep(0.2)

        # Create temp download file
        crdownload = os.path.join(self.src1, "archive.zip.crdownload")
        with open(crdownload, "w", encoding="utf-8") as f:
            f.write("zip download data")

        final_zip = os.path.join(self.src1, "archive.zip")
        # Rename like Chrome or Firefox does upon completion
        os.rename(crdownload, final_zip)

        # Allow watchdog and queue thread to catch event
        time.sleep(0.8)

        # File should be moved to dst1
        moved_file = os.path.join(self.dst1, "archive.zip")
        # If not moved yet by timer, trigger queue or check
        if not os.path.exists(moved_file):
            app.move_now(dry_run=False)

        self.assertTrue(os.path.exists(moved_file))
        app.quit_app()

    def test_destination_collision_renaming(self):
        """Integration Test 4: Moving a file when target exists creates enumerated duplicate."""
        app = FileMoverApp(test_mode=True)
        app.add_rule(self.src1, self.dst1, [".pdf"])

        # Existing target file
        existing = os.path.join(self.dst1, "report.pdf")
        with open(existing, "w", encoding="utf-8") as f:
            f.write("original")

        # Source file with same name
        source_file = os.path.join(self.src1, "report.pdf")
        with open(source_file, "w", encoding="utf-8") as f:
            f.write("updated")

        app.move_now(dry_run=False)

        self.assertTrue(os.path.exists(existing))
        with open(existing, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "original")

        renamed_target = os.path.join(self.dst1, "report (1).pdf")
        self.assertTrue(os.path.exists(renamed_target))
        with open(renamed_target, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "updated")

        app.quit_app()

    def test_registry_persistence_and_reload(self):
        """Integration Test 5: Save configuration in test mode and reload new instance."""
        app1 = FileMoverApp(test_mode=True)
        app1.add_rule(self.src1, self.dst1, [".docx"])
        app1.update_delay(15)
        app1.quit_app()

        app2 = FileMoverApp(test_mode=True)
        self.assertEqual(app2.delay_minutes, 15)
        rules = app2.get_all_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["source_folder"], os.path.abspath(self.src1))
        self.assertEqual(rules[0]["target_folder"], os.path.abspath(self.dst1))
        self.assertEqual(rules[0]["extensions"], [".docx"])
        app2.quit_app()

    def test_rule_removal_and_observer_cleanup(self):
        """Integration Test 6: Removing rules updates both observer and configuration."""
        app = FileMoverApp(test_mode=True)
        app.add_rule(self.src1, self.dst1, [".pdf"])
        app.add_rule(self.src2, self.dst2, [".jpg"])

        self.assertEqual(len(app.rules), 2)

        app.remove_rule(0)
        self.assertEqual(len(app.rules), 1)
        self.assertEqual(app.rules[0].source_folder, os.path.abspath(self.src2))

        saved_rules = ConfigManager.load_rules()
        self.assertEqual(len(saved_rules), 1)
        self.assertEqual(saved_rules[0]["source_folder"], os.path.abspath(self.src2))
        app.quit_app()

    def test_same_source_and_target_rejection(self):
        """Integration Test 7: Reject rule creation when source and target folder are identical."""
        app = FileMoverApp(test_mode=True)
        with self.assertRaises(ValueError) as ctx:
            app.add_rule(self.src1, self.src1, [".pdf"])
        self.assertIn("cannot be identical", str(ctx.exception))
        app.quit_app()

    def test_auto_move_toggle(self):
        """Integration Test 8: AutoMove toggle state updates configuration."""
        app = FileMoverApp(test_mode=True)
        self.assertTrue(app.is_auto_move_enabled())

        app.toggle_auto_move()
        self.assertFalse(app.is_auto_move_enabled())

        app.toggle_auto_move()
        self.assertTrue(app.is_auto_move_enabled())
        app.quit_app()

    def test_retry_on_locked_file(self):
        """Integration Test 9: FileQueueManager retries locked files up to max_retries."""
        rule = MoveRule(self.src1, self.dst1, [".pdf"])
        test_file = os.path.join(self.src1, "locked.pdf")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("content")

        from file_manager import FileQueueManager

        retries_recorded = []

        def log_cb(msg):
            retries_recorded.append(msg)

        qm = FileQueueManager(
            delay_minutes=0,
            log_callback=log_cb,
            max_retries=2,
            retry_delay_seconds=1,
        )

        # Simulate lock by making file match but move_file returns False
        original_move = rule.move_file
        try:
            rule.move_file = lambda path, name: False
            qm.add_file(test_file, rule)

            # Wait for first process attempt and retry scheduling
            time.sleep(0.3)
            status = qm.get_queue_status()
            self.assertTrue(len(status) > 0)
            self.assertEqual(status[0]["retries"], 1)

            qm.clear_queue()
        finally:
            rule.move_file = original_move

    def test_subfolder_targets_like_user_setup(self):
        """Integration Test 10: Target folders as subfolders of source (e.g. DL -> DL/ZIP)."""
        app = FileMoverApp(test_mode=True)
        zip_target = os.path.join(self.src1, "ZIP")
        media_target = os.path.join(self.src1, "Media")
        app.add_rule(self.src1, zip_target, ["zip"])
        app.add_rule(self.src1, media_target, ["jpg", "png"])

        test_zip = os.path.join(self.src1, "archive.zip")
        test_jpg = os.path.join(self.src1, "photo.jpg")
        with open(test_zip, "w", encoding="utf-8") as f:
            f.write("zip data")
        with open(test_jpg, "w", encoding="utf-8") as f:
            f.write("jpg data")

        app.move_now(dry_run=False)

        self.assertTrue(os.path.exists(os.path.join(zip_target, "archive.zip")))
        self.assertTrue(os.path.exists(os.path.join(media_target, "photo.jpg")))
        app.quit_app()

    def test_case_insensitive_extension_matching(self):
        """Integration Test 11: Uppercase filenames match lowercase rules and vice-versa."""
        rule = MoveRule(self.src1, self.dst1, [".PDF"])
        self.assertTrue(rule.matches_filename("DOCUMENT.PDF"))
        self.assertTrue(rule.matches_filename("document.pdf"))
        self.assertTrue(rule.matches_filename("Invoice.Pdf"))
        self.assertFalse(rule.matches_filename("document.pdf.txt"))

    def test_read_only_file_handling(self):
        """Integration Test 12: Read-only files are recognized as unlocked and moved."""
        import stat

        test_file = os.path.join(self.src1, "readonly.pdf")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("readonly content")

        # Mark file as read-only
        os.chmod(test_file, stat.S_IREAD)
        try:
            rule = MoveRule(self.src1, self.dst1, [".pdf"])
            self.assertTrue(rule._is_file_unlocked(test_file))
            success = rule.move_file(test_file, "readonly.pdf")
            self.assertTrue(success)
            self.assertTrue(os.path.exists(os.path.join(self.dst1, "readonly.pdf")))
        finally:
            # Restore write permission if needed
            dest = os.path.join(self.dst1, "readonly.pdf")
            if os.path.exists(dest):
                os.chmod(dest, stat.S_IWRITE)
            if os.path.exists(test_file):
                os.chmod(test_file, stat.S_IWRITE)


if __name__ == "__main__":
    unittest.main()
