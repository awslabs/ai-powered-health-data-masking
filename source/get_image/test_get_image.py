import unittest
from lambda_function import validate_parameters
import sys

class TestRequestHeaders(unittest.TestCase):

    def test_validate_parameters(self):
        # Two correct params
        event_correct = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey'}}
        # incorrect param (bucket)
        event_incorrect_param_bucket = {'queryStringParameters': {'s3Bucketa': 'mybucket', 's3Key': 'mykey'}}
        # incorrect param (key)
        event_incorrect_param_key = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Keya': 'mykey'}}
        # Not two params
        event_incorrect_param_num = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': 'mykey', 'asdf': '1234'}}
        # Two params, multi header key
        event_multi_header_key = {'queryStringParameters': {'s3Bucket': 'mybucket', 's3Key': ['mykey','mykey2']}}
        # Two params, multi header bucket
        event_multi_header_bucket = {'queryStringParameters': {'s3Bucket': ['mybucket', 'mybucket2'], 's3Key': 'mykey'}}
        # queryStringParameters missing
        event_missing_querystring = {'queryStringParametersasdf': {'s3Bucket': 'mybucket', 's3Key': 'mykey'}}
        
        self.assertTrue(validate_parameters(event_correct))
        self.assertFalse(validate_parameters(event_incorrect_param_bucket))
        self.assertFalse(validate_parameters(event_incorrect_param_key)) 
        self.assertFalse(validate_parameters(event_incorrect_param_num))
        self.assertFalse(validate_parameters(event_multi_header_key))
        self.assertFalse(validate_parameters(event_multi_header_bucket))
        self.assertFalse(validate_parameters(event_missing_querystring))


if __name__ == '__main__':
    unittest.main()