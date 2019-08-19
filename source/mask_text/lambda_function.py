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
            if len(params) == 1 and 'text' in params:
                return True
            elif len(params) == 2 and 'text' in params and 'phiDetectionThreshold' in params and 0.0 <= float(params['phiDetectionThreshold']) <= 1.0:
                return True
        return False
    except Exception:
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

        # Validate input parameters
        if not validate_parameters(event):
            logging.error('Bad Request')
            return {
                'statusCode': 400,
                'body': ''
            }

        params = get_parameters(event)
        
        phi_detection_threshold = params['phiDetectionThreshold'] if 'phiDetectionThreshold' in params else float(os.environ['PHI_DETECTION_THRESHOLD'])

        phi_list = mask_lib.extract_phi_from_text(params['text'], phi_detection_threshold=phi_detection_threshold)
        masked_text = mask_lib.mask_entities_in_message(params['text'], phi_list)

        result = {
            'statusCode': '200',
            'body': json.dumps({'maskedText': masked_text})
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

