from PySide2 import QtCore, QtGui
from PySide2.QtCore import Signal

import requests
import cv2 as cv
import numpy as np
from datetime import datetime
import time
import os
import ping


class IPCamera_th(QtCore.QThread):
    th_ip = None
    th_id = None
    th_pwd = None
    inference_signal = Signal(int)
    imgClass_signal = Signal(int)
    def __init__(self, loadingMain, viewer):
        super(IPCamera_th, self).__init__(None)
        self.th_viewer = viewer
        self.loading_main = loadingMain
        self.signal_stop = 1
        self.fr = None
        self.save_state = 0
        self.project_name = ""
        self.class_name = ""
        self.label_classnum = None
        self.signalBtn_on = 0
        self.holded = 0

    def run(self):

        capture = cv.VideoCapture(0)
        capture.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        capture.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

        while (1):
            if self.holded == 0:
                if self.th_id == None and self.th_id == None and self.th_pwd == None and self.signal_stop == 0:
                    ret, frame = capture.read()
                    cvimg = cv.resize(frame, (800, 600))
                    cvimg = cvimg[0:600, 100:700]
                    cvimg = cv.flip(cvimg, flipCode=1)
                    self.th_viewer.setPixmap(QtGui.QPixmap(QtGui.QImage(cvimg, 600, 600, QtGui.QImage.Format_BGR888)))
                    self.fr = cvimg

                    if self.signalBtn_on == 0:  # 한번만 발생하게
                        self.inference_signal.emit(1)
                        self.imgClass_signal.emit(1)
                        self.signalBtn_on = 1

                    if (self.save_state == 1) and (self.label_classnum != None):
                        cv.imwrite(
                            "project/" + self.project_name + "/" + self.class_name + "/" + self.class_name + "_" + datetime.now().strftime(
                                "%m%d_%H%M%S_%f") + ".jpg", cvimg)
                        print(
                            "project/" + self.project_name + "/" + self.class_name + "/" + self.class_name + "_" + datetime.now().strftime(
                                "%m%d_%H%M%S_%f") + ".jpg")
                        self.label_classnum.setText(
                            str(len(os.listdir("project/" + self.project_name + "/" + self.class_name))))
                    continue

                if (not (self.th_ip == None or self.th_id == None or self.th_pwd == None)) and self.signal_stop == 0:
                    try:
                        response = requests.get('http://' + self.th_ip + '/capture', timeout=5) #5초
                    except requests.exceptions.ConnectionError as timeout:
                        print("Timeout Error :", timeout.args[0])
                        ret = ping.ping(self.th_ip)
                        if ret:
                            continue
                        else:
                            self.stop()
                            continue
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout,SystemError) as e:
                        print("Connection Error : ", e)
                        self.stop()
                        continue


                    nparray = np.frombuffer(response.content, dtype=np.uint8)
                    try:
                        cvimg = cv.imdecode(nparray, cv.IMREAD_COLOR)
                        cvimg = cv.resize(cvimg, (800, 600))
                        cvimg = cvimg[0:600,100:700]
                        cvimg=cv.transpose(cvimg)
                        cvimg=cv.flip(cvimg,flipCode=1)
                    except cv.error as cvError:
                        print("cv2 error : ", cvError)
                        self.stop()
                        continue

                    self.th_viewer.setPixmap(QtGui.QPixmap(QtGui.QImage(cvimg, 600, 600, QtGui.QImage.Format_BGR888)))
                    self.fr = cvimg

                    if self.signalBtn_on == 0:  # 한번만 발생하게
                        self.inference_signal.emit(1)
                        self.imgClass_signal.emit(1)
                        self.signalBtn_on = 1

                    if (self.save_state == 1) and (self.label_classnum!=None):

                        cv.imwrite(
                            "project/" + self.project_name + "/" + self.class_name + "/" + self.class_name + "_" + datetime.now().strftime(
                                "%m%d_%H%M%S_%f") + ".jpg", cvimg)
                        print(
                            "project/" + self.project_name + "/" + self.class_name + "/" + self.class_name + "_" + datetime.now().strftime(
                                "%m%d_%H%M%S_%f") + ".jpg")
                        self.label_classnum.setText(str(len(os.listdir("project/"+self.project_name+"/"+self.class_name))))
                else:
                    time.sleep(1)
            else:
                time.sleep(1)

    def stop(self):
        self.signal_stop = 1
        self.signalBtn_on = 0
        self.inference_signal.emit(0)
        self.imgClass_signal.emit(0)
        self.hold(0) # connect error 시에 main loading 을 위해

    def hold(self, state):
        print("Viewer Hold : ", str(state))
        self.holded = state
        time.sleep(1)
        if self.signal_stop == 1 and self.holded == 0:
            self.loading_main.loadingMain(state)
        elif self.holded == 1:
            self.loading_main.loadingMain(state)

    def getImage(self):
        return self.fr

    def Save_state(self,state,projectname,classname,label_classnum):
        print("Save State "+str(state))
        self.save_state = state
        self.project_name = projectname
        self.class_name = classname
        self.label_classnum = label_classnum

    def Set_IP(self,ip,id,pwd):
        if ip is not None:
            self.th_ip = ip
        if id is not None:
            self.th_id = id
        if pwd is not None:
            self.th_pwd = pwd
        self.signal_stop = 0

