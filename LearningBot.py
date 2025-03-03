from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import *
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer
import time

import SetIP
import Project
import CameraView
import Inference
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

        # -----------------------------
        # 1) Inference 제어를 위한 새 그룹 박스 추가
        # -----------------------------
        self.inference_group = QtWidgets.QGroupBox(MainWindow)
        self.inference_group.setGeometry(QtCore.QRect(x, 300, w, 130))
        self.inference_group.setTitle("Inference Control")
        self.inference_group.setStyleSheet('border:1px solid gray;')

        # 시작 버튼
        self.btn_inference_start = QtWidgets.QPushButton(self.inference_group)
        self.btn_inference_start.setText("Start Inference")
        self.btn_inference_start.setGeometry(QtCore.QRect(10, 25, 100, 30))

        # 정지 버튼
        self.btn_inference_stop = QtWidgets.QPushButton(self.inference_group)
        self.btn_inference_stop.setText("Stop Inference")
        self.btn_inference_stop.setGeometry(QtCore.QRect(120, 25, 100, 30))

        # Inference 결과 출력 Label 추가
        self.inference_label = QLabel(self.inference_group)
        self.inference_label.setGeometry(QtCore.QRect(10, 70, 240, 30))  # 결과 표시할 위치
        self.inference_label.setStyleSheet("background: white; border: 1px solid gray; padding: 5px;")
        self.inference_label.setAlignment(QtCore.Qt.AlignCenter)
        self.inference_label.setText("Inference Result: None")

        self.image_view = QtWidgets.QLabel(MainWindow)
        self.image_view.setGeometry(QtCore.QRect(280, 20, 600, 600))


        self.ipCamera = CameraView.IPCamera_th(self,self.image_view)

        self.ipCamera.start()

        self.ipset = SetIP.IPset(MainWindow, x, y, w, h,self.ipCamera)
        y = y + h + t
        # self.project = Project.Project(MainWindow,x,y,w,80,self.ipCamera, self.ipset)

        self.inference = Inference.Inference(self.ipCamera)

        # -----------------------------
        # 3) Timer 설정
        # -----------------------------
        self.inference_timer = QTimer(self)
        # 1000ms(1초) 간격으로 Inference 실행
        self.inference_timer.setInterval(1000)
        self.inference_timer.timeout.connect(self.run_inference)

        # -----------------------------
        # 4) 버튼 시그널 연결
        # -----------------------------
        self.btn_inference_start.clicked.connect(self.start_inference)
        self.btn_inference_stop.clicked.connect(self.stop_inference)


        self.retranslateUi(MainWindow)

        self.gif = QtGui.QMovie("image/loading.gif")
        self.gif.setScaledSize(self.image_view.size())
        self.gif.start()

        self.th_gif = QtGui.QMovie("image/training_wait.gif")
        self.th_gif.setScaledSize(self.image_view.size())
        self.th_gif.start()


        self.loadingMain(0)

    def start_inference(self):
        """Inference 주기적으로 실행(타이머 시작)"""
        print("Inference Start!")
        self.inference_timer.start()

    def stop_inference(self):
        """Inference 정지(타이머 중지)"""
        print("Inference Stop!")
        self.inference_timer.stop()

    def run_inference(self):
        """Inference 실행 후 결과 표시"""
        print("Running Inference...")
        result = self.inference.Model_Inference()
        if result:
            self.inference_label.setText(f"Inference Result: {result}")
        else:
            self.inference_label.setText("No Face Detected")

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
        self.inference_timer.stop()
        time.sleep(0.3)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.show()
    app.exec_()

