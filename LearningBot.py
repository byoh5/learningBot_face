from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import *
from PySide2 import QtCore, QtGui, QtWidgets
import time

import SetIP
import Project
import ImageClass
import Training
import Inference
import CameraView
import login
import sys
import popup_msg

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow,self).__init__(None)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"Learning Bot")
        MainWindow.resize(900, 640)
        MainWindow.setWindowIcon(QtGui.QIcon('image/run-icon.png'))
        MainWindow.setStyleSheet('background-color: #fff4da; font-size:11px ')

        x=10
        y=10
        w=260
        h=200
        t = 10

        self.image_view = QtWidgets.QLabel(MainWindow)
        self.image_view.setGeometry(QtCore.QRect(280, 20, 600, 600))


        self.ipCamera = CameraView.IPCamera_th(self,self.image_view)

        self.ipCamera.start()

        self.ipset = SetIP.IPset(MainWindow, x, y, w, h,self.ipCamera)
        y = y + h + t
        self.project = Project.Project(MainWindow,x,y,w,80,self.ipCamera, self.ipset)
        y = y + 70 + t
        self.imgclass = ImageClass.Class(MainWindow,x,y,w,120,self.ipCamera, self.project)
        y = y + 120 + t
        self.training = Training.Training(MainWindow,x,y,w,100, self.ipCamera, self.ipset, self.project, self.imgclass)
        y = y + 70 + t
        self.inference = Inference.Inference(MainWindow,x,y,w,130,self.ipCamera, self.ipset, self.project, self.imgclass, self.training)

        self.retranslateUi(MainWindow)

        self.gif = QtGui.QMovie("image/loading.gif")
        self.gif.setScaledSize(self.image_view.size())
        self.gif.start()

        self.th_gif = QtGui.QMovie("image/training_wait.gif")
        self.th_gif.setScaledSize(self.image_view.size())
        self.th_gif.start()

        # id, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your id:')
        # pw, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your passwd:')
        # r = login.login(id,pw,'2020080013002')
        # if r != '200':
        #     if r == '204':
        #         popup_msg.Msg("Check id", "등록되지 않은 ID 입니다. ID를 확인해주세요!", popup_msg.msg_icon_warning)
        #     if r == '202':
        #         popup_msg.Msg("Check password", "PASS WORD를 확인해주세요!", popup_msg.msg_icon_warning)
        #     if r == '206':
        #         popup_msg.Msg("Check class", "Class가 등록되지 않았습니다. 등록후 사용해 주세요!", popup_msg.msg_icon_warning)
        #     sys.exit()


        self.loadingMain(0)

    def loadingMain(self, state): # 0:off 1:training
        if state == 0:
            self.image_view.setMovie(self.gif)
            print("Main Loading Image")

        elif state == 1:
            self.image_view.setMovie(self.th_gif)
            print("Training Loading Image")


    def stopLoadingMain(self):
        self.gif.stop()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("Learning Bot", u"Learning Bot", None))

    def closeEvent(self,event):
        self.stopLoadingMain()
        time.sleep(0.3)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.show()
    app.exec_()

