import unittest

from pyramid import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_root_view(self):
        from lobbypy.views import root_view
        request = testing.DummyRequest()
        info = root_view(request)
        self.assertEqual(info['project'], 'lobbypy')

