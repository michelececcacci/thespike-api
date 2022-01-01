import unittest
from vlrggapi import vlrggapi

class TestString(unittest.TestCase):
    def test_newline_removal(self):
        test_str = vlrggapi.RequestString("test\n")
        self.assertTrue(test_str.remove_newlines().string == "test")
        

    def test_tab_removal(self):
        test_str = vlrggapi.RequestString("te\tst")
        self.assertTrue(test_str.remove_tabs().string == "test")
        
class TestSoup(unittest.TestCase):
     def test_garbage_value(self):
         self.assertTrue(vlrggapi.get_soup("flsjflajfjalfaj") is None)

     def test_reasonable_value(self):
        self.assertTrue(vlrggapi.get_soup(vlrggapi.MATCHES) is not None)

if __name__ == "main":
    unittest.main()
