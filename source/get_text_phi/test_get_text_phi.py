import unittest
from lambda_function import validate_parameters
import sys

class TestRequestHeaders(unittest.TestCase):

    def test_validate_parameters(self):
        # One correct param
        event_correct_1 = {"body": "{\"text\": \"Mary Major was born on April 1 0, 1987\"}"}
        # One incorrect param
        event_incorrect_1param = {"body": "{\"phiDectionThreshold\": \"Mary Major was born on April 1 6, 1987\"}"}
        # Two correct params
        event_correct_2 = {"body": "{\"text\": \"Mary Major was born on April 1 2, 1987\", \"phiDetectionThreshold\":0.5}"}
        # Two correct params, incorrect threshold
        event_incorrect_threshold = {"body": "{\"text\": \"Mary Major was born on April 1 1, 1987\", \"phiDetectionThreshold\":1.5}"}
        # Two params, one correct
        event_incorrect_param2 = {"body": "{\"text\": \"Mary Major was born on April 1 3, 1987\", \"phectionThreshold\":0.5}"}
        # Body missing
        event_body_missing = {"bodysadfas": "{\"text\": \"Mary Major was born on April 1 4, 1987\", \"phiDetectionThreshold\":0.5}"}
        # Two params, same field
        event_duplicate_field = {"body": "{\"text\": \"Mary Major was born on April 1 3, 1987\", \"text\":0.5}"}
        
        self.assertTrue(validate_parameters(event_correct_1))
        self.assertFalse(validate_parameters(event_incorrect_1param))
        self.assertTrue(validate_parameters(event_correct_2)) 
        self.assertFalse(validate_parameters(event_incorrect_threshold))
        self.assertFalse(validate_parameters(event_incorrect_param2))
        self.assertFalse(validate_parameters(event_body_missing))
        self.assertFalse(validate_parameters(event_duplicate_field))


if __name__ == '__main__':
    unittest.main()