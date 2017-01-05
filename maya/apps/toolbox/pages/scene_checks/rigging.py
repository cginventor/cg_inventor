import cg_inventor.sys.lib.qt.widgets.scene_check     as scene_check

import cg_inventor.maya.apps.toolbox.page as page


TITLE    = 'Scene Checks'
SUBTITLE = 'Rigging' 


class RiggingChecks(page.Page):
    def __init__(self):
        page.Page.__init__(self)
        self.title    = TITLE
        self.subtitle = SUBTITLE
    