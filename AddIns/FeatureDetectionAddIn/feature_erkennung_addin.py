import adsk.core, adsk.fusion, adsk.cam, traceback, os, json

from . import fusion_python_path
fusion_python_path.run()
from . import feature_erkennung

_app = None
_ui = None
_handlers = []

def run(context):
    global _app, _ui
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Palette erstellen
        palette_id = 'FeatureErkennungPalette'
        palette_title = 'Feature Erkennung'
        html_file = os.path.join(os.path.dirname(__file__), 'palette.html')
        html_file = 'file:///'+html_file.replace('\\','/')

        palette = _ui.palettes.itemById(palette_id)
        if not palette:
            palette = _ui.palettes.add(
                palette_id,
                palette_title,
                html_file,
                True,  # Show close button
                True,  # Is visible
                True   # Show initially
            )

        onHTMLEvent = MyHTMLEventHandler()
        palette.incomingFromHTML.add(onHTMLEvent)
        _handlers.append(onHTMLEvent)

        # Palette an der rechten Seite andocken
        palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

    except:
        if _ui:
            _ui.messageBox('Fehler:\n{}'.format(traceback.format_exc()))

def stop(context):
    global _app, _ui
    try:
        _ui = _app.userInterface
        palette = _ui.palettes.itemById('FeatureErkennungPalette')
        if palette:
            palette.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed to stop:\n{}'.format(traceback.format_exc()))


class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)
            if htmlArgs.action == 'starteFeatureErkennung':
                user_input = json.loads(htmlArgs.data)
                feature_erkennung.run(user_input)
        except:
            _ui.messageBox('Fehler:\n{}'.format(traceback.format_exc()))
