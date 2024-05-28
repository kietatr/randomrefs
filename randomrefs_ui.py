import krita
import random
from PyQt5.QtCore import QDirIterator, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFrame, 
    QFormLayout, QLineEdit, QSpinBox, QPushButton,
    QFileDialog, QLabel,
)

from . import appConfig
from . import image_utils
from .colorButton import ColorButton
from .debug_utils import debugLog, warningLog

class RandomRefsDialog():

    def __init__(self):
        self.refImagePaths: list[str] = []

        self.mainDialog = QDialog()
        self.mainDialog.setWindowTitle("Random References")
        self.mainDialog.resize(500, 70)

        self.dialogUI()

    def dialogUI(self):
        self.mainLayout = QVBoxLayout()
        self.refFolderLayout = QVBoxLayout()
        self.formLayout = QFormLayout()

        self.refFolderInput = QLineEdit()
        self.refFolderInput.setPlaceholderText("C:/path/to/your/reference/folder")
        self.refFolderInfo = QLabel(f'{len(self.refImagePaths)} images in this folder')
        self.refFolderButton = QPushButton("Select Reference Folder")
        self.refFolderButton.setIcon(krita.Krita.instance().icon('folder'))

        self.refFolderLayout.addWidget(self.refFolderInput)
        self.refFolderLayout.addWidget(self.refFolderInfo)
        self.refFolderLayout.addWidget(self.refFolderButton)

        self.backgroundColorButton = ColorButton(color=appConfig.defaultBackgroundColor)

        self.rowSizeSpinBox = QSpinBox()
        self.rowSizeSpinBox.setRange(100,2000)
        self.rowSizeSpinBox.setSingleStep(100)
        self.rowSizeSpinBox.setProperty("value", appConfig.defaultRowSize)
        self.colSizeSpinBox = QSpinBox()
        self.colSizeSpinBox.setRange(100,2000)
        self.colSizeSpinBox.setSingleStep(100)
        self.colSizeSpinBox.setProperty("value", appConfig.defaultColSize)

        self.paddingSpinBox = QSpinBox()
        self.paddingSpinBox.setRange(0,200)
        self.paddingSpinBox.setSingleStep(10)
        self.paddingSpinBox.setProperty("value", appConfig.defaultPadding)

        self.rowSpinBox = QSpinBox()
        self.rowSpinBox.setRange(1,10)
        self.rowSpinBox.setProperty("value", 2)
        self.colSpinBox = QSpinBox()
        self.colSpinBox.setRange(1,10)
        self.colSpinBox.setProperty("value", 2)

        self.formLayout.addRow("Reference Folder", self.refFolderLayout)
        self.formLayout.addRow("Canvas Background Color", self.backgroundColorButton)
        self.formLayout.addRow("Row Size", self.rowSizeSpinBox)
        self.formLayout.addRow("Column Size", self.colSizeSpinBox)
        self.formLayout.addRow("Padding", self.paddingSpinBox)
        self.formLayout.addRow("Rows", self.rowSpinBox)
        self.formLayout.addRow("Columns", self.colSpinBox)

        self.samplesInfo = QLabel(f'{self.rowSpinBox.value() * self.colSpinBox.value()} random images will be selected out of {len(self.refImagePaths)} images')
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
        self.rowSpinBox.valueChanged.connect(self.updateInfoTexts)
        self.colSpinBox.valueChanged.connect(self.updateInfoTexts)
        self.createDocumentButton.clicked.connect(self.createDocument)

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
            if it.filePath().endswith(appConfig.supportedImageExtensions):
                self.refImagePaths.append(it.filePath())
            it.next()
            
        self.updateInfoTexts()

    def updateInfoTexts(self):
        self.refFolderInfo.setText(f'{len(self.refImagePaths)} images in this folder')
        self.samplesInfo.setText(f'{self.rowSpinBox.value() * self.colSpinBox.value()} random images will be selected out of {len(self.refImagePaths)} images')

    def createBackgroundColorLayer(self):
        backgroundColor = self.backgroundColorButton.color()
        
        activeDoc = krita.Krita.instance().activeDocument()
        if activeDoc is None:
            warningLog("No document is open at this moment")
            return
        
        layerConfig = krita.InfoObject();
        layerConfig.setProperty("color", backgroundColor)
        layerSelection = krita.Selection();
        layerSelection.select(0, 0, activeDoc.width(), activeDoc.height(), 255)
        
        bgFillLayer = activeDoc.createFillLayer("Background Fill", "color", layerConfig, layerSelection)

        root = activeDoc.rootNode();
        bottommostLayer = root.childNodes()[0]
        root.addChildNode(bgFillLayer, bottommostLayer)
        root.removeChildNode(bottommostLayer)

        activeDoc.refreshProjection()

    def createDocument(self):
        if len(self.refImagePaths) <= 0:
            warningLog("You must select a reference folder first")
            return
        
        # Randomly select images from ref folder
        numRows = self.rowSpinBox.value()
        numCols = self.colSpinBox.value()
        numSamples = numRows * numCols
        randomRefImagePaths = random.sample(self.refImagePaths, numSamples)

        # Create a document based on rows, columns, and padding
        rowSize = self.rowSizeSpinBox.value()
        colSize = self.colSizeSpinBox.value()
        padding = self.paddingSpinBox.value()
        docWidth = 2 * numCols * colSize + padding * (numCols * 2 + 1)
        docHeight = numRows * rowSize + padding * (numRows + 1)
        newDocument = krita.Krita.instance().createDocument(docWidth, docHeight, "New Document", "RGBA", "U8", "", appConfig.documentDPI)
        newDocument.setBackgroundColor(QColor(self.backgroundColorButton.color()))
        krita.Krita.instance().activeWindow().addView(newDocument)

        self.createBackgroundColorLayer()

        image_utils.importAndArrangeImages(randomRefImagePaths, numRows, numCols, rowSize, colSize, padding, docWidth)

        # Close the dialog so that the canvas can display the latest results
        self.mainDialog.done(0)
    