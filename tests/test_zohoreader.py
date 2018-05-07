from unittest import TestCase

from zohoreader import ZohoReader

class Testwreader(TestCase):
    def setUp(self):
        self.authtoken = 'inital_token'
        self.portalid = 3
        self.zr = ZohoReader(self.authtoken, self.portalid)



if __name__ == '__main__':
    unittest.main()
