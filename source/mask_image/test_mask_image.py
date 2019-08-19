import unittest
from lambda_function import validate_parameters
import sys

class TestRequestHeaders(unittest.TestCase):

    def test_validate_parameters(self):
        # Four correct params, five correct params
        event_correct_4 = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\"}'}
        event_correct_5_str = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\", \"phiDetectionThreshold\": \"0.1\"}'}
        event_correct_5_int = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\", \"phiDetectionThreshold\": 0}'}
        event_correct_5_float = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\", \"phiDetectionThreshold\": 0.1}'}
        self.assertTrue(validate_parameters(event_correct_4))
        self.assertTrue(validate_parameters(event_correct_5_str))
        self.assertTrue(validate_parameters(event_correct_5_int))
        self.assertTrue(validate_parameters(event_correct_5_float))
        
        # Correct param keys but wrong values
        event_multi_bucket = {'body': '{\"s3Bucket\": [\"mybucket\", \"mybucket2\"], \"s3Key\": \"mykey\"}'}
        event_multi_key = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": [\"mykey\",\"mykey2\"]}'}
        event_multi_destbucket = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": [\"myBucket\",\"mybucket2\"], \"destinationKey\": \"newKey\"}'}
        event_multi_destkey = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": [\"newKey\",\"newKey2\"]}'}
        event_incorrect_threshold_str = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\", \"phiDetectionThreshold\": \"f\"}'}
        event_incorrect_threshold_multi = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\", \"phiDetectionThreshold\": [0.1,0.2]}'}
        event_incorrect_threshold_oob = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\", \"phiDetectionThreshold\": 2}'}
        self.assertFalse(validate_parameters(event_multi_bucket))
        self.assertFalse(validate_parameters(event_multi_key)) 
        self.assertFalse(validate_parameters(event_multi_destbucket))
        self.assertFalse(validate_parameters(event_multi_destkey))
        self.assertFalse(validate_parameters(event_incorrect_threshold_str))
        self.assertFalse(validate_parameters(event_incorrect_threshold_multi))
        self.assertFalse(validate_parameters(event_incorrect_threshold_oob))

        # incorrect param (bucket, key, num)
        event_incorrect_param_bucket = {'body': '{\"s3Bucketa\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\"}'}
        event_incorrect_param_key = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Keya\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\"}'}
        event_incorrect_param_destbucket = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucketa\": \"myBucket\", \"destinationKey\": \"newKey\"}'}
        event_incorrect_param_destkey = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"myBucket\", \"destinationKeya\": \"newKey\"}'}
        event_incorrect_param_num = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"phiDetectionThreshold\": \"0.1\", \"destinationBucket\": \"myBucket\", \"destinationKey\": \"newKey\", \"asdf\": \"1234\"}'}
        self.assertFalse(validate_parameters(event_incorrect_param_bucket))
        self.assertFalse(validate_parameters(event_incorrect_param_key))
        self.assertFalse(validate_parameters(event_incorrect_param_destbucket))
        self.assertFalse(validate_parameters(event_incorrect_param_destkey))
        self.assertFalse(validate_parameters(event_incorrect_param_num))
        
        # bucket and key can\"t be equal (must be new, not overwrite)
        event_equal_bucket_key = {'body': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\", \"destinationBucket\": \"mybucket\", \"destinationKey\": \"mykey\"}'}
        self.assertFalse(validate_parameters(event_equal_bucket_key))

        # queryStringParameters missing
        event_missing_body = {'bodyasdf': '{\"s3Bucket\": \"mybucket\", \"s3Key\": \"mykey\"}'}
        self.assertFalse(validate_parameters(event_missing_body))

if __name__ == '__main__':
    unittest.main()