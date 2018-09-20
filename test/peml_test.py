import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import peml

class PemlFiles(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_that_it_has_a_version_number(self):
        pass
        
    def test_it_does_something_useful(self):
        peml.loads('')
    
    def test_reading_from_file(self):
        with open('test/palindrome.peml', 'r') as palindrome_file:
            data = peml.load(palindrome_file)
        self.assertTrue(data)

if __name__ == '__main__':
    unittest.main(buffer=False)
