from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Signal
import os
import time
import popup_msg
import serial
import serial.tools.list_ports as sp
import login
import sys


class IPset(QtCore.QObject):
    ipadd = None
    id = 'runcoding'
    pwd = 'runcoding'

    directory = None

    project_signal_groupEnable = Signal(int)
    training_signal_groupEnable = Signal(int)
    def __init__(self,upper_window,x,y,w,h,c_th_IpCamera):
        super().__init__()
        self.group = QtWidgets.QGroupBox(upper_window)
        self.group.setGeometry(QtCore.QRect(x,y,w,h))
        self.group.setStyleSheet('border:none;')

        self.groupTitleLabel = QtWidgets.QLabel(self.group)
        self.groupTitleLabel.setGeometry(QtCore.QRect(10, 20, 100, 22))
        self.groupTitleLabel.setText("STEP0. 연결하기")
        self.groupTitleLabel.setStyleSheet('font: bold')

        self.getssidLabel = QtWidgets.QLabel(self.group)
        self.getssidLabel.setGeometry(QtCore.QRect(10, 40, 100, 22))
        self.getssidLabel.setText("ID")

        self.getssid = QtWidgets.QLineEdit(self.group)
        self.getssid.setGeometry(QtCore.QRect(10, 60, 240, 22))
        self.getssid.setStyleSheet(':enabled {background-image:url(./image/lineEdit_240.png);} :disabled {background-image:url(./image/lineEdit_240_dis.png);}')

        self.getpwLabel = QtWidgets.QLabel(self.group)
        self.getpwLabel.setGeometry(QtCore.QRect(10, 90, 100, 22))
        self.getpwLabel.setText("PASSWORD")

        self.getpw = QtWidgets.QLineEdit(self.group)
        self.getpw.setGeometry(QtCore.QRect(10, 120, 240, 22))
        self.getpw.setEchoMode(QLineEdit.Password)
        self.getpw.setStyleSheet(':enabled {background-image:url(./image/lineEdit_240.png);} :disabled {background-image:url(./image/lineEdit_240_dis.png);}')

        self.button_con = QtWidgets.QPushButton(self.group)
        self.button_con.setGeometry(QtCore.QRect(10, 150, 240, 22))
        self.button_con.setStyleSheet(':enabled {background-image:url(./image/button_connect.png);} :disabled {background-image:url(./image/button_connect_dis.png);}')

        self.button_con.clicked.connect(self.connectProcess)

        self.c_th_ipCamera = c_th_IpCamera

        self.setgroupEnable(0)
        # if os.path.isfile("setfile.txt"):
        #     self.getFile()
        #     self.GetIpadd()

        self.wifiresult = 0
        self.com = None


    def Ipaddress(self):
        return self.ipadd

    # def GetIpadd(self):
    #     #print("GetIpadd : " + self.ipadd)
    #     if self.checkIP() == True:
    #         self.c_th_ipCamera.Set_IP(self.ipadd,self.id,self.pwd)



    def connectProcess(self):
        if(self.loginProcess()):
            self.wificon()


    def loginProcess(self):
        id = self.getssid.text()
        pw = self.getpw.text()
        r = login.login(id, pw, '2020080013002')
        if r != '200':
            if r == '204':
                popup_msg.Msg("Check id", "등록되지 않은 ID 입니다. ID를 확인해주세요!", popup_msg.msg_icon_warning)
            if r == '202':
                popup_msg.Msg("Check password", "PASS WORD를 확인해주세요!", popup_msg.msg_icon_warning)
            if r == '206':
                popup_msg.Msg("Check class", "Class가 등록되지 않았습니다. 등록후 사용해 주세요!", popup_msg.msg_icon_warning)
            return False
        return True

    def wificon(self):
        if self.c_th_ipCamera.signal_stop == 0:
            print("stop")
            self.c_th_ipCamera.stop()
            time.sleep(2)

        self.c_th_ipCamera.signalBtn_on = 0
        self.setgroupEnable(0)

        # if SerialLen == 0 and ssidLen == 0 and pwLen == 0:
        popup_msg.Msg("Check Arduino", "PC 카메라 모드입니다. 아두이노를 PC와 연결 후 COM 번호를 확인해주세요!", popup_msg.msg_icon_warning)

        while True:
            # select comport popup
            portlist = self.find_port()
            comdlg = COMSettingDialog(portlist)
            comdlg.exec_()
            self.com = self.setCOMport(comdlg.com_name)
            if self.com == None:
                popup_msg.Msg("Check Serial port", "아두이노 시리얼 번호를 다시 확인해주세요.", popup_msg.msg_icon_warning)
                continue
            break

        self.c_th_ipCamera.signal_stop = 0  # pccam 모드
        self.ipadd =None
        # self.setFile()                      # 다음번 에도 pccam 모드를 사용하기 위해
        self.setgroupEnable(1)              # group 활성화
        return

        # if SerialLen == 0:
        #     popup_msg.Msg("Check Serial NUmber", "러닝캠 시리얼 번호를 다시 확인해주세요.", popup_msg.msg_icon_warning)
        # else:
        #     if ssidLen == 0 and pwLen == 0:
        #         popup_msg.Msg("WIFI connecting", "다이렉트 모드로 동작하여 인터넷 연결이 끊어집니다.", popup_msg.msg_icon_warning)
        #         self.thread_wificon = wificon_th(self)
        #         self.thread_wificon.start()
        #         self.thread_wificon.IPset_signal_wificonResult.connect(self.wifidone)
        #     elif ssidLen == 0 or pwLen == 0:
        #         popup_msg.Msg("Check WIFI", "입력정보를 다시 확인해주세요. WIFI ID/PW 모두 필요합니다.", popup_msg.msg_icon_warning)
        #         return
        #     else:
        #         popup_msg.Msg("WIFI connecting", "인터넷 연결이 끊어집니다. \n러닝캠 WIFI 연결이 되면 다시 연결되니 기다려주세요~", popup_msg.msg_icon_warning)
        #         self.thread_wificon = wificon_th(self)
        #         self.thread_wificon.start()
        #         self.thread_wificon.IPset_signal_wificonResult.connect(self.wifidone)

            # wifiresult = WifiConnect.startWifiConnection(self.getssid.text(), self.getpw.text(), self.getserial.text())

    def wifidone(self):
        returnval=self.wifiresult
        if returnval == 10:
            popup_msg.Msg("WIFI Disconnect", "러닝캠 WIFI 연결에 실패했습니다. \n1. 러닝캠 리셋\n2. 러닝봇 입력정보 확인", popup_msg.msg_icon_warning)
        else:
            self.ipadd = returnval
            # self.setFile()
        self.setgroupEnable(1)

    def setgroupEnable(self, state):
        self.project_signal_groupEnable.emit(state)
        self.training_signal_groupEnable.emit(state)

    # def setFile(self):
    #     f = open("setfile.txt","w")
    #     if self.ipadd:
    #         f.write(self.ipadd +"\n")
    #     f.write(self.getssid.text()+"\n")
    #     f.write(self.getpw.text()+"\n")
    #     f.write(self.getserial.text()+"\n")
    #     f.close()

    # def getFile(self):
    #     f = open("setfile.txt",'r')
    #     self.ipadd= f.readline().rstrip('\n')
    #     self.getssid.setText(f.readline().rstrip('\n'))
    #     self.getpw.setText(f.readline().rstrip('\n'))
    #     self.getserial.setText(f.readline().rstrip('\n'))
    #     f.close()

    def getCOMport(self):
        list = sp.comports()
        connected = []
        for i in list:
            connected.append(i.device)
        print("Connected COM ports: " + str(connected))
        return connected

    def find_port(self):
        # 찾고 싶은 디스크립션 키워드를 리스트로 관리
        description_filters = [
            "USB-SERIAL CH340",
            "Arduino Uno"
        ]

        ports = list(serial.tools.list_ports.comports())
        matched_devices = []

        for p in ports:
            # 만약 description이 필터 문자열 중 하나를 포함한다면,
            # 해당 포트의 device를 리스트에 추가
            if any(f in p.description for f in description_filters):
                matched_devices.append(p.device)

        # 필터를 만족하는 모든 device를 리스트 형태로 반환
        return matched_devices

    def setCOMport(self, comport):
        ser = None
        try:
            ser = serial.Serial(  # set parameters, in fact use your own :-)
                port=comport,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            ser.isOpen()  # try to open port, if possible print message and proceed with 'while True:'
            print("port is opened!")

        except IOError:  # if port is already opened, close it and open it again and print message
            # ser.close()
            # ser.open()
            print("port was already open, was closed and opened again!")

        return ser


class COMSettingDialog(QtWidgets.QDialog):
    def __init__(self,comport_list):
        super().__init__()
        self.comport_list = comport_list
        self.com_name = None
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("COM PORT SETTING")
        self.resize(300, 100)

        self.com_list = QtWidgets.QComboBox(self)
        self.com_list.setGeometry(QtCore.QRect(30, 20, 240, 30))
        self.com_list.setObjectName("com_list")

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(120, 60, 171, 41))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.line = QtWidgets.QFrame(self)

        self.buttonBox.accepted.connect(self.BT_OK)

        for com_number in self.comport_list:
            self.com_list.addItem(com_number)

    def BT_OK(self):
        self.com_name = self.com_list.currentText()
        self.close()