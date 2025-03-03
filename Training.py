from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Signal

import os
import time
import numpy as np
import tensorflow as tf
import popup_msg

class Training(QtCore.QObject):
    inference_signal = Signal(int)
    def __init__(self,upper_window,x,y,w,h, c_th_IpCamera, c_Ipset, c_Project, c_ImageClass):
        super().__init__()

        self.c_th_ipCamera = c_th_IpCamera
        self.c_ipset = c_Ipset
        self.c_project = c_Project
        self.c_imageClass = c_ImageClass

        self.allow_trainingImg_max = 16

        self.group = QtWidgets.QGroupBox(upper_window)
        self.group.setGeometry(QtCore.QRect(x,y,w,h))
        self.group.setStyleSheet('border:none;')

        self.groupTitleLabel = QtWidgets.QLabel(self.group)
        self.groupTitleLabel.setGeometry(QtCore.QRect(10, -5, 180, 22))
        self.groupTitleLabel.setText("STEP3. 인공지능 학습")
        self.groupTitleLabel.setStyleSheet('font: bold')

        self.epoch_list = QtWidgets.QComboBox(self.group)
        self.epoch_list.addItem('5')
        self.epoch_list.addItem('10')
        self.epoch_list.addItem('20')
        self.epoch_list.addItem('30')
        self.epoch_list.addItem('40')
        self.epoch_list.addItem('50')

        self.epoch_list.setGeometry(QtCore.QRect(10, 20, 180, 22))
        self.epoch_list.setObjectName("epoch_list")
        self.epoch_list.setStyleSheet(
            ':drop-down:enabled {image:url(./image/comboList_180.png);} :drop-down:disabled {image:url(./image/comboList_180_dis.png);}')

        self.label_epochTime = QtWidgets.QLabel(self.group)
        self.label_epochTime.setGeometry(QtCore.QRect(200, 20, 60, 22))
        self.label_epochTime.setAlignment(QtCore.Qt.AlignCenter)
        self.label_epochTime.setObjectName("label_epochTime")

        self.button_training = QtWidgets.QPushButton(self.group)
        self.button_training.setGeometry(QtCore.QRect(10, 50, 240, 22))
        self.button_training.setObjectName("button_training")
        self.button_training.setStyleSheet(':enabled {background-image:url(./image/button_training_start.png);} :disabled {background-image:url(./image/button_training_start_dis.png);}')

        self.c_imageClass.training_signal.connect(self.buttonChg)
        self.c_ipset.training_signal_groupEnable.connect(self.buttonChg)

        self.buttonChg(self.c_imageClass.class_list.count() != 0)
        self.button_training.clicked.connect(self.DoTraining)

        self.model_list = self.c_project.getModelList()
        self.epoch_list.currentTextChanged.connect(self.list_chg)

        self.epoch_list.setCurrentText("20")
        self.list_chg()

    def current_epoch(self):
        return self.epoch_list.currentText()

    def list_chg(self):
        print("Current_epoch:", self.epoch_list.currentText())
        totalAmount = self.c_imageClass.getClassTotalCnt() * int(self.epoch_list.currentText()) * 0.06
        print(self.c_imageClass.getClassTotalCnt())
        print(totalAmount)
        if totalAmount<60 :
            self.label_epochTime.setText(str(int(totalAmount))+ " sec")
        else :
            self.label_epochTime.setText(str(int(totalAmount/60))+ " min")
        # if int(self.epoch_list.currentText()) == 5:
        #     self.label_epochTime.setText("over 5 min")
        # elif int(self.epoch_list.currentText()) == 10:
        #     self.label_epochTime.setText("over 5 min")
        # elif int(self.epoch_list.currentText()) == 20:
        #     self.label_epochTime.setText("over 5 min")
        # elif int(self.epoch_list.currentText()) == 30:
        #     self.label_epochTime.setText("over 20 min")
        # elif int(self.epoch_list.currentText()) == 40:
        #     self.label_epochTime.setText("over 5 min")
        # elif int(self.epoch_list.currentText()) == 50:
        #     self.label_epochTime.setText("over 30 min")

    def buttonChg(self,state):
        print("Training btn : ", state)
        classCnt = self.c_imageClass.class_list.count()
        self.group.setEnabled(state)
        self.inference_signal.emit(1)
        if state == 1 and classCnt < 2:  # class 파일은 두개 이상
            self.group.setEnabled(0)
            print("Check pls - over 2 class files")
        elif state == 1 and classCnt > 1: # class 파일이 존재하고
            if self.getCountClassImg() == 0: # 사진이 없으면 disable
                self.group.setEnabled(0)
            print("Check pls - no image files")

    def getCountClassImg(self):
        classCnt = self.c_imageClass.class_list.count()
        classList_cnt = 0;
        for i in range(classCnt):
            className = self.c_imageClass.class_list.itemText(i)
            calss_flolder = "project/" + self.c_project.getPrjName() + "/" + className + "/"
            if not os.listdir(calss_flolder):  # 사진이 없으면
               return 0

            classList_cnt += len(os.listdir(calss_flolder))

        return classList_cnt

    def DoTraining(self):
        print("Do Training")

        imgCount =  self.getCountClassImg()

        if self.getCountClassImg() < self.allow_trainingImg_max:
            popup_msg.Msg("More Image Data", "데이터를 " + str(self.allow_trainingImg_max) + "개 이상 모아주세요. 현재는 [" + str(imgCount) + "]개 입니다.\n", popup_msg.msg_icon_warning)
            return

        self.thread_training = Training_th(self.c_imageClass.class_list, self.c_project, self)
        self.thread_training.start()

        self.buttonChg(0)
        self.c_ipset.group.setEnabled(0)
        self.c_project.group.setEnabled(0)
        self.c_imageClass.group.setEnabled(0)
        self.group.setEnabled(0)
        self.inference_signal.emit(0)
        self.c_th_ipCamera.hold(1)

    def Bt_Train_done(self):
        print("Train Done")
        self.buttonChg(1)
        self.c_ipset.group.setEnabled(1)
        self.c_project.group.setEnabled(1)
        self.group.setEnabled(1)
        self.c_th_ipCamera.hold(0)

        if self.c_th_ipCamera.signal_stop == 0: # 카메라가 켜져 있을때만 enable
            self.c_imageClass.group.setEnabled(1)
            self.inference_signal.emit(1)

class Training_th(QtCore.QThread):
    def __init__(self, class_list, c_project, c_train):
        super(Training_th, self).__init__(None)

        self.th_class_list = class_list
        self.th_model_list = c_train.model_list
        self.c_project = c_project
        self.c_train = c_train

    def run(self):
        if self.th_model_list == None:
            print("Fail : th_model is None")
            return
        time_a = time.time()
        if self.th_model_list == "MobileNetV2_35":
            base_model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, alpha=0.35)
            input_size = 224
        elif self.th_model_list == "DenseNet121":
            base_model = tf.keras.applications.DenseNet121(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "DenseNet169":
            base_model = tf.keras.applications.DenseNet169(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "DenseNet201":
            base_model = tf.keras.applications.DenseNet201(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "InceptionResNetV2":
            base_model = tf.keras.applications.InceptionResNetV2(weights='imagenet', include_top=False)
            input_size = 299
        elif self.th_model_list == "InceptionV3":
            base_model = tf.keras.applications.InceptionV3(weights='imagenet', include_top=False)
            input_size = 299
        elif self.th_model_list == "MobileNetV2":
            base_model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "NASNetLarge":
            base_model = tf.keras.applications.NASNetLarge(weights='imagenet', include_top=False)
            input_size = 331
        elif self.th_model_list == "NASNetMobile":
            base_model = tf.keras.applications.NASNetMobile(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "ResNet101":
            base_model = tf.keras.applications.ResNet101(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "ResNet101V2":
            base_model = tf.keras.applications.ResNet101V2(weights='imagenet', include_top=False)
            input_size = 299
        elif self.th_model_list == "ResNet152":
            base_model = tf.keras.applications.ResNet152(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "ResNet152V2":
            base_model = tf.keras.applications.ResNet152V2(weights='imagenet', include_top=False)
            input_size = 299
        elif self.th_model_list == "ResNet50":
            base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)
            input_size = 224
        elif self.th_model_list == "ResNet50V2":
            base_model = tf.keras.applications.ResNet50V2(weights='imagenet', include_top=False)
            input_size = 299
        elif self.th_model_list == "Xception":
            base_model = tf.keras.applications.Xception(weights='imagenet', include_top=False)
            input_size = 299
        else:
            pass

        print(self.th_model_list)
        print(input_size)
        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(100, activation='relu')(x)
        preds = tf.keras.layers.Dense(self.th_class_list.count(), activation='softmax')(x)
        train_model = tf.keras.models.Model(inputs=base_model.input, outputs=preds)
        current_epochs = int(self.c_train.current_epoch())
        print("Current_epochs : ", current_epochs)

        for layer in train_model.layers[:-(2)]:
            layer.trainable = False
        for layer in train_model.layers[-(2):]:
            layer.trainable = True
        train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255) # normalize 추가
        print("Training project name :", self.c_project.getPrjName())
        train_generator = train_datagen.flow_from_directory('project/' + self.c_project.getPrjName(),
                                                            target_size=(input_size, input_size),
                                                            class_mode='categorical', batch_size=self.c_train.allow_trainingImg_max)
        train_model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.CategoricalCrossentropy(),
                            metrics=['accuracy'])
        step_size_train = train_generator.n // train_generator.batch_size

        train_model.fit_generator(generator=train_generator,
                                  steps_per_epoch=step_size_train,
                                  epochs=current_epochs)

        if not os.path.exists("model/"):
            os.makedirs("model/")

        train_model.save('model/' + self.c_project.getPrjName() + "_" + self.th_model_list + ".model", include_optimizer=False)
        print("TRAINING DONE")

        f2 = open("model/" + self.c_project.getPrjName() + "_" + self.th_model_list + ".txt", "w")

        list_sort = np.sort(os.listdir("project/" + self.c_project.getPrjName()))
        for class_items in list_sort:
            f2.write(class_items + "\n")
        f2.close()

        print(time.time() - time_a)

        self.c_train.Bt_Train_done()

