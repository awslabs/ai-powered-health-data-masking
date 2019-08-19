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
import threading
import traceback
import mask_lib


def timeout(event, context):
    raise Exception('Execution is about to time out. Exiting...')

def parse_object_pairs(pairs):
    return pairs

def validate_parameters(event):
    try: 
        if 'body' in event:
            decoder = json.JSONDecoder(object_pairs_hook=parse_object_pairs)
            decoded = decoder.decode(event['body'])
            params = json.loads(event['body'])
            
            # Ensure not duplicate keys
            if len(params) != len(decoded):
                return False
            if 's3Bucket' in params and 's3Key' in params and 'destinationBucket' in params and 'destinationKey' in params:
                if params['s3Bucket'] == params['destinationBucket'] and params['s3Key'] == params['destinationKey']:
                    return False # Same location
                if not (type(params['s3Bucket']) is str and type(params['s3Key']) is str and type(params['destinationBucket']) is str and type(params['destinationKey']) is str):
                    return False
                if len(params) == 4:
                    return True
                elif len(params) == 5 and 'phiDetectionThreshold' in params and type(params['phiDetectionThreshold']) in [str, int, float] and 0.0 <= float(params['phiDetectionThreshold']) <= 1.0:
                    return True
        return False
    except:
        return False

def get_parameters(event):
    # Validate parameters
    try:
        params = json.loads(event['body']) 
        return params
    except Exception as e:
        raise e

def lambda_handler(event, context):
    try:
        global log_level
        log_level = str(os.environ.get('LOG_LEVEL')).upper()
        if log_level not in [
                                'DEBUG', 'INFO',
                                'WARNING', 'ERROR',
                                'CRITICAL'
                            ]:
            log_level = 'ERROR'
        logging.getLogger().setLevel(log_level)

        timer = threading.Timer((context.get_remaining_time_in_millis() / 1000.00) - 1, timeout, args=[event, context])
        timer.start()

        if not validate_parameters(event):
            logging.error('Bad Request')
            return {
                'statusCode': 400,
                'body': ''
            }

        redacted_box_color=os.environ['REDACTED_BOX_COLOR']

        # Get parameters
        params = get_parameters(event)
        source_bucket = params['s3Bucket']
        source_key = params['s3Key']
        destination_bucket = params['destinationBucket']
        destination_key = params['destinationKey']
        phi_detection_threshold = params['phiDetectionThreshold'] if 'phiDetectionThreshold' in params else float(os.environ['PHI_DETECTION_THRESHOLD'])

        # Extract bounding boxes and text from image
        text_detections = mask_lib.get_text_in_image(source_bucket, source_key)

        # The various text detections are returned in a JSON object.  Aggregate the text into a single large block and
        # keep track of the offsets. This will allow us to make a single call to Amazon Comprehend Medical for
        # PHI detection and minimize our Comprehend Medical service charges.
        concatenated_text, offset_array = mask_lib.concatenate_image_text(text_detections)

        # Extract PHI from text using Comprehend Medical
        phi_list = mask_lib.extract_phi_from_text(concatenated_text, phi_detection_threshold=phi_detection_threshold)

        # Amazon Comprehend Medical will return a JSON object that contains all of the PHI detected in the text block with
        # offset values that describe where the PHI begins and ends.  We can use this to determine which of the text blocks 
        # detected by Amazon Rekognition should be redacted.  The 'phi_locations' list is created to keep track of the
        # bounding boxes that potentially contain PHI.
        phi_locations = mask_lib.identify_phi_locations_in_image(phi_list, offset_array, text_detections)

        # Now this list of bounding boxes will be used to draw boxes over the PHI text.
        response = mask_lib.mask_phi_in_image(source_bucket, source_key, phi_locations, redacted_box_color, destination_bucket, destination_key)

        result = {
            'statusCode': '200',
            'body': json.dumps({'maskedImagePath': 's3://%s/%s' % (destination_bucket, destination_key)})
        }

        return result
    except Exception as error:
        logging.error('lambda_handler error: %s' % (error))
        logging.error('lambda_handler trace: %s' % traceback.format_exc())
        result = {
            'statusCode': '500',
            'body':  json.dumps({'message': 'error'})
        }
        return result

