import os
import time
import cv2
from django.conf import settings
import numpy as np
import pytesseract
from PIL import Image
import imutils
from skimage.segmentation import clear_border
import json, os, time, cv2
from datetime import datetime
from django.http import HttpResponse
import numpy as np
from PIL import Image
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from anpr_app.anpr import cleanup_text, extract_num, find_and_ocr
from django.core.files.storage import FileSystemStorage
from anpr_app.models import Photo, User, VehicleOwner
from .anpr import image_processed, license_plate_recognition, roi_file

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"

def extract_num(img):
    image = img
    image = imutils.resize(image, width = 500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11,17,17)
    edge = cv2.Canny(gray, 170,200)
    cnts, new = cv2.findContours(edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    image1 = image.copy()
    cv2.drawContours(image1,cnts,-1,(0,225,0),3)
    cv2.imwrite("media/Con_1.png", image1)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
    NumberPlateCount = None
    image2 = image.copy()
    cv2.drawContours(image2,cnts,-1,(0,255,0),3)
    count = 0
    name = 1
    timestramp_ = str(time.time()).split(".")[0]
    timeStrp = "".join([timestramp_])  

    for i in cnts:
        perimeter = cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i,0.02*perimeter,True)
        if(len(approx)==4):
            NumberPlateCount = approx
            x,y,w,h = cv2.boundingRect(i)
            crp_img = image[y:y+h, x:x+w]
            cv2.imwrite(f'media/{timeStrp}.png', crp_img)
            name +=1
            break
    cv2.drawContours(image, NumberPlateCount, -1, (0,255,0),3)
    crp_img_loc = f'{timeStrp}.png'
    path = os.path.join(settings.MEDIA_ROOT, crp_img_loc)
    img_ = Image.open(path).filename

    # cv2.imshow("Cropped Image", cv2.imread(img_))
    text = pytesseract.image_to_string(img_, lang='eng')
    print("Number is : ", text)


    # cv2.imshow('original image', image)
    # cv2.imshow('Gray Image', gray)
    # cv2.imshow('Smoother', gray)
    # cv2.imshow("canny image", edge)
    # cv2.imshow("Canny after contours", image1)
    # cv2.imshow("Top 30 contours",image2)
    # cv2.imshow("Final Image", image)
    # cv2.waitKey(0)
    return text

minAR=4
maxAR=5
debug=False
timestramp_ = str(time.time()).split(".")[0]
timeStrp_roi = "".join([timestramp_])
roi_file = None

def debug_imshow(title, image, waitKey=True):
    # check to see if we are in debug mode, and if so, show the
    # image with the supplied title
    if debug:
        cv2.imshow(title, image)

        if waitKey:
            cv2.waitKey(0)

def locate_license_plate_candidates(gray, img, keep=5):
    # perform a blackhat morphological operation that will allow
    # us to reveal dark regions (i.e., text) on light backgrounds
    # (i.e., the license plate itself)
    rectKern = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKern)
    debug_imshow("Blackhat", blackhat)
    cv2.imwrite("media/blackhat.png", blackhat) 

    squareKern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    light = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, squareKern)
    light = cv2.threshold(light, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    debug_imshow("Light Regions", light)
    cv2.imwrite("media/light.png", light) 

    grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale
    grayed = cv2.bilateralFilter(grayed, 11, 17, 17) #Blur to reduce noise
    edged = cv2.Canny(grayed, 30, 200)
    cv2.imwrite("media/edged.png", edged) 
    cntses,new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    img1=img.copy()
    cv2.drawContours(img1,cntses,-1,(0,255,0),3)
    cv2.imwrite("media/contours.png", img1) 
    cntses = sorted(cntses, key = cv2.contourArea, reverse = True)[:30]
    screenCnt = None #will store the number plate contour
    img2 = img.copy()
    cv2.drawContours(img2,cntses,-1,(0,255,0),3) 
    cv2.imwrite("media/contours_50.png", img2)    


    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F,
                      dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = 255 * ((gradX - minVal) / (maxVal - minVal))
    gradX = gradX.astype("uint8")
    debug_imshow("Scharr", gradX)
    cv2.imwrite("media/gradX.png", gradX) 

    gradX = cv2.GaussianBlur(gradX, (5, 5), 0)
    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKern)
    thresh = cv2.threshold(gradX, 0, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    debug_imshow("Grad Thresh", thresh)
    cv2.imwrite("media/thresh.png", thresh) 

    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)
    debug_imshow("Grad Erode/Dilate", thresh)
    cv2.imwrite("media/thresh_2.png", thresh) 

    thresh = cv2.bitwise_and(thresh, thresh, mask=light)
    thresh = cv2.dilate(thresh, None, iterations=2)
    thresh = cv2.erode(thresh, None, iterations=1)
    debug_imshow("Final", thresh)
    cv2.imwrite("media/thresh_3.png", thresh) 
    
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:keep]
    # return the list of contours
    return cnts

def locate_license_plate(gray, candidates, clearBorder=True):
    # initialize the license plate contour and ROI
    lpCnt = None
    roi = None
    # loop over the license plate candidate contours
    for c in candidates:
        # compute the bounding box of the contour and then use
        # the bounding box to derive the aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        if ar >= minAR and ar <= maxAR:
            # store the license plate contour and extract the
            # license plate from the grayscale image and then
            # threshold it
            lpCnt = c
            licensePlate = gray[y:y + h, x:x + w]
            roi = cv2.threshold(licensePlate, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            
            # check to see if we should clear any foreground
            # pixels touching the border of the image
            # (which typically, not but always, indicates noise)
            if clearBorder:
                roi = clear_border(roi)
            
            # display any debugging information and then break
            # from the loop early since we have found the license
            # plate region
            debug_imshow("License Plate", licensePlate)
            debug_imshow("ROI", roi)
            roi_file = licensePlate
            cv2.imwrite("media/roi.png", roi)            
            # cv2.imwrite(f"media/lp{timeStrp_roi}.png", licensePlate)
            break
    # return a 2-tuple of the license plate ROI and the contour
    # associated with it
    return (roi, lpCnt)

def build_tesseract_options(psm=7):
    # tell Tesseract to only OCR alphanumeric characters
    alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    options = "-c tessedit_char_whitelist={}".format(alphanumeric)
    # set the PSM mode
    options += " --psm {}".format(psm)
    # return the built options string
    return options

def find_and_ocr(image, psm=7, clearBorder=False):
    # initialize the license plate text
    lpText = None
    # convert the input image to grayscale, locate all candidate
    # license plate regions in the image, and then process the
    # candidates, leaving us with the *actual* license plate
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    candidates = locate_license_plate_candidates(gray, image)
    (lp, lpCnt) = locate_license_plate(gray, candidates, clearBorder=clearBorder)
    # only OCR the license plate if the license plate ROI is not
    # empty
    
    if lp is not None:
        # OCR the license plate
        debug_imshow('pretessaract', lp)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        options = build_tesseract_options(psm=psm)
        lpText = pytesseract.image_to_string(lp, config=options)
        debug_imshow("License Plate", lp)
    
    # return a 2-tuple of the OCR'd license plate text along with
    # the contour associated with the license plate region
    return (lpText, lpCnt)

def cleanup_text(text):
    # strip out non-ASCII text so we can draw the text on the image
    # using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()

#*********************************************************************************
faceCascade = cv2.CascadeClassifier('anpr_app/haarcascade_russian_plate_number.xml')

def image_processed(img_file):
    # img = cv2.imread(img_file)
    print("Image Type*******", type(img_file))
    gray = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors = 5, minSize=(25,25))

    for (x,y,w,h) in faces:
        cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
        plate = gray[y: y+h, x:x+w]
        plate = cv2.blur(plate,ksize=(20,20))
        # put the blurred plate into the original image
        gray[y: y+h, x:x+w] = plate

    # cv2.imshow('plates', gray)
    cv2.imwrite("media/Rus_Plate.png", gray)


def processed_image(request):
    if request.method == 'POST':
        file = request.FILES.get('myfile', False)
        if file:
            print("file = ", file)
            img = Image.open(file).filename
            # print("Img*********", img)
            image = np.array(img)
            image_processed(img)
    return HttpResponse(json.dumps({"status":"false",}))


def image_process(request):
    if request.method == 'POST':
        file = request.FILES.get('myfile', False)
        if file:
            print("file = ", file)
            img = Image.open(file).filename
            print("Img*********", img)
            image = np.array(img)
            extract_num(img)
    return HttpResponse(json.dumps({"status":"false",}))


def process_image(request):
    if request.method == 'POST':
        file = request.FILES.get('myfile', False)
        if file:
            print("file = ", file)
            # Read the image via file.stream
            img = Image.open(file).convert('RGB')
            #img.show()

            #return jsonify({'msg': 'success', 'size': [img.width, img.height]})
            image = np.array(img)
            image = cv2.resize(image, (600, 360))
            # cv2.imshow("Output ANPR", image)
            # cv2.waitKey(0)

            (lpText, lpCnt) = find_and_ocr(image)            

            if lpText is not None and lpCnt is not None:
                # fit a rotated bounding box to the license plate contour and
                # draw the bounding box on the license plate
                box = cv2.boxPoints(cv2.minAreaRect(lpCnt))
                box = box.astype("int")
                cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
                
                # compute a normal (unrotated) bounding box for the license
                # plate and then draw the OCR'd license plate text on the
                # image
                (x, y, w, h) = cv2.boundingRect(lpCnt)
                cv2.putText(image, cleanup_text(lpText), (x, y - 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                
                # show the output ANPR image
                #print(format(lpText))
                print("[INFO] {}".format(lpText))
                # cv2.imshow("Output ANPR", image)
                # cv2.waitKey(0)
                timestramp_ = str(time.time()).split(".")[0]
                timeStrp = "".join([timestramp_])                                
                try:  
                    cv2.imwrite(f"media/{timeStrp}.png", image) 
                    # cv2.imwrite(f"media/lp{timeStrp}.png", roi_file) 
                    path = os.path.join(settings.MEDIA_ROOT, f'{timeStrp}.png')
                    # path_roi = os.path.join(settings.MEDIA_ROOT, f'lp{timeStrp_roi}.png')               
                    img_ = Image.open(path).filename
                    # img_roi = Image.open(path_roi).filename
                    # Photo.objects.filter(title='photo').update(img=img_, roi=img_roi)
                    imgFile = Photo(img=img_)
                    # imgFile_roi = Photo.objects.get(roi=img_roi)
                except FileNotFoundError:
                    print('File Error ********')                
                queryshot = VehicleOwner.objects.filter(plate_number__exact=format(cleanup_text(lpText)))
                if queryshot.exists():                    
                    return HttpResponse(json.dumps({
                        "status": "true", 
                        'plate': format(cleanup_text(lpText)), 
                        'name': f'{queryshot.first().first_name} {queryshot.first().last_name}',
                        'age': queryshot.first().age,
                        'model': queryshot.first().vehicle_model,
                        'date': str(datetime.now().strftime("%d-%m-%Y %H:%M")),
                        'url': queryshot.first().avatar.url, 
                        'imgurl': imgFile.img.url,
                        # 'roiurl': imgFile_roi.roi.url,               
                    }))
                else:
                    return HttpResponse(json.dumps({"status":"false", 'imgurl': imgFile.img.url,}))
            else:
                return HttpResponse(json.dumps({"status":"Error", 'plate':'unable to decode'}))
        else:
            messages.error(request, 'Upload an Image!')

