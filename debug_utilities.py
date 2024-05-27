from PyQt5.QtWidgets import QMessageBox, QWidget

def debugLog(message):
    QMessageBox.information(QWidget(), "Warnning", message)