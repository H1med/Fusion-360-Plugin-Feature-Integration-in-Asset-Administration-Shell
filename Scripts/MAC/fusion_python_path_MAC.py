import adsk.core, adsk.fusion, adsk.cam, traceback, re, sys

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        _PATH = '/Users/hamed/uni/bachelorarbeit/fusion/py39_fusion/lib/python3.12/site-packages'

        executable_path = sys.executable
        match = re.search(r'production/([^/]+)/', executable_path)
        if match:
            fusion_id = match.group(1)
            app.log(f'Fusion ID: {fusion_id}')
        else:
            app.log('Fusion ID nicht gefunden.')
        if not _PATH in sys.path:
            sys.path.append(_PATH)
            pass
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
