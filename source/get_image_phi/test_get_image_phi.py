import unittest
from lambda_function import validate_parameters
import sys

class TestRequestHeaders(unittest.TestCase):

    def test_validate_parameters(self):
        # Two correct params
        event_correct_2 = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey'}}
        # Three correct params
        event_correct_3_str = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'phiDetectionThreshold': '0.1'}}
        event_correct_3_int = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'phiDetectionThreshold': 0.1}}
        event_correct_3_float = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'phiDetectionThreshold': 0}}
        # Correct param keys but wrong values
        event_multi_bucket = {'queryStringParameters': {'s3Bucket': ['mybucket', 'mybucket2'], 's3Key': 'mykey'}}
        event_multi_key = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': ['mykey','mykey2']}}
        event_incorrect_threshold_str = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'phiDetectionThreshold': 'f'}}
        event_incorrect_threshold_multi = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'phiDetectionThreshold': [0.1,0.2]}}
        event_incorrect_threshold_oob = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'phiDectectionThreshold': 2}}
        # incorrect param (bucket)
        event_incorrect_param_bucket = {'queryStringParameters': {'s3Bucketa': 'mybucket', 's3Key': 'mykey'}}
        # incorrect param (key)
        event_incorrect_param_key = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Keya': 'mykey'}}
        # Not two or 3 params
        event_incorrect_param_num = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'phiDetectionThreshold': '0.1', 'asdf': '1234'}}
        # queryStringParameters missing
        event_missing_querystring = {'queryStringParametersasdf': {'s3Bucket': 'mybucket', 's3Key': 'mykey'}}
        
        self.assertTrue(validate_parameters(event_correct_2))
        self.assertTrue(validate_parameters(event_correct_3_str))
        self.assertTrue(validate_parameters(event_correct_3_int))
        self.assertTrue(validate_parameters(event_correct_3_float))

        self.assertFalse(validate_parameters(event_multi_bucket))
        self.assertFalse(validate_parameters(event_multi_key)) 
        self.assertFalse(validate_parameters(event_incorrect_threshold_str))
        self.assertFalse(validate_parameters(event_incorrect_threshold_multi))
        self.assertFalse(validate_parameters(event_incorrect_threshold_oob))
        self.assertFalse(validate_parameters(event_incorrect_param_bucket))
        self.assertFalse(validate_parameters(event_incorrect_param_key))
        self.assertFalse(validate_parameters(event_incorrect_param_num))
        self.assertFalse(validate_parameters(event_missing_querystring))


if __name__ == '__main__':
    unittest.main()