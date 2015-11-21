import unittest
import mock
import mox
import navigate
import json

class NavigateTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_something(self):
        self.assertEquals(2, 2)

    # Source for MockResponse class:
    # http://stackoverflow.com/questions/15753390/python-mock-requests-and-the-response
    def foo(*args, **kwargs):
    	class MockResponse(object):
    		def __init__(self, code, text):
    			self.code = code
    			self.text = text
    			
        return MockResponse(200, json.dumps(
        	{'result': {'formatted_address': 'foobar'}}))

    @mock.patch('requests.get', side_effect=foo)
    def test_address_lookup(self, obj):
        add = navigate.address_lookup('22')
        self.assertEquals('foobar', add)
