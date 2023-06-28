# Configure Python environment
# ---- Basic modules ----
import cv2
import zipfile
import io
from typing import List


# ---- FastAPI ----
from fastapi import FastAPI
from fastapi import File
from fastapi import UploadFile
from fastapi import HTTPException
from fastapi import Depends
from fastapi import Response
from fastapi.responses import StreamingResponse

# ---- unet ----
from unet import data
from unet.model import get_model


# Global variables
OPEN_MSSG = {"Application": "CellSegger-0.0",
            "Author": "Jingqi Duan, Ph.D",
            "Date": "04-28-2023",
            "Dedicated to": "Bayanhar my lovely daughter, Shuzheng and Haiyu my supportive parents",
            }


# Some functions

def is_accepted_format(infile): 
    """Check infile format and return True if it is accepted or False if not accepted"""
    
    accepted_format = infile.content_type.split('/')[-1] in ('bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff')
    return accepted_format


# API interface
app = FastAPI()

@app.get("/") 
async def root():
    return OPEN_MSSG


@app.post("/predict/single", response_class=Response)
async def predict_single(infile: UploadFile = File(...), model = Depends(get_model)):

    name = infile.filename
    # Check input image format
    if not is_accepted_format(infile):
        raise HTTPException(400, detail=f"{name} is in a unaccepted format! Please upload a bmp, jpeg/jpg, png or tiff/tif image.")
    # Predict
    response = []
    X = data.ImageSequenceFromBytes([infile.file])
    prediction = model.predict(X)
    predicted_annotation = prediction[0] * 255
    # Encode the predicted image
    im = cv2.imencode('.png', predicted_annotation)[1]
    name_for_prediction = name.split('.')[0] + '_annotation.png'
    headers = {'Content-Disposition': f'attachment; filename={name_for_prediction}'}

    return Response(im.tobytes() , headers=headers, media_type='image/png')
    

@app.post("/predict/batch", response_class=Response)
async def predict_batch(infiles: List[UploadFile], model = Depends(get_model)):

    images_in_bytes = []
    imagenames = []
    for _file in infiles:
        if not is_accepted_format(_file):
            print (f"{_file.filename} is in a unaccepted format! Please upload bmp, jpeg/jpg, png or tiff/tif images.")
            continue
        images_in_bytes.append(_file.file)
        imagenames.append(_file.filename)

    # Predict
    X = data.ImageSequenceFromBytes(images_in_bytes)
    predictions = model.predict(X)
    # Compress into zipfile
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a') as zf:
        for _, (name, predict) in enumerate(zip(imagenames, predictions)):
            name_for_prediction = name.split('.')[0] + '_annotation.png'
            predict = predict * 255

            zf.writestr(name_for_prediction, predict)

    headers = {'Content-Disposition': 'attachment; filename="predictions.zip"',
               'Content-Length': str(zip_buffer.getbuffer().nbytes)}
    media_type='application/x-zip-compressed'
    response = StreamingResponse(iter([zip_buffer.getvalue()]),
                                 media_type=media_type,
                                 headers=headers)

    return response