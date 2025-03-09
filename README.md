Python==3.6.9


pip3 install -r requirements.txt


How to inatll 

pyinstaller --onefile --noconsole LearningBot.py

cv2 폴더 인식안되는 문제때문에 아래 명령어로 실행해야함
pyinstaller --onefile --hidden-import cv2 --add-data "C:\Users\Obang\anaconda3\envs\learningBot_face\lib\site-packages\cv2\data;cv2/data" LearningBot.py