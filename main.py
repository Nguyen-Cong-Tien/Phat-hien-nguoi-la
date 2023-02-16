#khai báo các module cần sử dụng
from flask import Flask, render_template, Response, request
import cv2
import datetime, time
from threading import Thread
import json
import cvzone
import requests 

#khai báo các biến sử dụng
global rec_frame, switch, face
face=0
switch=1
timedelay = {
  "delay": str(datetime.datetime.now()+datetime.timedelta(minutes = -10))
}
timedelay = json.loads(json.dumps(timedelay))

#khởi tạo server flask app  
app = Flask(__name__, template_folder='./templates')
#khởi tạo haarcascade dùng để nhận diện khuôn mặt
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
#khởi tạo webcam
camera = cv2.VideoCapture(0)
#hàm phát hiện khuôn mặt và cứ sau 10 giây sẽ chụp ảnh và gửi đến server 
def detect_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    #Cho phép nhận diện nhiều khuôn mặt
    faces = face_cascade.detectMultiScale(gray, 1.1, 6)
    if len(faces) >0:
        # print(1)
        count=0
        #Tạo hình chữ nhật xung quanh khuôn mặt
        for(x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            count+=1
            cvzone.putTextRect(frame,f'Person{count}',(30,60),scale=2,thickness=2,offset=5)
            fmt1 = '%Y-%m-%d %H:%M:%S.%f'
            delay = datetime.datetime.strptime(timedelay['delay'], fmt1)
            datetime_now = datetime.datetime.now()
            if (datetime_now - delay).total_seconds() >= 10:
                print(datetime_now)
                print(delay)
                print((datetime_now - delay).total_seconds())
                timedelay['delay'] = str(datetime_now)
                print(timedelay)
                img_item = "%s.jpg" % (datetime.datetime.now().strftime("%d-%m-%Y_%Hh%Mm%Ss"))
                cv2.imwrite(img_item,frame)
                # requests.post('http://127.0.0.1:3000/email/send', json={"img": img_item,"content":'CÓ NGƯỜI VÀO NHÀ YẾN !!!'})
    else:
        # print(0)
        cvzone.putTextRect(frame,f'NO-Person',(30,60),scale=2,thickness=2,offset=5)
    return frame

def gen_frames():  # tạo từng khung hình từ máy ảnh
    global out, capture,rec_frame
    while True:
        success, frame = camera.read() 
        if success:
            if(face):                
                frame= detect_face(frame)      
            try:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass


@app.route('/')
def index():
    return render_template('index.html')
    
    
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# kiểm tra các yêu cầu được gửi từ client
@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        print(request.form)
        if  request.form.get('dectect') == 'Detect Person':
            global face
            face=not face 
            if(face):
                time.sleep(4)                
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
    
camera.release()
cv2.destroyAllWindows()     
