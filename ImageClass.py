from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal
import os
import shutil
from datetime import datetime
import cv2 as cv

import popup_msg

class Class(QtCore.QObject):
    training_signal = Signal(int)
    def __init__(self,upper_window,x,y,w,h,c_th_IpCamera,c_project):
        super().__init__()

        self.group = QtWidgets.QGroupBox(upper_window)
        self.group.setGeometry(QtCore.QRect(x, y, w, h))
        self.group.setStyleSheet('border:none;')

        self.groupTitleLabel = QtWidgets.QLabel(self.group)
        self.groupTitleLabel.setGeometry(QtCore.QRect(10, 0, 180, 22))
        self.groupTitleLabel.setText("STEP2. 데이터 모으기")
        self.groupTitleLabel.setStyleSheet('font: bold')

        self.class_edit = QtWidgets.QLineEdit(self.group)
        self.class_edit.setGeometry(QtCore.QRect(10, 30, 180, 22))
        self.class_edit.setObjectName("class_edit")
        self.class_edit.setStyleSheet(
            ':enabled {background-image:url(./image/lineEdit_180.png);} :disabled {background-image:url(./image/lineEdit_180_dis.png);} ')

        self.button_classadd = QtWidgets.QPushButton(self.group)
        self.button_classadd.setGeometry(QtCore.QRect(190, 30, 30, 22))
        self.button_classadd.setObjectName("button_classadd")
        self.button_classadd.setStyleSheet(':enabled {background-image:url(./image/button_add.png);} :disabled {background-image:url(./image/button_add_dis.png);}')

        self.button_classdelete = QtWidgets.QPushButton(self.group)
        self.button_classdelete.setGeometry(QtCore.QRect(220, 30, 30, 22))
        self.button_classdelete.setObjectName("button_classdelete")
        self.button_classdelete.setStyleSheet(':enabled {background-image:url(./image/button_delete.png);} :disabled {background-image:url(./image/button_delete_dis.png);}')

        self.class_list = QtWidgets.QComboBox(self.group)
        self.class_list.setGeometry(QtCore.QRect(10, 60, 180, 22))
        self.class_list.setObjectName("class_list")
        self.class_list.setStyleSheet(':drop-down:enabled {image:url(./image/comboList_180.png);} :drop-down:disabled {image:url(./image/comboList_180_dis.png);}')

        self.label_classnum = QtWidgets.QLabel(self.group)
        self.label_classnum.setGeometry(QtCore.QRect(210, 60, 30, 22))
        self.label_classnum.setAlignment(QtCore.Qt.AlignCenter)
        self.label_classnum.setObjectName("label_classnum")

        self.button_save = QtWidgets.QPushButton(self.group)
        self.button_save.setGeometry(QtCore.QRect(10, 90, 240, 22))
        self.button_save.setObjectName("button_save")
        self.button_save.setStyleSheet(':enabled {background-image:url(./image/button_photo.png);} :disabled {background-image:url(./image/button_photo_dis.png);} ')

        self.c_project = c_project
        self.c_th_ipCamera = c_th_IpCamera

        self.buttonChg(self.c_project.project_list.count() != 0)

        for class_items in os.listdir("project/"+self.c_project.getPrjName()):
            self.class_list.addItem(class_items)

        self.buttonChg(0)
        self.c_th_ipCamera.imgClass_signal.connect(self.buttonChg)
        self.c_project.imgClass_signal_comboChg.connect(self.ComboChg)
        self.c_project.imgClass_signal_groupEnable.connect(self.buttonChg)

        self.training_signal.emit(self.class_list.count() != 0)

        self.button_classadd.clicked.connect(self.Add)
        self.button_classdelete.clicked.connect(self.Delete)
        self.button_save.setCheckable(True)
        self.button_save.toggled.connect(self.ToggleSave)
        self.class_list.currentTextChanged.connect(self.List_chg)
        self.List_chg()

        self.totalImageCnt = 0

    def buttonChg(self,state):
        print("Class btn:", str(state))
        self.group.setEnabled(state)
        if self.c_th_ipCamera.signal_stop == 1: #버튼 on 상태를 하려는데 카메라가 꺼져있으면
            self.group.setEnabled(0)  # 버튼 off
            print("Check pls - Current Camera OFF")
        elif state == 0 and not self.c_project.getPrjName() == "":
            self.group.setEnabled(1)
            print("None Project")

    def Add(self):
        if self.class_edit.text() is "":
            pass

        else:
            for i in range(self.class_list.count()):
                if self.class_list.itemText(i) == self.class_edit.text():
                    popup_msg.Msg("Overlap", "이미 있는 이름이에요. [" + self.class_edit.text() + "] \n다른 이름으로 만들어주세요.", popup_msg.msg_icon_warning)
                    self.class_edit.clear()
                    return

            if not os.path.exists("project/" + self.c_project.getPrjName() + "/" + self.class_edit.text()):
                os.makedirs("project/" + self.c_project.getPrjName() + "/" + self.class_edit.text())
            self.class_list.addItem(self.class_edit.text())
            self.class_list.setCurrentText(self.class_edit.text())
            self.class_edit.clear()
            print("CLASS ADDED")

        self.buttonChg(self.class_list.count() != 0)
        self.training_signal.emit(self.class_list.count() != 0)

    def Delete(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText('정말로 ['+self.class_list.currentText()+'] 파일을 삭제하시겠습니까? \n속한 모든 내용이 사라집니다.')
        msg.setWindowTitle('Delete')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            if not os.path.exists("project/" + self.c_project.getPrjName() + "/" + self.class_list.currentText()):
                self.class_list.removeItem(self.class_list.currentIndex())
            else:
                print("CLASS DELETED")

                shutil.rmtree("project/" + self.c_project.getPrjName()+ "/" + self.class_list.currentText())
                self.class_list.removeItem(self.class_list.currentIndex())
        else:
            print("CLASS DELETE CANCEL")

        self.buttonChg(self.class_list.count() != 0)
        self.training_signal.emit(self.class_list.count() != 0)

    def Save(self):
        print("JPEG_SAVE")
        cv.imwrite(
            "project/" + self.c_project.getPrjName() + "/" + self.getClassName() + "/" + self.getClassName() + "_" + datetime.now().strftime(
                "%m%d_%H%M%S_%f") + ".jpg", self.c_th_ipCamera.getImage())
        print(
            "project/" + self.c_project.getPrjName() + "/" + self.getClassName() + "/" + self.getClassName() + "_" + datetime.now().strftime(
                "%m%d_%H%M%S_%f") + ".jpg")

    def ToggleSave(self,state):
        print("togglesave "+str(state))
        if not self.getClassName() == "":
            self.c_th_ipCamera.Save_state(state,self.c_project.getPrjName(),self.getClassName(),self.label_classnum)

        if state:
            self.button_save.setStyleSheet(':enabled {background-image:url(./image/button_stop.png);} :disabled {background-image:url(./image/button_stop_dis.png);}')
        else:
            self.button_save.setStyleSheet(':enabled {background-image:url(./image/button_photo.png);} :disabled {background-image:url(./image/button_photo_dis.png);}')

        self.training_signal.emit(self.class_list.count() != 0)

    def List_chg(self):
        self.label_classnum.setText(str(self.getClassNum()))

    def ComboChg(self):
        print("Project was changed")
        self.class_list.clear()
        for class_items in os.listdir("project/"+self.c_project.getPrjName()):
            self.class_list.addItem(class_items)
        self.label_classnum.setText(str(self.getClassNum()))
        self.buttonChg(1)
        self.training_signal.emit(self.class_list.count() != 0)

    def getClassName(self):
        return self.class_list.currentText()

    def getClassNum(self):
        return str(len(os.listdir("project/"+self.c_project.getPrjName()+"/"+self.getClassName())))

    def getClassTotalCnt(self):
        self.totalImageCnt = 0
        for class_items in os.listdir("project/" + self.c_project.getPrjName()):
            self.totalImageCnt += len(os.listdir("project/" + self.c_project.getPrjName() + "/" + class_items))
        return self.totalImageCnt