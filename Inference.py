from PySide2 import QtCore, QtWidgets

import os
import cv2 as cv
import numpy as np
import tensorflow as tf
import urllib.request
import time

import serial
# import serial.tools.list_ports as sp


class Inference():
    def __init__(self,upper_window,x,y,w,h,c_th_IpCamera, c_Ipset, c_Project, c_ImageClass,c_Training):

        self.c_th_ipCamera = c_th_IpCamera
        self.c_ipset = c_Ipset
        self.c_project = c_Project
        self.c_imageClass = c_ImageClass
        self.c_training = c_Training

        self.group = QtWidgets.QGroupBox(upper_window)
        self.group.setGeometry(QtCore.QRect(x,y,w,h))
        self.group.setStyleSheet('border:none;')

        self.groupTitleLabel = QtWidgets.QLabel(self.group)
        self.groupTitleLabel.setGeometry(QtCore.QRect(10, 0, 120, 22))
        self.groupTitleLabel.setText("STEP4. 이미지 분석")
        self.groupTitleLabel.setStyleSheet('font: bold')

        self.button_inference = QtWidgets.QPushButton(self.group)
        self.button_inference.setGeometry(QtCore.QRect(10, 30, 240, 22))
        self.button_inference.setObjectName("button_inference")
        self.button_inference.setStyleSheet(
            ':enabled {background-image:url(./image/button_inference_start.png);} :disabled {background-image:url(./image/button_inference_start_dis.png);} ')
        self.button_inference.setDefault(True)

        self.label_inference = QtWidgets.QLabel(self.group)
        self.label_inference.setGeometry(QtCore.QRect(10, 60, 240, 40))
        self.label_inference.setAlignment(QtCore.Qt.AlignCenter)
        self.label_inference.setObjectName("label_inference")

        self.group.setEnabled(0)

        self.thread_inference = None
        self.c_training.inference_signal.connect(self.buttonChg)
        self.c_th_ipCamera.inference_signal.connect(self.buttonChg)

        self.button_inference.setCheckable(True)
        self.button_inference.toggled.connect(self.ToggleInference)

        self.signal_loadmodel = 0
        self.model = None
        self.classarray = []

    def buttonChg(self, state):
        print("Inference btn :", str(state))

        self.group.setEnabled(state)
        if state == 0 and self.thread_inference != None: #카메라가 꺼지면 inference thread stop
            print("Inference thread STOP")
            self.thread_inference.stop()

        if not os.path.exists("model/"):
            self.group.setEnabled(0)
        elif not os.listdir("model/"): # 추론할 모델이 하나도 없으면 버튼을 열지 않는다.
            self.group.setEnabled(0)
        elif not os.path.exists("model/" + self.c_project.getPrjName() + "_" + self.c_training.model_list + ".model"):
            self.group.setEnabled(0)
        elif self.c_th_ipCamera.signal_stop == 1:
            self.group.setEnabled(0)

    def Model_Load(self):
        print("Model Loading...")
        self.model = tf.keras.models.load_model("model/"+ self.c_project.getPrjName() + "_" + self.c_training.model_list + ".model")
        f2 = open("model/"+ self.c_project.getPrjName() + "_" + self.c_training.model_list + ".txt", 'r')
        for project_class_list in f2.readlines():
            self.classarray.append(project_class_list.rstrip())
        f2.close()

    def Model_Inference(self):
        print("INFERENCE")

        frame = self.c_th_ipCamera.getImage()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        usb_new_image = cv.resize(frame, (224, 224))
        usb_new_image = tf.keras.preprocessing.image.img_to_array(usb_new_image)
        usb_new_image = np.expand_dims(usb_new_image, axis=0)
        usb_new_image = (usb_new_image / 127.5) - 1
        usb_img_result = self.model.predict(usb_new_image)

        # if np.argmax(usb_img_result) == 0:
        #     ')
        # elif np.argmax(usb_img_result) == 1:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_2.png);')
        # elif np.argmax(usb_img_result) == 2:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_3.png);')
        # elif np.argmax(usb_img_result) == 3:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_4.png);')
        # elif np.argmax(usb_img_result) == 4:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_5.png);')
        # elif np.argmax(usb_img_result) == 5:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_6.png);')
        # elif np.argmax(usb_img_result) == 6:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_7.png);')
        # elif np.argmax(usb_img_result) == 7:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_8.png);')
        # elif np.argmax(usb_img_result) == 8:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_9.png);')
        # else:
        #     self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_10.png);')

        self.label_inference.setStyleSheet('background-image:url(./image/resultColor/result_class_1.png); font: bold; font-size: 15px;')
        self.label_inference.setText(self.classarray[np.argmax(usb_img_result)] +"["+str(np.round(100*(np.max(usb_img_result)),1))+"%]")
        print("INFERENCE Done")
        return np.argmax(usb_img_result), np.max(usb_img_result)

    def ToggleInference(self,state):
        print("ToggleInference "+str(state))
        if state:
            self.c_ipset.group.setEnabled(0)
            self.c_project.group.setEnabled(0)
            self.c_imageClass.group.setEnabled(0)
            self.c_training.group.setEnabled(0)
            self.button_inference.setStyleSheet(':enabled {background-image:url(./image/button_stop.png);} :disabled {background-image:url(./image/button_stop_dis.png);}')
            self.thread_inference = Inference_th(self,self.c_ipset)
            self.thread_inference.start()

        else:
            self.c_ipset.group.setEnabled(1)
            self.c_project.group.setEnabled(1)
            self.c_imageClass.group.setEnabled(1)
            self.c_training.group.setEnabled(1)
            self.thread_inference.stop()
            self.button_inference.setStyleSheet(':enabled {background-image:url(./image/button_inference_start.png);} :disabled {background-image:url(./image/button_inference_start_dis.png);}')



class Inference_th(QtCore.QThread):

    def __init__(self,c_inference,c_ipset):
        super(Inference_th, self).__init__(None)
        self.signal_stop = 0
        self.c_inference = c_inference
        self.c_ipset = c_ipset
        self.resultVal = 0
        self.prob = 0

    def run(self):
        while 1:
            if self.c_inference.model == None:
                if self.signal_stop == 0:
                    self.c_inference.Model_Load()
            else:
                self.resultVal, self.prob = self.c_inference.Model_Inference()

                try:
                    self.result()
                except (urllib.error.URLError, TimeoutError) as error:
                    print("Inference error :", error)
                    self.signal_stop = 1
            if self.signal_stop == 1:
                self.signal_stop = 0
                self.c_inference.classarray.clear()
                self.c_inference.label_inference.clear()
                self.c_inference.label_inference.setStyleSheet('background-image:none;')
                self.c_inference.model = None
                if self.c_inference.button_inference.isChecked() == True:
                    self.c_inference.button_inference.toggle()
                break
            time.sleep(0.3)



    def stop(self):
        self.signal_stop = 1

    def result(self):
        # oby
        if self.prob> 0.9:
            if not self.c_ipset.Ipaddress() == None:
                resultUrl ="http://"+ self.c_ipset.Ipaddress() + "/control?var=result&val=" + str(self.resultVal+1)  # check need (error)
                print("\n*****\nsend result({})\n".format(resultUrl))
                resultOpen = urllib.request.urlopen(resultUrl)
                resultOpen.close()
            else:

                print("PC CAM Mode result:{}".format(str(self.resultVal+1)))
                value = str(self.resultVal+1)
                val =value.encode('utf-8')
                self.c_ipset.com.write(val)


