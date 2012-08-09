import unittest
from pyramid import testing

class CollectionTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_find_item(self):
        """
        Test that our find() wrapper method works
        """
        pass

    def test_find_one_item(self):
        """
        Test that our find_one() wrapper method works
        """
        pass

    def test_remove_item(self):
        """
        Test that our remove() wrapper method works
        """
        pass

    def test_save_item(self):
        """
        Test that our save() wrapper method works
        """
        pass

    def test_update_item(self):
        """
        Test that our update() wrapper method works
        """
        pass

    def test_insert_item(self):
        """
        Test that our insert() wrapper method works
        """
        pass
