import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import random as rd
import numpy as np
import time

capture = cv2.VideoCapture(0)
frameWidth = 500
frameHeight = 500
capture.set(3, frameWidth)
capture.set(4, frameHeight)


class Ball():
    def __init__(self, radius=20, color=(0, 0, 255), startX=50, startY=50, step=10):
        self.radius = radius
        self.color = color
        self.startX = startX
        self.startY = startY
        self.stepX = step
        self.stepY = step
        self.img = None
        self.score1 = 0
        self.score2 = 0

    def createBall(self, image):
        cv2.circle(image, (self.startX, self.startY), self.radius, self.color, cv2.FILLED)
        self.moveRandom()

    def moveRandom(self):
        self.startX -= self.stepX
        self.startY -= self.stepY

    def drawRect(self,start_point,end_point):
        cv2.rectangle(self.img, start_point, end_point,(0,255,0),10)

    def wallCollision(self, obs1=None, obs2=None):
        if self.startX < obs1.posx+self.radius*4 and obs1.posy<self.startY<obs1.posy+obs1.height:
            self.stepX *= -1
            print("collision to wall 1")

        if self.startX+self.radius*3 > obs2.posx and obs2.posy<self.startY<obs2.posy+obs2.height:
            self.stepX *= -1
            print("collision to wall 2")

    def bounceBack(self):
        if self.startX < self.radius * 2:
            self.stepX *= -1
            self.score2 += 1
        if self.startX > frameWidth:
            self.stepX *= -1
            self.score1 += 1
        if self.startY < 2 * self.radius:
            self.stepY *= -1
        if self.startY > frameHeight - 20:
            self.stepY *= -1

    def drawText(self,text,pos,color=(255,255,255)):
        cv2.putText(self.img, text,pos, cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, color, 1, cv2.LINE_AA)


ball = Ball(radius=15, color=(100, 255, 100), step=18, startX=500)


class Wall():
    def __init__(self, posx=0, posy=0, width=5, height=20):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.color = (23,108,173)
        self.thickness = -1

    def createWall(self, image, pos_y):
        self.posy = pos_y
        start_point = (self.posx, self.posy)
        end_point = (self.posx + self.width, self.posy + self.height)
        cv2.rectangle(image, start_point, end_point, self.color, self.thickness)


detector = HandDetector(maxHands=2, detectionCon=0.8)

wall1 = Wall(posx=100, posy=10, width=35, height=100)
wall2 = Wall(posx=500, posy=10, width=35, height=100)

hand_cy1 = 10
hand_cy2 = 10
score1,score2 = 0,0

while True:
    success, img = capture.read()
    img = cv2.flip(img, 1)
    hand, image = detector.findHands(img, draw=True)
    # zimg = np.ones((frameHeight, frameWidth, 3), dtype=np.float)/10
    # img = img*zimg
    # overlay = img.copy()
    # x, y, w, h = 0,0 , 1000, 10000
    # cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 250,250), -1)
    # alpha = 0.4  # Transparency factor.
    # img = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

    if hand:
        if len(hand) == 2:
            hand_cx1 = hand[0]['lmList'][8][0]
            hand_cy1 = hand[0]['lmList'][8][1]

            hand_cx2 = hand[1]['lmList'][8][0]
            hand_cy2 = hand[1]['lmList'][8][1]

            cv2.circle(img, (hand_cx1, hand_cy1), 5, (255, 0, 100), cv2.FILLED)
            cv2.circle(img, (hand_cx2, hand_cy2), 5, (100,0, 255), cv2.FILLED)

        if len(hand) == 1:
            hand_cx1 = hand[0]['lmList'][8][0]
            hand_cy1 = hand[0]['lmList'][8][1]

            cv2.circle(img, (hand_cx1, hand_cy1), 5, (255, 0, 100), cv2.FILLED)


    ball.img = img
    ball.createBall(img)
    ball.bounceBack()
    wall1.createWall(img, hand_cy1)
    wall2.createWall(img, hand_cy2)
    ball.wallCollision(wall1, wall2)

    ball.drawText("Player 1 ",(10,20),color=(0,0,0))
    ball.drawText("Player 2",(520,20),color=(0,0,0))

    ball.drawText(f"Score : {ball.score1}",(10,40),color=(0,0,0))
    ball.drawText(f"Score : {ball.score2}",(520,40),color=(0,0,0))

    cv2.imshow("Ping Pong", img)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break
