import krita
from pathlib import Path
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QUrl
from PyQt5.QtGui import QImage

from .debug_utils import debugLog, warningLog

# Adapted from:
# https://github.com/duskydd/Krita-Photobash-Images-Plugin/blob/f952b0eb4499f37bc2973edc7da84dcfee2dda00/photobash_images/photobash_images_docker.py#L418C9-L418C22
def importAsPaintLayer(imageFilePath, x: int, y: int, width: int, height: int):
    if not Path(imageFilePath).exists:
        warningLog(f'No image exists with path {imageFilePath}')
        return
    
    activeDoc = krita.Krita.instance().activeDocument()
    if activeDoc is None:
        warningLog("No document is open at this moment")
        return

    scaledImage = QImage(imageFilePath).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    # Ensure that information can be safely transferred between applications, and copied around within the same application
    mimedata = QMimeData()
    mimedata.setUrls([QUrl().fromLocalFile(imageFilePath)])
    mimedata.setImageData(scaledImage)

    # Copy image data into a new Paint Layer
    newLayer = activeDoc.createNode(Path(imageFilePath).name, "paintlayer")

    imageByteArray = scaledImage.bits()
    imageByteArray.setsize(scaledImage.byteCount())
    newLayer.setPixelData(QByteArray(imageByteArray.asstring()), 0, 0, scaledImage.width(), scaledImage.height())

    newLayer.move(x, y)

    root = activeDoc.rootNode()
    root.addChildNode(newLayer, None)

    krita.Krita.instance().activeDocument().refreshProjection()
    