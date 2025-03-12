import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        _PATH = 'HIER PFAD EINGEBEN'
        import sys
        app.log(f'sys executable: {sys.executable}')
        if not _PATH in sys.path:
            sys.path.append(_PATH)
            pass
        app.log(f'sys path: {sys.path[-1]}')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
