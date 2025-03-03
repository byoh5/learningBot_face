from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets
msg_icon_warning = 1
msg_icon_critical = 2
msg_icon_question = 3
msg_icon_information = 4

class Msg(QtCore.QObject):
    def __init__(self, title, text, icon):
        super().__init__()

        msg = QMessageBox()
        if msg_icon_warning == icon:
            msg.setIcon(QMessageBox.Warning)
        elif msg_icon_critical == icon:
            msg.setIcon(QMessageBox.critical)
        elif msg_icon_question == icon:
            msg.setIcon(QMessageBox.question)
        elif msg_icon_information == icon:
            msg.setIcon(QMessageBox.information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


