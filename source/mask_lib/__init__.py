#!/usr/bin/python
# -*- coding: utf-8 -*-
###################################################################################
#  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.        #
#                                                                                 #
#  Licensed under the "MIT No Attribution" License (the "License"). You may not   #
#  use this file except in compliance with the License. A copy of the             #
#  License is located in the "license" file accompanying this file.               #
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS #
#  OF ANY KIND, express or implied. See the License for the specific language     #
#  governing permissions and limitations under the License.                       #
###################################################################################

import logging
import json
import os
import boto3
import traceback
import threading
import base64
import sys
import io
from PIL import Image, ImageDraw, ImageColor


s3 = boto3.resource('s3', use_ssl=True)
cm = boto3.client('comprehendmedical', use_ssl=True)
rekognition = boto3.client('rekognition', use_ssl=True)

def get_text_in_image(s3_bucket, s3_key):
    response = rekognition.detect_text(Image={
            'S3Object':{'Bucket':s3_bucket, 'Name': s3_key}
        })
    return response['TextDetections']

def get_source_bucket_key_from_event(event):
    return event['SourceBucket'], event['SourceKey']

def get_destination_bucket_key_from_event(event):
    return event['DestinationBucket'], event['DestinationKey']

def identify_phi_locations_in_image(phi_list, offset_array, text_detections):
    phi_locations = []
    phi_text_detections = []

    for phi in phi_list:
        for i in range(len(offset_array)-1):
            if offset_array[i] <= phi['BeginOffset'] < offset_array[i+1] and text_detections[i]['Geometry']['BoundingBox'] not in phi_text_detections:
                phi_locations.append({phi['Text']: text_detections[i]['Geometry']['BoundingBox']})
                phi_text_detections.append(text_detections[i]['Geometry']['BoundingBox'])

    return phi_locations

def mask_phi_in_image(bucket, key_name, phi_boxes_list, redacted_box_color, destination_bucket, destination_key):
    # Create image
    img_bucket = s3.Bucket(bucket)
    img_object = img_bucket.Object(key_name)
    image_data = io.BytesIO()
    img_object.download_fileobj(image_data)

    im = Image.open(image_data).convert('RGB')
    draw = ImageDraw.Draw(im)

    image_width, image_height = im.size
    color = ImageColor.getrgb(redacted_box_color)

    for phi in phi_boxes_list:
        # Only one value in the dictionary
        box = [ phi[_] for _ in phi][0]
        #The bounding boxes are described as a ratio of the overall image dimensions, so we must multiply them
        #by the total image dimensions to get the exact pixel values for each dimension.
        x0 = image_width * box['Left']
        y0 = image_height * box['Top']
        x1 = x0 + image_width * box['Width']
        y1 = y0 + image_height * box['Height']
        draw.rectangle([(x0,y0), (x1,y1)], outline=color, fill=color)

    dest_bucket = s3.Bucket(destination_bucket)
    proc_img_data = io.BytesIO()

    im.save(proc_img_data, 'png')
    proc_img_data.seek(0)
    
    dest_bucket.put_object(Body=proc_img_data, ContentType='image/png', Bucket=bucket, Key=destination_key)  
    
    return 's3//%s/%s' % (destination_bucket, destination_key)


def concatenate_image_text(image_text_list):
    detected_text = [ _['DetectedText'] for _ in image_text_list]
    
    #The various text detections are returned in a JSON object.  Aggregate the text into a single large block and
    #keep track of the offsets.  This will allow us to make a single call to Amazon Comprehend Medical for
    #PHI detection and minimize our Comprehend Medical service charges.
    offset_array = []
    combined_text = ''

    for image_text in detected_text:
        offset_array.append(len(combined_text))
        combined_text = combined_text + image_text + ' ' # Add image text to the total text for CM

    # append last one
    offset_array.append(len(combined_text))

    return combined_text, offset_array

def extract_phi_from_text(message, phi_detection_threshold = 0.0):
    response = cm.detect_phi(Text=message)

    # Now filter by PHI threshold
    return [ _ for _ in response['Entities'] if _['Score'] >= phi_detection_threshold ]


def mask_entities_in_message(message, entity_list):
    for entity in entity_list:
        message = message.replace(entity['Text'], entity['Type'])

    return message
