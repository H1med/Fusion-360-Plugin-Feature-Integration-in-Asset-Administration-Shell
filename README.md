# Einrichtung der virtuellen Umgebung für das Fusion-AddIn

Dieses Dokument erklärt, wie man eine virtuelle Umgebung für die Python-Installation von Autodesk Fusion einrichtet, um das AddIn `feature_erkennung_addin` ausführen zu können.

## Voraussetzungen

- Autodesk Fusion installiert
- Python und `virtualenv` installiert

## Schritte zur Einrichtung

### 1. Ermitteln des Python-Pfads von Fusion

Führen Sie das Skript `fusion_python_path.py` in Fusion aus, um den Pfad zur Python-Installation von Fusion zu ermitteln. Sie können Skripte und AddIns mit dem shortcut `shift + s` zu Fusion hinzufügen.

### 2. Ermittlung des Pfades der Python Installation von Fusion
 
Nach der Ausführung des Skripts wird der Pfad zur Python-Installation in der Konsole von Fusion angezeigt.

##### Windows
`sys executable :C:\Users\<username>\AppData\Local\Autodesk\webdeploy\production\...\Python\python.exe`

##### MacOS
`sys executable: /Users/<username>/Library/Application Support/Autodesk/webdeploy/production/.../Autodesk Fusion.app/Contents/MacOS/Autodesk Fusion`

##### Hinweis: Der Ausgegebene Pfad für MacOS ist nicht korrekt. Der tatsächliche Pfad lautet:
`/Users/<username>/Library/Application\ Support/Autodesk/webdeploy/production/.../Autodesk\ Fusion.app/Contents/Frameworks/Python.framework/Versions/3.12/bin/python`

### 3. Erstellen der virtuellen Umgebung
Erstellen sie einen Ordner names `Fusion` an einem Pfad ihrer Wahl und navegieren sie zu dem Ordner mit:
`cd Fusion`
Verwenden Sie den ermittelten Pfad, um eine virtuelle Umgebung zu erstellen:
`virtualenv -p <FUSION_PYTHON_PFAD> py39_fusion`
Aktivieren Sie die virtuelle Umgebung:
#### Windows
`.\py39_fusion\Scripts\activate`
#### MacOS/Linux
`source py39_fusion/bin/activate`

### 4. Installieren der Module
Installieren Sie das requests Modul mit pip:
`pip install requests`

### 5. Erneutes Ausführen des Skripts
Führen Sie das Skript `fusion_python_path.py` erneut aus, um den `sys path` zu erhalten. Dieser Pfad muss im Skript unter der Variable `_PATH` eingesetzt werden.
```python
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        _PATH = <HIER DEN PFAD EINFÜGEN>
        import sys
        app.log(f'sys executable: {sys.executable}')      
        if not _PATH in sys.path:
            sys.path.append(_PATH)                        
            pass
        app.log(f'sys path: {sys.path[-1]}')              
        sys.path
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
```
### 6. AddIn ausführen
Starten Sie anschließend Fusion neu, um die Änderungen zu übernehmen.
Nach dem Neustart können Sie das AddIn `feature_erkennung_addin` ausführen in dem Sie es mit `shift + s` unter AddIns hinzufügen und ausführen.
