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
import traceback
import mask_lib


def parse_object_pairs(pairs):
    return pairs

def validate_parameters(event):
    # Validate parameters
    # Need to check that there are only 2 and only 2 parameters in query string, s3Bucket and s3Key
    try:
        if 'queryStringParameters' in event and len(event['queryStringParameters']) == 2:
            if 's3Bucket' in event['queryStringParameters'] and 's3Key' in event['queryStringParameters']:
                if type(event['queryStringParameters']['s3Bucket']) is str and type(event['queryStringParameters']['s3Key']) is str:
                    return True
        return False
    except:
        return False

def get_parameters(event):
    # Validate parameters
    # Need to check that there are only 2 and only 2 parameters in query string, s3Bucket and s3Key
    try:
        query_params = event['queryStringParameters']
        return query_params['s3Bucket'], query_params['s3Key'] 
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

        # Validate input parameters
        if not validate_parameters(event):
            logging.error('Bad Request')
            return {
                'statusCode': 400,
                'body': ''
            }

        # Validate and extract query parameters for Amazon S3 location for image
        s3_bucket, s3_key = get_parameters(event)

        # Extract bounding boxes and text from image
        text_detections = mask_lib.get_text_in_image(s3_bucket, s3_key)

        result = {
            'statusCode': '200',
            'body': json.dumps(text_detections)
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

