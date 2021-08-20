#######################################################################################
from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *
import sys
from MotionVanguard import social_distancing_config as config
from MotionVanguard.detection import detect_people
from scipy.spatial import distance as dist
import numpy as np
import argparse
import imutils
import cv2
import os
from playsound import playsound
import winsound
import threading 
import mysql.connector
import mysql
from collections import Counter 
##################################################################################
def camera(self):
    def annoy(x):
        for i in range(0,x): 
            winsound.Beep(741, 750)
    def most_frequent(List):
         return max(set(List), key = List.count) 
    pre=[]
    pre_num=[]
    def sound_effects(sound):
        if sound=="open":
            sound ="textaudio.wav"
        winsound.PlaySound(sound,winsound.SND_ASYNC)

    db1 = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="admin00000",
        database="testdatabase"
        )
    mycursor1 = db1.cursor()
    mycursor1.execute("DROP TABLE Violators_Cam1")
    mycursor1.execute("CREATE TABLE Violators_Cam1 (name VARCHAR(255), No VARCHAR(255), Path VARCHAR(255))")
    
    db2 = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="admin00000",
        database="testdatabase"
        )
    mycursor2 = db2.cursor()
    mycursor2.execute("DROP TABLE Violators_Cam2")
    mycursor2.execute("CREATE TABLE Violators_Cam2 (name VARCHAR(255), No VARCHAR(255), Path VARCHAR(255))")
    
    mycursor2.execute("SHOW TABLES")
    for x in mycursor2:
        print(x)
######################################################################################################################
    # load the COCO class labels our YOLO model was trained on
    labelsPath = os.path.sep.join([config.MODEL_PATH, "coco.names"])
    LABELS = open(labelsPath).read().strip().split("\n")
    
    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join([config.MODEL_PATH, "yolov3.weights"])
    configPath = os.path.sep.join([config.MODEL_PATH, "yolov3.cfg"])
    
    # load our YOLO object detector trained on COCO dataset (80 classes)
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    
    # check if we are going to use GPU
    if config.USE_GPU:
        # set CUDA as the preferable backend and target
        print("[INFO] setting preferable backend and target to CUDA...")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    
    # initialize the video stream and pointer to output video file
    print("[INFO] accessing video stream...")
    vs1 = cv2.VideoCapture(0)
    vs2 = cv2.VideoCapture(1)
    
    # loop over the frames from the video stream
    while True:
        # read the next frame from the file
        ret1, frame1 = vs1.read()  
        ret2, frame2 = vs2.read()
        
        frame1 = imutils.resize(frame1, width=700)
        results1 = detect_people(frame1, net, ln,
            personIdx=LABELS.index("person"))
        frame2 = imutils.resize(frame2, width=700)
        results2 = detect_people(frame2, net, ln,
            personIdx=LABELS.index("person"))
###############################################################################  
        violate1 = set()
    
        if len(results1) >= 2:
            centroids1 = np.array([r[2] for r in results1])
            D1 = dist.cdist(centroids1, centroids1, metric="euclidean")
            
            for i in range(0, D1.shape[0]):
                for j in range(i + 1, D1.shape[1]):
                
                    if D1[i, j] < config.MIN_DISTANCE:
                        violate1.add(i)
                        violate1.add(j)
        
        for (i, (prob, bbox1, centroid1)) in enumerate(results1):
            (startX, startY, endX, endY) = bbox1
            (cX, cY) = centroid1
            color1 = (0, 255, 0)
            
            if i in violate1:
                color1 = (0, 0, 255)
                sound_effects("open")
                img_counter = 0
                list_violate1 = format(len(violate1))
                #print(list_violate)
                aaa1 = "INSERT INTO Violators_Cam1 (name, No, Path) VALUES (%s, %s, %s)"
                bbb1 = ("Employee", list_violate1[-1], r"C:\Users\klyde\Desktop\thesis")
                mycursor1.execute(aaa1,bbb1)
                db1.commit()
                mycursor1.execute("SELECT * FROM Violators_Cam1")
                for x in mycursor1:
                    print(x)
                #while success:
                    #if img_counter % 10000 == 0:
                        #cv2.imwrite("frame%d.jpg" % img_counter, image)
                        #success,image = vs.read()
                        #print("screeshot taken")
                    #img_counter+=1
                    #print(img_counter)
                    
            # draw (1) a bounding box around the person and (2) the
            # centroid coordinates of the person,  
            cv2.rectangle(frame1, (startX, startY), (endX, endY), color1, 2)
            cv2.circle(frame1, (cX, cY), 5, color1, 1)
###############################################################################  
        violate2 = set()
        
        if len(results2) >= 2:
            centroids2 = np.array([r[2] for r in results2])
            D2 = dist.cdist(centroids2, centroids2, metric="euclidean")
            
            for i in range(0, D2.shape[0]):
                for j in range(i + 1, D2.shape[1]):
                
                    if D2[i, j] < config.MIN_DISTANCE:
                        violate2.add(i)
                        violate2.add(j)
                        
        for (i, (prob, bbox2, centroid2)) in enumerate(results2):
            (startX, startY, endX, endY) = bbox2
            (cX, cY) = centroid2
            color2 = (0, 255, 0)
            
            if i in violate2:
                color2 = (0, 0, 255)
                sound_effects("open")
                img_counter = 0
                list_violate2 = format(len(violate2))
                #print(list_violate)
                aaa2 = "INSERT INTO Violators_Cam2 (name, No, Path) VALUES (%s, %s, %s)"
                bbb2 = ("Employee", list_violate2[-1], r"C:\Users\klyde\Desktop\thesis")
                mycursor2.execute(aaa2,bbb2)
                db2.commit()
                mycursor2.execute("SELECT * FROM Violators_Cam1")
                for x in mycursor2:
                    print(x)
                #while success:
                    #if img_counter % 10000 == 0:
                        #cv2.imwrite("frame%d.jpg" % img_counter, image)
                        #success,image = vs.read()
                        #print("screeshot taken")
                    #img_counter+=1
                    #print(img_counter)
                    
            # draw (1) a bounding box around the person and (2) the
            # centroid coordinates of the person,      
            cv2.rectangle(frame2, (startX, startY), (endX, endY), color2, 2)
            cv2.circle(frame2, (cX, cY), 5, color2, 1)
###############################################################################  
        text = "Social Distancing Violations: {}".format(len(violate1))
        cv2.putText(frame1, text, (10, frame1.shape[0] - 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 3)
            
        text = "Social Distancing Violations: {}".format(len(violate2))
        cv2.putText(frame2, text, (10, frame2.shape[0] - 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 3)
            
        if (ret1):
            cv2.imshow('frame 1', frame1)
        if (ret2):
            cv2.imshow('frame 2', frame2)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    # After the loop release the cap object
    vs1.release()
    vs2.release()
    # Destroy all the windows
    cv2.destroyAllWindows()
############################################################################### 
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(444, 373)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.right = QFrame(self.centralwidget)
        self.right.setFrameShape(QFrame.StyledPanel)
        self.right.setFrameShadow(QFrame.Raised)
        self.right.setObjectName("right")
        self.verticalLayout = QVBoxLayout(self.right)
        self.verticalLayout.setObjectName("verticalLayout")
        self.body = QFrame(self.right)
        self.body.setFrameShape(QFrame.StyledPanel)
        self.body.setFrameShadow(QFrame.Raised)
        self.body.setObjectName("body")
        self.horizontalLayout_5 = QHBoxLayout(self.body)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout.addWidget(self.body)
        self.frame_6 = QFrame(self.right)
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_3 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_4 = QFrame(self.frame_6)
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.camera_button = QPushButton(self.frame_4)
        self.camera_button.setGeometry(QRect(13, 30, 351, 51))
        font = QFont()
        font.setKerning(True)
        self.camera_button.setFont(font)
        icon = QIcon()
        icon.addPixmap(QPixmap("icons/camera.svg"), QIcon.Normal, QIcon.Off)
        self.camera_button.setIcon(icon)
        self.camera_button.setCheckable(False)
        self.camera_button.setFlat(False)
        self.camera_button.setObjectName("camera_button")
        self.camera_button.clicked.connect(camera)
        self.horizontalLayout_3.addWidget(self.frame_4)
        self.verticalLayout.addWidget(self.frame_6)
        self.footer = QFrame(self.right)
        self.footer.setFrameShape(QFrame.StyledPanel)
        self.footer.setFrameShadow(QFrame.Raised)
        self.footer.setObjectName("footer")
        self.horizontalLayout_2 = QHBoxLayout(self.footer)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame_2 = QFrame(self.footer)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_3 = QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QLabel(self.frame_2)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label, 0, Qt.AlignBottom)
        self.horizontalLayout_2.addWidget(self.frame_2)
        self.frame = QFrame(self.footer)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setObjectName("frame")
        self.question_button = QPushButton(self.frame)
        self.question_button.setGeometry(QRect(80, 20, 33, 29))
        self.question_button.setText("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap("icons/help-circle.svg"), QIcon.Normal, QIcon.Off)
        self.question_button.setIcon(icon1)
        self.question_button.setFlat(False)
        self.question_button.setObjectName("question_button")
        self.horizontalLayout_2.addWidget(self.frame)
        self.verticalLayout.addWidget(self.footer, 0, Qt.AlignBottom)
        self.horizontalLayout.addWidget(self.right)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.camera_button.setText(_translate("MainWindow", "Open Camera"))
        self.label.setText(_translate("MainWindow", "MOTION VANGUARD V.1.1"))
import icons_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
