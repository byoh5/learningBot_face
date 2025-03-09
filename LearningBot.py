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

INFERENCE_IMAGE_MAP = {
    "angry": "image/ai/angry.png",
    "disgust":"image/ai/disgust.png",
    "fear": "image/ai/fear.png",
    "happy": "image/ai/happy.png",
    "neutral": "image/ai/neutral.png",
    "sad": "image/ai/sad.png",
    "surprise":"image/ai/surprise.png"
}

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow,self).__init__(None)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"AI Mood")
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
        self.inference_group.setGeometry(QtCore.QRect(x, 300, w, 200))
        self.inference_group.setStyleSheet('border:none;')
        # self.inference_group.setTitle("Inference Control")
        # self.inference_group.setStyleSheet('border:1px solid gray;')

        self.groupTitleLabel = QtWidgets.QLabel(self.inference_group)
        self.groupTitleLabel.setGeometry(QtCore.QRect(10, 20, 100, 22))
        self.groupTitleLabel.setText("STEP1. 감정인식")
        self.groupTitleLabel.setStyleSheet('font: bold')

        # 시작 버튼
        self.btn_inference_start = QtWidgets.QPushButton(self.inference_group)
        # self.btn_inference_start.setText("Start Inference")
        self.btn_inference_start.setGeometry(QtCore.QRect(10, 50, 116, 23))
        self.btn_inference_start.setStyleSheet(':enabled {background-image:url(./image/ai/startEnable.png);} :disabled {background-image:url(image/ai/startDisable.png);}')

        # 정지 버튼
        self.btn_inference_stop = QtWidgets.QPushButton(self.inference_group)
        # self.btn_inference_stop.setText("Stop Inference")
        self.btn_inference_stop.setGeometry(QtCore.QRect(126, 50, 116, 23))
        self.btn_inference_stop.setStyleSheet(':enabled {background-image:url(./image/ai/stopEnable.png);} :disabled {background-image:url(image/ai/stopDisable.png);}')

        # 초기 상태 설정 (시작 버튼 활성화, 정지 버튼 비활성화)
        self.btn_inference_start.setEnabled(True)
        self.btn_inference_stop.setEnabled(False)

        # Inference 결과 출력 Label 추가
        self.inference_label = QLabel(self.inference_group)
        self.inference_label.setGeometry(QtCore.QRect(10, 90, 241, 39))  # 결과 표시할 위치
        self.inference_label.setStyleSheet('background-image:url(./image/ai/emotionResult.png);')
        self.inference_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.inference_label.setText("Inference Result: None")

        # Inference 결과 출력 Label 추가
        self.inference_result = QLabel(self.inference_group)
        self.inference_result.setGeometry(QtCore.QRect(10, 140, 241, 39))  # 결과 표시할 위치
        self.inference_result.setAlignment(QtCore.Qt.AlignCenter)
        self.inference_result.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")

        # self.inference_result.setText("Inference Result: None")



        self.image_view = QtWidgets.QLabel(MainWindow)
        self.image_view.setGeometry(QtCore.QRect(280, 20, 600, 600))


        self.ipCamera = CameraView.IPCamera_th(self,self.image_view)

        self.ipCamera.start()

        self.ipset = SetIP.IPset(MainWindow, x, y, w, h,self.ipCamera)
        y = y + h + t
        # self.project = Project.Project(MainWindow,x,y,w,80,self.ipCamera, self.ipset)

        self.inference = Inference.Inference(self.ipCamera,self.image_view,self.ipset)

        # -----------------------------
        # 3) Timer 설정
        # -----------------------------
        self.inference_timer = QTimer(self)
        # 1000ms(1초) 간격으로 Inference 실행
        self.inference_timer.setInterval(500)
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
        self.btn_inference_start.setEnabled(False)
        self.btn_inference_stop.setEnabled(True)


    def stop_inference(self):
        """Inference 정지(타이머 중지)"""
        print("Inference Stop!")
        self.inference_timer.stop()
        self.loadingMain(0)
        self.btn_inference_start.setEnabled(True)
        self.btn_inference_stop.setEnabled(False)

    def run_inference(self):
        """Inference 실행 후 결과 표시"""
        print("Running Inference...")
        result = self.inference.Model_Inference()

        if result:
            # 감정 리스트 생성
            emotion_list = list(INFERENCE_IMAGE_MAP.keys())

            # 결과 감정의 인덱스 가져오기
            result_emotion = result.lower()
            image_path = INFERENCE_IMAGE_MAP.get(result_emotion, "image/ai/happy.png")  # 기본 이미지 설정

            # 감정의 순서 (1부터 시작)
            emotion_index = emotion_list.index(result_emotion) + 1 if result_emotion in emotion_list else None

            print(f"Emotion: {result_emotion}, Index: {emotion_index}, Image Path: {image_path}")

            # QLabel에 이미지 적용
            pixmap = QtGui.QPixmap(image_path)
            self.inference_result.setPixmap(pixmap)
            self.inference_result.setScaledContents(True)  # 이미지 크기 자동 조정

            value = str(emotion_index)
            val = value.encode('utf-8')
            self.ipset.com.write(val)

        else:
            self.inference_result.clear()  # 이미지 제거
            self.inference_result.setText("No Face Detected")

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

