import cv2
from deepface import DeepFace
from PySide2 import QtCore, QtGui

class Inference():
    def __init__(self, c_th_IpCamera, viewer, c_ipset):
        self.c_th_ipCamera = c_th_IpCamera
        self.th_viewer = viewer
        self.c_ipset = c_ipset

    def Model_Inference(self):
        print("INFERENCE STARTED")

        frame = self.c_th_ipCamera.getImage()
        if frame is None:
            print("No frame captured.")
            return None  # 결과 없음

        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                detector_backend='opencv'
                # enforce_detection=False
            )

            # 얼굴이 감지되지 않은 경우
            if not result or 'dominant_emotion' not in result[0]:
                print("No face detected in the frame.")
                return None  # 결과값만 None 반환 (화면 유지)

            dominant_emotion = result[0]['dominant_emotion']
            print(f"Emotion: {dominant_emotion}")

            # 감정 분석된 얼굴의 경계 상자 표시
            for face in result:
                if 'region' in face and face['region']:
                    x, y, w, h = face['region']['x'], face['region']['y'], face['region']['w'], face['region']['h']
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        except Exception as e:
            print(f"Inference Error: {e}")

        # 예외가 발생하든 안 하든 화면 업데이트 수행
        try:
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format_BGR888)
            self.th_viewer.setPixmap(QtGui.QPixmap(image))
        except Exception as img_err:
            print(f"Image Update Error: {img_err}")

        return dominant_emotion if 'dominant_emotion' in locals() else None
