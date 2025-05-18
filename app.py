import os
from flask import Flask, request, render_template
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

def pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
    return images[0]

def compare_images(img1, img2):
    gray1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    output_img = np.array(img2).copy()
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 10 and h > 10:
            cv2.rectangle(output_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
    return output_img

@app.route('/', methods=['GET', 'POST'])
def upload_and_compare():
    if request.method == 'POST':
        old_path = os.path.join(UPLOAD_FOLDER, 'old_plan.pdf')
        new_path = os.path.join(UPLOAD_FOLDER, 'new_plan.pdf')
        request.files['file1'].save(old_path)
        request.files['file2'].save(new_path)
        img1 = pdf_to_image(old_path)
        img2 = pdf_to_image(new_path)
        result_array = compare_images(img1, img2)
        result_img = Image.fromarray(result_array)
        result_path = os.path.join(STATIC_FOLDER, 'result.png')
        result_img.save(result_path)
        return render_template('result.html', result_image='result.png')
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
