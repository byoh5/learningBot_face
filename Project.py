from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Signal
import os
import shutil

import popup_msg

class Project(QtCore.QObject):
    imgClass_signal_comboChg = Signal()
    imgClass_signal_groupEnable = Signal(int)
    def __init__(self,upper_window,x,y,w,h,c_th_IpCamera, c_Ipset):
        super().__init__()
        self.group= QtWidgets.QGroupBox(upper_window)
        self.group.setGeometry(QtCore.QRect(x, y, w, h))
        self.group.setStyleSheet('border:none;')

        self.groupTitleLabel = QtWidgets.QLabel(self.group)
        self.geometry = self.groupTitleLabel.setGeometry(QtCore.QRect(10, -5, 150, 22))
        self.groupTitleLabel.setText("STEP1. 프로젝트 만들기")
        self.groupTitleLabel.setStyleSheet('font: bold')

        self.project_edit = QtWidgets.QLineEdit(self.group)
        self.project_edit.setGeometry(QtCore.QRect(10, 20, 180, 22))
        self.project_edit.setObjectName("project_edit")
        self.project_edit.setStyleSheet(':enabled {background-image:url(./image/lineEdit_180.png);} :disabled {background-image:url(./image/lineEdit_180_dis.png);} ')

        self.button_projectadd = QtWidgets.QPushButton(self.group)
        self.button_projectadd.setGeometry(QtCore.QRect(190, 20, 40, 22))
        self.button_projectadd.setObjectName("button_projectadd")
        self.button_projectadd.setStyleSheet(
            ':enabled {background-image:url(./image/button_add.png);} :disabled {background-image:url(./image/button_add_dis.png);}')

        self.button_projectdelete = QtWidgets.QPushButton(self.group)
        self.button_projectdelete.setGeometry(QtCore.QRect(220, 20, 30, 22))
        self.button_projectdelete.setObjectName("button_projectdelete")
        self.button_projectdelete.setStyleSheet(
            ':enabled {background-image:url(./image/button_delete.png);} :disabled {background-image:url(./image/button_delete_dis.png);}')

        self.project_list = QtWidgets.QComboBox(self.group)
        self.project_list.setGeometry(QtCore.QRect(10, 50, 240, 22))
        self.project_list.setObjectName("project_list")
        self.project_list.setStyleSheet(
            ':drop-down:enabled {image:url(./image/comboList_240.png);} :drop-down:disabled {image:url(./image/comboList_240_dis.png);}')

        self.c_th_IpCamera = c_th_IpCamera
        self.c_ipset = c_Ipset

        self.button_projectadd.clicked.connect(self.Add)
        self.button_projectdelete.clicked.connect(self.Delete)
        self.project_list.currentTextChanged.connect(self.List_chg)
        self.c_ipset.project_signal_groupEnable.connect(self.groupEnable)

        if not os.path.exists("project/"):
            os.makedirs("project/")

        for training_items in os.listdir("project/"):
            self.project_list.addItem(training_items)

    def groupEnable(self, state):
        self.group.setEnabled(state)

    def List_chg(self):
        self.imgClass_signal_comboChg.emit()

    def Add(self):
        if self.project_edit.text() is "":
            pass
        else:
            for i in range(self.project_list.count()):
                if self.project_list.itemText(i) == self.project_edit.text():
                    popup_msg.Msg("Overlap","이미 있는 이름이에요. ["+self.project_edit.text()+"] \n다른 이름으로 만들어주세요.", popup_msg.msg_icon_warning)
                    self.project_edit.clear()
                    return

            if not os.path.exists("project/" + self.project_edit.text()):
                os.makedirs("project/" + self.project_edit.text())
            self.project_list.addItem(self.project_edit.text())
            self.project_list.setCurrentText(self.project_edit.text())
            print("Project Added")
            self.imgClass_signal_groupEnable.emit(1)
            self.project_edit.clear()

    def Delete(self):
        if self.project_list.count() != 0:

            project_name = self.getPrjName()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText('정말로 ['+project_name+'] 파일을 삭제하시겠습니까? \n속한 모든 내용이 사라집니다.')
            msg.setWindowTitle('Delete')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            reply = msg.exec_()
            if reply == QtWidgets.QMessageBox.Yes:
                if project_name == "":
                    pass
                else:
                    if os.path.exists("project/" + project_name):
                        shutil.rmtree("project/" + project_name)

                    model = "model/" + project_name + "_" + self.getModelList()
                    if os.path.exists(model + ".model"):
                        os.remove(model + ".model")
                        os.remove(model + ".txt")

                    self.project_list.removeItem(self.project_list.currentIndex())
                    print("PROJECT DELETED")
                if self.project_list.count() == 0:
                    self.imgClass_signal_groupEnable.emit(0)
            else:
                print("PROJECT DELETE CANCEL")
        else:
            pass

    def getPrjName(self):
        return self.project_list.currentText()

    def getModelList(self):
        return "MobileNetV2_35"
