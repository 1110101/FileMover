# FileMover Entwicklerdokumentation

Dieses Dokument beschreibt die Architektur, Konventionen und Entwicklungsrichtlinien für FileMover.

## Architektur

FileMover ist eine Windows-Hintergrundanwendung zur automatisierten Organisation von Dateiverzeichnissen.

* **Hauptprozess (`move.py`):** Initialisiert DPI-Awareness, startet die System-Tray-Integration mit Pystray und verwaltet den Tkinter-Event-Loop im Haupt-Thread.
* **Konfiguration (`config.py`):** Verwaltet die Anwendungsdaten in der Windows-Registry unter `HKCU\Software\FileMover\Config` sowie den Autostart unter `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Beinhaltet einen isolierten Testmodus für Unit- und Integrationstests.
* **Dateiverwaltung (`file_manager.py`):**
  * `FileObserverManager`: Koordiniert Watchdog-Observer pro Quellverzeichnis. Unterstützt mehrere Regeln für denselben Quellordner über einen zentralen Event-Handler.
  * `FileEventHandler`: Fängt Dateierstellungs-, Änderungs- und Umbenennungsereignisse (`on_moved`) ab. Letzteres stellt sicher, dass abgeschlossene Browser-Downloads zuverlässig erkannt werden.
  * `FileQueueManager`: Verwaltet zeitverzögerte Aktionen mit Wiederholungslogik (`max_retries`) für temporär gesperrte Dateien.
  * `MoveRule`: Führt Prüfungen auf Dateisperren, Erweiterungsfilter und automatische Kollisionsauflösung (`datei (1).ext`) durch.
* **Benutzeroberfläche (`gui.py`):** Tkinter/TTK-Oberfläche mit sicherem Regel-Bearbeitungsmodus und asynchroner Ausführung manueller Verschiebevorgänge.

## Qualitätsstandards

* **Stilrichtlinien für Texte:** 
  * Keine dekorativen Emojis vor Menüs oder Überschriften.
  * Keine Gedankenstriche im Fließtext.
  * Keine Wortpaare mit Kaufmanns-Und.
  * Keine Einschübe in Klammern.
* **Kommentare und Dokumentation:**
  * Kommentare ausschließlich für nicht offensichtliche Designentscheidungen, Workarounds oder komplexe Zusammenhänge einsetzen.
  * Selbsterklärender Code benötigt keine Begleitkommentare wie Abschnittstrenner oder Code-Nacherzählungen.
* **Linter und Formatierung:** 
  * Codeformatierung und statische Typprüfung mit Ruff (`ruff check .`, `ruff format .`).
* **Testausführung:**
  * Tests laufen strikt im isolierten Testmodus (`ConfigManager.set_test_mode(True)`), um reale Produktivdaten des Nutzers zu schützen.
* **Git-Hooks:**
  * Husky mit Pre-Commit-Hook (`npm run check`: Linter, Formatierung und 14 Tests).
  * Commit-Message-Prüfung auf Conventional Commits (`feat:`, `fix:`, `docs:` usw.).
  * Pre-Push-Hook zur Absicherung des Push-Vorgangs.

## Build und Packaging

1. **Abhängigkeiten installieren:**
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. **Standalone-Executable erstellen:**
   ```powershell
   pyinstaller move.spec
   ```
3. **Setup-Installer erstellen:**
   ```powershell
   iscc installer.iss
   ```
