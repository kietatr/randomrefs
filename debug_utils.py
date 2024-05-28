from PyQt5.QtWidgets import QMessageBox, QWidget

def debugLog(message, title="Debug Log"):
    QMessageBox.information(QWidget(), title, str(message))

def warningLog(message, title="Warning"):
    QMessageBox.information(QWidget(), title, str(message))