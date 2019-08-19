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
import mask_lib


def validate_parameters(event):
    try:
        if 'queryStringParameters' in event and 's3Bucket' in event['queryStringParameters'] and 's3Key' in event['queryStringParameters']:
            if not (type(event['queryStringParameters']['s3Bucket']) is str and type(event['queryStringParameters']['s3Key']) is str):
                return False
            if len(event['queryStringParameters']) == 2:
                return True
            if len(event['queryStringParameters']) == 3 and 'phiDetectionThreshold' in event['queryStringParameters'] \
                and type(event['queryStringParameters']['phiDetectionThreshold']) in [str, int, float] \
                and 0.0 <= float(event['queryStringParameters']['phiDetectionThreshold']) <= 1.0:
                return True
        return False
    except:
        return False

def get_parameters(event):
    # Required are s3Bucket and s3Key
    query_params = event['queryStringParameters']

    params = dict(
        s3Bucket=query_params['s3Bucket'],
        s3Key = query_params['s3Key'] 
    )

    # Optional is detection threshold
    if 'phiDetectionThreshold' in query_params:
        params['phiDetectionThreshold'] = query_params['phiDetectionThreshold']

    return params

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

        # Validate input parameters
        if not validate_parameters(event):
            logging.error('Bad Request')
            return {
                'statusCode': 400,
                'body': ''
            }

        # Get parameters
        params = get_parameters(event)
        s3_bucket = params['s3Bucket']
        s3_key = params['s3Key']
        phi_detection_threshold = params['phiDetectionThreshold'] if 'phiDetectionThreshold' in params else float(os.environ['PHI_DETECTION_THRESHOLD'])

        # Extract bounding boxes and text from image
        text_detections = mask_lib.get_text_in_image(s3_bucket, s3_key)

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

        result = {
            'statusCode': '200',
            'body': json.dumps(phi_locations)
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

