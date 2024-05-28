import krita
import random
from PyQt5.QtCore import QDirIterator, Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFrame, 
    QFormLayout, QLineEdit, QSpinBox, QPushButton,
    QFileDialog, QLabel,
)

from . import randomrefs
from .debug_utilities import debugLog

class RandomRefsDialog():

    def __init__(self):
        self.supportedImageExtensions = (".webp", ".png", ".jpg", ".jpeg", ".bmp", ".tiff")
        self.refImagePaths: list[str] = []

        self.mainDialog = QDialog()
        self.mainDialog.setWindowTitle("Random References")
        self.mainDialog.resize(500, 80)

        self.dialogUI()

    def dialogUI(self):
        self.mainLayout = QVBoxLayout()
        self.refFolderLayout = QVBoxLayout()
        self.formLayout = QFormLayout()

        self.refFolderInput = QLineEdit()
        self.refFolderInput.setPlaceholderText("C:/path/to/your/reference/folder")
        self.refFolderInfo = QLabel(f'{len(self.refImagePaths)} images in this folder')
        self.refFolderButton = QPushButton("Select Folder")
        self.refFolderButton.setIcon(krita.Krita.instance().icon('folder'))

        self.refFolderLayout.addWidget(self.refFolderInput)
        self.refFolderLayout.addWidget(self.refFolderInfo)
        self.refFolderLayout.addWidget(self.refFolderButton)

        self.rowSpinBox = QSpinBox()
        self.rowSpinBox.setRange(1,10)
        self.rowSpinBox.setProperty("value", 2)
        self.colSpinBox = QSpinBox()
        self.colSpinBox.setRange(1,10)
        self.colSpinBox.setProperty("value", 2)

        self.formLayout.addRow("", QLabel())  # empty row for extra spacing
        self.formLayout.addRow("Reference Folder", self.refFolderLayout)
        self.formLayout.addRow("", QLabel())
        self.formLayout.addRow("Rows", self.rowSpinBox)
        self.formLayout.addRow("Columns", self.colSpinBox)
        # self.formLayout.addRow("", QLabel())

        self.samplesInfo = QLabel(f'{self.rowSpinBox.value() * self.colSpinBox.value()} random images will be selected')
        self.samplesInfo.setAlignment(Qt.AlignHCenter)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.createDocumentButton = QPushButton("Create Document")
        self.createDocumentButton.setIcon(krita.Krita.instance().icon('media-playback-start'))

        self.mainLayout.addWidget(QLabel("First, select a folder containing your reference images. Then, click 'Create Document'"))
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.samplesInfo)
        self.mainLayout.addWidget(self.line)
        self.mainLayout.addWidget(self.createDocumentButton)
        self.mainDialog.setLayout(self.mainLayout)

        self.refFolderButton.clicked.connect(self.selectReferenceFolder)
        self.rowSpinBox.valueChanged.connect(self.updateSamplesInfo)
        self.colSpinBox.valueChanged.connect(self.updateSamplesInfo)

    def openDialog(self):
        self.mainDialog.show() 
        self.mainDialog.exec_()

    def selectReferenceFolder(self):
        title = "Choose a Folder that contains your Reference Images"
        dialogOptions = QFileDialog.ShowDirsOnly
        self.refFolderPath = QFileDialog.getExistingDirectory(parent=self.mainDialog, caption=title, options=dialogOptions)
        if self.refFolderPath is None or self.refFolderPath == "":
            return
        self.refFolderInput.setText(self.refFolderPath)
        self.getRefImagePaths()
        
    def getRefImagePaths(self):
        self.refImagePaths = []
        it = QDirIterator(self.refFolderPath, QDirIterator.Subdirectories)
        while(it.hasNext()):
            if it.filePath().endswith(self.supportedImageExtensions):
                self.refImagePaths.append(it.filePath())
            it.next()
            
        self.refFolderInfo.setText(f'{len(self.refImagePaths)} images in this folder')

    def updateSamplesInfo(self):
        self.samplesInfo.setText(f'{self.rowSpinBox.value() * self.colSpinBox.value()} random images will be selected')

    def randomlySelectImages(self):
        numSamples = self.rowSpinBox.value() * self.colSpinBox.value()
        randomRefImagePaths = random.sample(self.refImagePaths, numSamples)
