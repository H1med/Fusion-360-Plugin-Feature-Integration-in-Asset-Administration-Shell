import adsk.core, adsk.fusion, adsk.cam, traceback

def run():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        _PATH = '/Users/hamed/uni/bachelorarbeit/fusion/py39_fusion/lib/python3.12/site-packages'
        import sys
        app.log(f'sys executable: {sys.executable}')      # get Fusion's python path
        if not _PATH in sys.path:
            sys.path.append(_PATH)                        # add module's path to sys.path if it doesn't
            pass
        app.log(f'sys path: {sys.path[-1]}')              # print last path in sys.path
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
