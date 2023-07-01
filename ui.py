# Configure Python Environment for streamlit UI
# ---- Basic modules ----
import os 
import sys
import random
import zipfile
import io
import numpy as np
import pandas as pd
import time

# ---- Image processing ----
import cv2
from PIL import Image
from matplotlib import cm

# ---- streamlit ----
import streamlit as st

# ---- unet model related ----
from unet import data
from unet.model import Metrics, UnetModel, get_model
from unet import process as P


# UI components
# ---- Logo ----
st.image('./logo/logo.png')

# ---- Sidebar ----
st.sidebar.title('Cell Segger v1.0')
st.sidebar.caption('Outline cells in microscope images')
st.sidebar.markdown('[Jingqi Duan, Ph.D](https://github.com/duanjingqi)')
st.sidebar.markdown('---')
st.sidebar.markdown('''
This software is dedicated to\n
Bayanhar, my lovely daughter, who involved from start to finish by occupying me for her games and snacks;\n
Jianle, my wife\n
Shuzhen & Haiyu, my parents\n
for their steady mental and financial support.
''')
st.sidebar.markdown('---')

preview = st.sidebar.checkbox(
    'Preview',
    value=False,
    help='Preview input images'
    )

scale = float(
    st.sidebar.number_input(
        'scale',
        min_value=0.2,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help='Scale for downsizing input image',
        disabled=bool(preview),
        )
    )

input_mode = st.selectbox(
    'Color space of input images',
    ('L', 'RGB'),
    )


# App
# ---- File uploader ----
image_files = st.file_uploader('Upload images',
                         key='file_uploader',
                         type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'],
                         accept_multiple_files=True)

images_df = pd.DataFrame(columns=['name', 'width', 'height', 'rle_annotation', 'bytes_original', 'bytes_predicted'])

if len(image_files) > 0:

    st.info(f'{len(image_files)} images uploaded')

    # Cell segmentation with a pre-trained U-Net model
    X = data.ImageSequenceFromBytes(image_files)
    # Load model
    unet_model = get_model(input_mode)
    # Prediction
    start = time.time()
    with st.spinner('U-Net model prediction in progress...'):

        annotations = unet_model.predict(X)
        st.success('Done!')
        end = time.time()
        elapsed_time = end - start

    st.info(f'Prediction took {round(elapsed_time/60, 2)} min to complete.')

    # Collect info and store them in images_df
    for idx, (img, pred) in enumerate(zip(image_files, annotations)):

        ori_fp = img

        # Image name
        name = ori_fp.name

        # Image dimension
        original_dimension = Image.open(ori_fp).size

        # Image of predicted annotation
        pred = np.uint8(pred * 255) 
        pred_in_gray = cv2.cvtColor(pred, cv2.COLOR_BGR2GRAY)
        pred_in_gray = cv2.resize(pred_in_gray, original_dimension, interpolation=cv2.INTER_AREA)

        # RLE annotation
        rle = P.annotation2rle(pred_in_gray, binary=False)
       
        # Bytes file
        pred_fp = io.BytesIO()
        pred_image = Image.fromarray(pred_in_gray)
        pred_image.save(pred_fp, 'PNG')
        pred_fp.seek(0)

        # Store in images_df
        images_df.loc[idx] = {'name': name,
                              'width': original_dimension[0],
                              'height': original_dimension[1],
                              'rle_annotation': rle, 
                              'bytes_original': ori_fp,
                              'bytes_predicted': pred_fp}
        
    if preview:

        # Preview original and predicted images
        idx = random.choice(range(images_df.shape[0]))
        col1, col2 = st.columns(2)
        # Original
        with col1: 
            st.header('Original')
            original = Image.open(images_df.loc[idx, 'bytes_original'])
            st.image(original)
        # Predicted
        with col2: 
            st.header('Predicted')
            predicted = Image.open(images_df.loc[idx, 'bytes_predicted'])
            st.image(predicted)

    else:

        pass

else: 

    st.warning('Please upload an image')


# Write predicted image to a zipfile
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'a') as zf:

    # Add Welcome message
    welcome = b'''Thank you very much for using Cell Segger.
    Please reach out to duanjingqi@gmail.com for any question.'''
    zf.writestr('welcome.txt', welcome)

    for _, row in images_df.iterrows():

        name = row['name'].split('.')[0] + '_annotation.png'
        zf.writestr(name, row['bytes_predicted'].read())

    zf.writestr('images.csv', images_df.iloc[:, 0:4].to_csv())


st.download_button(label='Download results',
                   data=zip_buffer.getvalue(),
                   file_name='prediction.zip',
                   mime='application/zip')