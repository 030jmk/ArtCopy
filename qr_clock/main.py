from flask import Flask, render_template, url_for, redirect
from time import sleep
from datetime import datetime
import qrcode
import os

def current_time_qr(filename="time.png"):

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(datetime.now().strftime("%H:%M"))
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="white",
        back_color="black")
    img.save(os.path.join("static",filename))

app = Flask(__name__)

@app.route('/')
def index():
    current_time_qr()
    img_location= os.path.join("static","time.png")
    return render_template("index.html", image=img_location, alt=datetime.now().strftime("%H:%M"))


if __name__ == '__main__':  
    Flask.run(app, host='0.0.0.0', port=80, debug=True)  
