import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
tipIds = [4, 8, 12, 16, 20]
#####
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

print(volRange)
#########
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = hands.process(imgRGB)

    lmList = []

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                ####################Audio
                if len(lmList) == 21:
                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[8][1], lmList[8][2]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                    #green
                    cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
                    #black
                    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 3)
                    #white
                    cv2.circle(img, (cx, cy), 3, (255, 255, 255), cv2.FILLED)

                    length = math.hypot(x2 - x1, y2 - y1)
                    #print(length)

                    # length 50 -200
                    if length < 50:
                        #blue
                        cv2.circle(img, (cx, cy), 7, (255, 50, 0), cv2.FILLED)
                    if length > 200:
                        #red
                        cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

                    vol = np.interp(length, [50, 100], [minVol, maxVol])

                    volume.SetMasterVolumeLevel(vol, None)

                    ###############################5
                    fingers = []

                    if lmList[tipIds[0]][1] < lmList[tipIds[0] - 2][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                    for tip in range(1, 5):
                        if lmList[tipIds[tip]][2] < lmList[tipIds[tip] - 2][2]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                    totalFingers = fingers.count(1)
                    #print(totalFingers)
                    cv2.putText(img, f'{totalFingers}', (40, 80), cv2.FONT_HERSHEY_SIMPLEX,
                                3, (0, 0, 255), 6)

    cv2.imshow('Hand Tracker', img)
    if cv2.waitKey(5) & 0xff == 27:
        break
