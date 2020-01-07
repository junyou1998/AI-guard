
import cv2
import time
import datetime
import imutils

import smtplib
from email.mime.text import MIMEText

import json

account = json.load(open('account.json', 'r', encoding='utf-8'))

gmail_user = account['user']
gmail_password = account['password']

html = """
<html>
    <head>
        <style>
            h1{
                color: #ff5e5e;
            }
            a{
                border-color: #0366d6;
                text-decoration: none;
                background-color: #0366d6;
                border: solid 1px #0366d6;
                border-radius: 5px;
                color: #ffffff;
                display: inline-block;
                font-size: 16px;
                font-weight: bold;
                margin: 0;
                padding: 10px 20px;
            }
            .footer{
                text-align: center;
                color: #888;
                border-color: #999;
            }
        </style>
    </head>
    <body>
        <h1>📢有人入侵!</h1>
        <img src="https://i.imgur.com/x4Red6D.png">
        <a href="google.com.tw">此為開源專案 點此瞭解更多❤</a>
        
        <div class="footer">
            <hr>
            Copyright © 2020 JunYou X 吳沅騏. All rights reserved
            <hr>
        </div>
        
    </body>
</html>
"""


msg = MIMEText(html,'html')
msg['Subject'] = 'AI 保全'
msg['From'] = gmail_user
msg['To'] = account['to_user']


def send_mail():
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.send_message(msg)
    server.quit()
    print('email sent!')
    
def motion_detection():
    video_capture = cv2.VideoCapture(0) 
    time.sleep(2)

    first_frame = None 
    first = None
    while True:
        
        frame = video_capture.read()[1] 
        text = 'Unoccupied'

        greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        gaussian_frame = cv2.GaussianBlur(greyscale_frame, (21,21),0)
       

        blur_frame = cv2.blur(gaussian_frame, (5,5)) 
       

        greyscale_image = blur_frame 

        if first_frame is None:
            first_frame = greyscale_image 
            
        else:
            pass


        frame = imutils.resize(frame, width=1000)
        frame_delta = cv2.absdiff(first_frame, greyscale_image) 
    
        thresh = cv2.threshold(frame_delta, 100, 255, cv2.THRESH_BINARY)[1]

        dilate_image = cv2.dilate(thresh, None, iterations=2)
        
        cnt = cv2.findContours(dilate_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        

        for c in cnt:
            if cv2.contourArea(c) > 800: 
                (x, y, w, h) = cv2.boundingRect(c) 

                cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2) 
                text = 'Occupied'
         
                if first is None:
                    '''寄信'''
                    send_mail()
                    first = datetime.datetime.now()
                    print(datetime.datetime.now())
                    
                record = (datetime.datetime.now()-first).seconds     
                    
                if(record>60):
                    '''寄信'''
                    send_mail()
                    first = datetime.datetime.now()
                    print('過很久了')
                else:
                    pass
                    
                print(record)
            else:
                pass
                
        font = cv2.FONT_HERSHEY_SIMPLEX 

        cv2.putText(frame, 'Room Status: %s' % (text), 
            (10,20), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (0, 0, 255), 2)
     
        cv2.putText(frame, datetime.datetime.now().strftime('%A %d %B %Y %I:%M:%S%p'), 
            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX , 0.35, (0, 0, 255),1) 
       
        cv2.imshow('Security Feed', frame)
        cv2.imshow('Threshold(foreground mask)', dilate_image)
        cv2.imshow('Frame_delta', frame_delta)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cv2.destroyAllWindows()
            break
                


if __name__=='__main__':    
    motion_detection()

