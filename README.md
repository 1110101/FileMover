# FileMover

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/1110101/FileMover/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Eine Windows-Systray-Anwendung zum automatischen Verschieben von Dateien basierend auf Dateiendungen mit Timer-basierter Verzögerung.

## Beschreibung

FileMover überwacht Quellordner in Echtzeit und verschiebt Dateien mit bestimmten Endungen nach einer konfigurierbaren Wartezeit automatisch in Zielordner. Die Anwendung läuft im Hintergrund im System Tray und bietet eine optionale GUI zur Konfiguration.

## Features

- 🖥️ **System Tray Integration**: Läuft unsichtbar im Hintergrund, jederzeit über Systray-Icon erreichbar
- ⏱️ **Timer-basiertes Verschieben**: Konfigurierbare Wartezeit (in Minuten) bevor Dateien verschoben werden
- 🚀 **Windows-Autostart**: Optional beim Windows-Start automatisch starten
- 🔄 **Echtzeit-Überwachung**: Watchdog überwacht Ordner und erkennt neue Dateien sofort
- 🎛️ **Auto-Move Toggle**: Automatisches Verschieben ein-/ausschalten ohne Regeln zu löschen
- 🧪 **Dry Run Mode**: Test-Modus zum Prüfen was verschoben würde, ohne Dateien zu bewegen
- 📁 **Mehrere Regeln**: Beliebig viele Verschiebe-Regeln konfigurierbar
- 🎯 **Dateifilter**: Filterung nach Dateiendungen (z.B. `.pdf`, `.jpg`, `.docx`)
- 💾 **Persistente Konfiguration**: Speicherung aller Einstellungen in der Windows-Registry
- 📝 **Activity Log**: Detaillierte Protokollierung aller Aktionen im GUI
- ⚡ **Manuelle Ausführung**: "Move Now" - sofortiges Verschieben ohne Wartezeit
- 🔒 **File-Lock-Check**: Verhindert Verschieben von noch in Bearbeitung befindlichen Dateien
- 📐 **Resizable GUI**: Vergrößerbares Fenster mit anpassbaren Listen und Logs
- 🐛 **Crash-Logging**: Automatische Fehlerprotokollierung bei unerwarteten Abstürzen

## Voraussetzungen

- Windows Betriebssystem
- Python 3.7 oder höher

## Installation

1. Repository klonen oder herunterladen:
```bash
git clone <repository-url>
cd FileMover
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

## Verwendung

### Anwendung starten

**Als Python-Script:**
```bash
python move.py
```

**Als .exe ausführen:**
```
dist\move.exe
```

Die App startet im System Tray (Taskleiste rechts unten). Klicke auf das Icon für Optionen.

### System Tray Menü

- **Öffnen**: Öffnet das Konfigurations-Fenster (alternativ: Doppelklick auf Icon)
- **Beenden**: Schließt die Anwendung komplett

### Konfiguration

1. **Doppelklick auf Systray-Icon** oder Rechtsklick → "Öffnen"
2. Im Konfigurationsfenster:

#### Neue Regel erstellen

1. **Source Folder**: Wähle den Quellordner, der überwacht werden soll
2. **Target Folder**: Wähle den Zielordner, wohin die Dateien verschoben werden
3. **File Extensions**: Gebe die Dateiendungen ein (mit Komma getrennt, z.B. `.pdf, .jpg, .png`)
4. Klicke auf **"Add Rule"**

#### Einstellungen & Aktionen

- **Wait Time**: Lege fest, wie lange nach Datei-Erkennung gewartet werden soll (1-60 Minuten)
  - Klicke auf **"Update"** zum Speichern
- **Auto-Move Toggle**: Schalte automatisches Verschieben ein/aus
  - 🟢 Grün = Aktiv, Dateien werden automatisch verschoben
  - 🔴 Rot = Inaktiv, Dateien werden nur in Warteschlange gehalten
- **Autostart Toggle**: Windows-Autostart aktivieren/deaktivieren
  - ✓ ON = App startet mit Windows
  - OFF = Manueller Start erforderlich

#### Aktionen

- **Dry Run**: Aktiviere diesen Modus für Test-Läufe (zeigt nur was passieren würde)
- **Show Waiting Files**: Zeige alle Dateien die aktuell in der Warteschlange sind
- **Move Now**: Verschiebe alle wartenden Dateien sofort (ignoriert Timer)

#### Regel bearbeiten

- Doppelklick auf eine Regel in der Liste lädt sie zur Bearbeitung

#### Regel löschen

- Wähle eine Regel aus und klicke auf **"Remove Selected"**

### GUI schließen

Das Schließen des Fensters beendet die App NICHT - sie läuft weiter im System Tray. Um die App komplett zu beenden: Rechtsklick auf Systray-Icon → "Beenden"

## Beispiel-Workflow

1. Quellordner: `D:/Downloads`
2. Zielordner: `D:/Dokumente/PDFs`
3. Endungen: `.pdf`
4. Delay: `5` Minuten
5. **Ergebnis**: Wenn eine PDF-Datei in Downloads auftaucht, wird sie nach 5 Minuten automatisch nach `D:/Dokumente/PDFs` verschoben

**Warum Delay?** Dies verhindert, dass Dateien verschoben werden, die noch heruntergeladen oder bearbeitet werden.

## .exe erstellen (Build)

Die Anwendung kann mit dem mitgelieferten Build-Script kompiliert werden:

**Windows:**
```bash
build.bat
```

Das Script:
1. Installiert automatisch alle Dependencies
2. Führt PyInstaller mit der move.spec-Konfiguration aus
3. Erstellt die .exe im `dist`-Ordner

**Manuell bauen:**
```bash
pip install -r requirements.txt
pyinstaller move.spec
```

## Konfiguration & Datenspeicherung

Die Konfiguration wird persistent in der Windows-Registry gespeichert:

**Einstellungen** (`HKEY_CURRENT_USER\Software\FileMover\Config`):
- `move_rules` - Alle Verschiebe-Regeln
- `delay_minutes` - Wartezeit in Minuten
- `auto_move_enabled` - Status des Auto-Move-Toggles

**Autostart** (`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`):
- `FileMover` - Pfad zur Anwendung (wenn Autostart aktiviert)

**Crash-Logs**: `filemover_crash.log` im Programmverzeichnis

## Technische Details

- **GUI**: tkinter
- **System Tray**: pystray
- **Icons**: Pillow (PIL)
- **Dateiüberwachung**: watchdog
- **Queue-System**: Threading mit individuellen Timern pro Datei
- **Speicherung**: Windows Registry (winreg)
- **Build**: PyInstaller

## Architektur

```
move.py          - Haupteinstiegspunkt, Systray-Integration
gui.py           - GUI-Komponenten (tkinter)
file_manager.py  - FileQueueManager, FileEventHandler, MoveRule
config.py        - Registry-Operationen, Konfigurationsverwaltung
```

## Abhängigkeiten

- `watchdog` - Datei-System-Überwachung
- `pystray` - System Tray Integration
- `Pillow` - Icon-Erstellung
- `tkinter` - GUI (in Python enthalten)

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

## Hinweise

- Die Anwendung wurde für Windows entwickelt
- Stelle sicher, dass du Schreibrechte für Ziel- und Quellordner hast
- Bei Verwendung von Netzlaufwerken kann die Überwachung langsamer sein

