# FileMover - Schnellstart

## Installation & Start

### 1. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 2. Anwendung starten
```bash
python move.py
```

Die App erscheint im System Tray (rechts unten in der Taskleiste).

## Erste Schritte

### 1. GUI öffnen
- **Doppelklick** auf das FileMover-Icon im System Tray
- Oder: **Rechtsklick** → "Öffnen"

### 2. Delay einstellen
- Standardwert ist 5 Minuten
- Passe den Wert an (z.B. 1 Minute für Tests)
- Klicke **"Update Delay"**

### 3. Erste Regel hinzufügen

**Beispiel: PDFs aus Downloads verschieben**

1. **Source Folder**: `C:\Users\IhrName\Downloads`
2. **Target Folder**: `C:\Users\IhrName\Documents\PDFs`
3. **File Extensions**: `.pdf`
4. Klicke **"Add Rule"**

### 4. Testen

**Option A: Manuell testen**
- Klicke **"Move Now"** → Dateien werden sofort verschoben

**Option B: Automatisch testen**
- Lege eine PDF-Datei in den Downloads-Ordner
- Warte die eingestellte Delay-Zeit
- Die Datei wird automatisch verschoben

**Queue überprüfen:**
- Klicke **"Refresh Queue"** um wartende Dateien zu sehen

## Autostart aktivieren

1. **Rechtsklick** auf System Tray Icon
2. Klicke **"Autostart"** um zu aktivieren
3. FileMover startet jetzt automatisch mit Windows

## Tipps

### Mehrere Dateitypen
```
.pdf, .docx, .xlsx, .pptx
```

### Bilder organisieren
- **Source**: `C:\Users\IhrName\Downloads`
- **Target**: `C:\Users\IhrName\Pictures\FromDownloads`
- **Extensions**: `.jpg, .jpeg, .png, .gif, .webp`

### Videos organisieren
- **Source**: `C:\Users\IhrName\Downloads`
- **Target**: `C:\Users\IhrName\Videos\FromDownloads`
- **Extensions**: `.mp4, .mkv, .avi, .mov`

## Executable erstellen

```bash
build.bat
```

Die `.exe` ist dann in `dist\move.exe`

## Fehlerbehebung

**App erscheint nicht im System Tray:**
- Prüfe ob Python-Prozess läuft (Task-Manager)
- Prüfe Konsolen-Output auf Fehler

**Dateien werden nicht verschoben:**
- Prüfe ob Source-Folder existiert
- Prüfe "Activity Log" in der GUI
- Klicke "Refresh Queue" um wartende Dateien zu sehen

**GUI reagiert nicht:**
- Schließe das Fenster (läuft weiter im Tray)
- Öffne erneut über System Tray Icon

## Die App beenden

**Komplett beenden:**
- **Rechtsklick** auf System Tray Icon
- Klicke **"Beenden"**

**Wichtig:** Das Schließen des GUI-Fensters beendet die App NICHT! Sie läuft weiter im Hintergrund.

