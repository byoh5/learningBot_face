import cv2
from deepface import DeepFace

class Inference():
    def __init__(self, c_th_IpCamera):
        self.c_th_ipCamera = c_th_IpCamera

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
                detector_backend='opencv',
                enforce_detection=False
            )
            dominant_emotion = result[0]['dominant_emotion']
            print(f"Emotion: {dominant_emotion}")
            return dominant_emotion  # 결과 반환
        except Exception as e:
            print(f"Inference Error: {e}")
            return None  # 감정 분석 실패 시 None 반환
