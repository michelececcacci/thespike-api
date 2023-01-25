import unittest
from thespikeapi import thespikeapi

class TestString(unittest.TestCase):
    def test_newline_removal(self):
        test_str = thespikeapi.RequestString("test\n")
        self.assertTrue(test_str.remove_newlines().string == "test")
        

    def test_tab_removal(self):
        test_str = thespikeapi.RequestString("te\tst")
        self.assertTrue(test_str.remove_tabs().string == "test")
        
class TestSoup(unittest.TestCase):
     def test_garbage_value(self):
         self.assertTrue(thespikeapi.get_soup("flsjflajfjalfaj") is None)

     def test_reasonable_value(self):
        self.assertTrue(thespikeapi.get_soup(thespikeapi.MATCHES) is not None)

if __name__ == "main":
    unittest.main()
