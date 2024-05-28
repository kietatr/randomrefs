import krita
from pathlib import Path
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QUrl
from PyQt5.QtGui import QImage

from .debug_utils import debugLog, warningLog

def importAndArrangeImages(imagePaths: list[str], numRows: int, numCols: int, rowSize: int, colSize: int, padding: int, documentWidth: int):
    # Import the images as paint layers, then arrange them in a grid
    for row in range(numRows):
        for col in range(numCols):
            i = row * numCols + col
            scaledImage, scaledImageName = getImage(imagePaths[i], colSize, rowSize)

            # Empty space in the center (ref images arranged to the left and right sides)
            if numCols == 2 and col == 1:
                x = documentWidth - padding - scaledImage.width()
                y = (row + 1) * padding + (row) * rowSize 
            # Equal grid with ref images on the left of each grid cell
            else:
                x = (2 * col + 1) * padding + (2 * col) * colSize
                y = (row + 1) * padding + (row) * rowSize

            importQImageAsPaintLayer(scaledImage, scaledImageName, x, y)
    
    krita.Krita.instance().activeDocument().refreshProjection()

def getImage(imageFilePath: str, width: int, height: int) -> tuple[QImage, str]:
    """
    Get the image scaled to specified width and height (while maintaining aspect ratio)
    """
    if not Path(imageFilePath).exists:
        warningLog(f'No image exists with path {imageFilePath}')
        return
    
    scaledImage = QImage(imageFilePath).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    # Ensure that information can be safely transferred between applications, and copied around within the same application
    mimedata = QMimeData()
    mimedata.setUrls([QUrl().fromLocalFile(imageFilePath)])
    mimedata.setImageData(scaledImage)

    return (scaledImage, imageFilePath)

def importQImageAsPaintLayer(scaledImage: QImage, scaledImageName: str, x: int, y: int) -> None:
    activeDoc = krita.Krita.instance().activeDocument()
    if activeDoc is None:
        warningLog("No document is open at this moment")
        return

    # Copy image data into a new Paint Layer
    newLayer = activeDoc.createNode(scaledImageName, "paintlayer")
    imageByteArray = scaledImage.bits()
    imageByteArray.setsize(scaledImage.byteCount())
    newLayer.setPixelData(QByteArray(imageByteArray.asstring()), 0, 0, scaledImage.width(), scaledImage.height())

    newLayer.move(x, y)

    # Make the new layer show up in the document
    root = activeDoc.rootNode()
    root.addChildNode(newLayer, None)

    # krita.Krita.instance().activeDocument().refreshProjection()


# Adapted from:
# https://github.com/duskydd/Krita-Photobash-Images-Plugin/blob/f952b0eb4499f37bc2973edc7da84dcfee2dda00/photobash_images/photobash_images_docker.py#L418C9-L418C22
def importImagePathAsPaintLayer(imageFilePath: str, x: int, y: int, width: int, height: int) -> None:
    scaledImage, imageFilePath = getImage(imageFilePath, width, height)

    activeDoc = krita.Krita.instance().activeDocument()
    if activeDoc is None:
        warningLog("No document is open at this moment")
        return

    # Copy image data into a new Paint Layer
    newLayer = activeDoc.createNode(Path(imageFilePath).name, "paintlayer")
    imageByteArray = scaledImage.bits()
    imageByteArray.setsize(scaledImage.byteCount())
    newLayer.setPixelData(QByteArray(imageByteArray.asstring()), 0, 0, scaledImage.width(), scaledImage.height())

    newLayer.move(x, y)

    # Make the new layer show up in the document
    root = activeDoc.rootNode()
    root.addChildNode(newLayer, None)

    krita.Krita.instance().activeDocument().refreshProjection()
