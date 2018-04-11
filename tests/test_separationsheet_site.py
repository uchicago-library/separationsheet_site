import unittest
from unittest.mock import patch

from separationsheet_site import app


class Tests(unittest.TestCase):
    def setUp(self):
        # Perform any setup that should occur
        # before every test
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        self.app = app.test_client()

    def tearDown(self):
        # Perform any tear down that should
        # occur after every test
        pass

    def testGetRootPage(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testGetListPage(self):
        response = self.app.get("/list", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testGetBotPage(self):
        response = self.app.get("/both", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testGetRemovalPage(self):
        response = self.app.get("/removal", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testGetBarcodePage(self):
        response = self.app.get("/barcode/foo", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testPostRemovalForm(self):
        response = self.app.post('/removal', data=dict(acc_no="2000-000", batch_name="test", identifier="testing", media_type="CD", restriction="R-X", note="a note about a test accession"), content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
