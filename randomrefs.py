# TODO: delete this line and the file PyKrita when publishing
from .PyKrita import *  # for autocomplete 

import krita
from . import randomrefs_dialog


class RandomRefsExtension(krita.Extension):

    def __init__(self, parent):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("random_refs", "Random References", "tools/scripts")
        action.triggered.connect(self.openDialog)

    def openDialog(self):
        self.randomrefsdialog = randomrefs_dialog.RandomRefsDialog()
        self.randomrefsdialog.openDialog()

