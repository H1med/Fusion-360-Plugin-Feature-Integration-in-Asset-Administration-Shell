# Einrichtung der virtuellen Umgebung für das Fusion-AddIn

Dieses Dokument erklärt, wie man eine virtuelle Umgebung für die Python-Installation von Autodesk Fusion einrichtet, um das AddIn `feature_erkennung_addin` ausführen zu können.

## Voraussetzungen

- Autodesk Fusion installiert
- Python und `virtualenv` installiert

## Schritte zur Einrichtung

### 1. Ermitteln des Python-Pfads von Fusion

Sie können Skripte und AddIns mit dem shortcut `shift + s` zu Fusion hinzufügen.
Führen Sie entweder das Skript `fusion_python_path_WINDOWS.py` oder `fusion_python_path_MAC.py` in Fusion aus, um den Pfad zur Python-Installation von Fusion zu ermitteln. Diese befinden sich im `Scripts`Ordner unter jeweils `WINDOWS`oder `MAC`.

### 2. Ermittlung des Pfades der Python Installation von Fusion
 
Nach der Ausführung des Skripts wird eine ID angezeigt. Diese ID ist für Schritt 3 erforderlich und muss in den folgenden Pfad eingefügt werden:

##### Windows
`C:\\Users\\<username>\\AppData\\Local\\Autodesk\\webdeploy\\production\\<HIER_DIE_ID_EINGEBEN>\\Python\\python.exe`

##### MacOS:
`/Users/<username>/Library/Application\ Support/Autodesk/webdeploy/production/<HIER_DIE_ID_EINGEBEN>/Autodesk\ Fusion.app/Contents/Frameworks/Python.framework/Versions/3.12/bin/python`

### 3. Erstellen der virtuellen Umgebung
Erstellen Sie einen Ordner names `Fusion` an einem Pfad ihrer Wahl und navigieren Sie zu dem Ordner mit:
`cd Fusion`
Verwenden Sie den ermittelten Pfad, um eine virtuelle Umgebung zu erstellen:
`python -m virtualenv -p <PFAD_AUS_SCHRITT_2> py39_fusion`
Aktivieren Sie die virtuelle Umgebung:
#### Windows
`.\py39_fusion\Scripts\activate`
#### MacOS/Linux
`source py39_fusion/bin/activate`

### 4. Installieren der Module
Installieren Sie das requests Modul mit pip:
`python -m pip install requests`

### 5. Ermitteln des `site-packages` -Pfads
Damit Fusion auf die in der virtuellen Umgebung installierten Python-Module zugreifen kann, muss der absolute Pfad zum `site-packages` -Ordner in das Skript eingetragen werden. Je nach Betriebssystem befindet sich der `site-packages` -Ordner an folgendem Speicherort:

#### Windows 
`\Fusion\py39_fusion\Lib\site-packages`

#### MacOS
`/Fusion/py39_fusion/lib/python3.12/site-packages`

#### Wichtig: Der absolute Pfad hängt davon ab, wo Sie den Ordner Fusion erstellt haben.

#### Windows: Den vollständigen Pfad kopieren
1. Öffnen Sie den Datei-Explorer und navigieren Sie zum `site-packages`-Ordner.
2. Klicken Sie in die Adressleiste des Explorers
3. Drücken Sie `Strg + C`, um den Pfad zu kopieren.   

#### **MacOS: Den vollständigen Pfad kopieren**  
1. Öffnen Sie das Terminal und navigieren SIe zum erstellten `Fusion` Ordner.  
2. Navigieren Sie dann zu:
`cd /py39_fusion/lib/python3.12/site-packages`
3. Führen Sie den folgenden Befehl aus, um den absoluten Pfad auszugeben:
`pdw`
4. Kopieren Sie den ausgegebenen Pfad

### 6. Pfad in das Skript eintragen
Öffnen Sie das Skript `fusion_python_path.py` mit dem Editor Ihrer Wahl und fügen Sie den Kopierten Pfad unter der Variable `_PATH` ein. Starten Sie anschließend erneut das Skript.
#### Hinweis Windows:
In Python müssen Backslashes (\\) durch doppelte Backslashes (\\\\) ersetzt werden.

#### Hinweis MacOS:
Falls der Pfad Leerzeichen enthält, müssen diese in Python mit einem \ (Backslash) escaped werden.

### 7. AddIn ausführen
Starten Sie anschließend Fusion neu, um die Änderungen zu übernehmen.
Nach dem Neustart können Sie das AddIn `feature_erkennung_addin` ausführen in dem Sie es mit `shift + s` unter AddIns hinzufügen und ausführen.

#### Wichtiger Hinweis
Nach jedem Neustart von Fusion muss einmal das Skript `fusion_python_path_WINDOWS.py` oder `fusion_python_path_MAC.py` erneut ausgeführt werden bevor das AddIn getartet wird.
