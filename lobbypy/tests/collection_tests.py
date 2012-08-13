import unittest
from pyramid import testing

class CollectionTest(unittest.TestCase):
    def _makeOne(self, collection):
        from lobbypy.resources.collections import Collection
        class MockItem(dict):
            def __init__(self, adict):
                self.update(adict)
        class MockCollection(Collection):
            def _make_one(self, adict, name):
                return self._assign(MockItem(adict), name)
        coll = MockCollection(collection)
        coll.__name__ = 'test'
        return coll

    def setUp(self):
        from paste.deploy import appconfig
        import pymongo, os
        MongoDB = pymongo.Connection
        settings = appconfig('config:development.ini#lobbypy',
                relative_to=os.getcwd())
        db_uri = settings['mongodb.url']
        conn = MongoDB(db_uri)
        db_name = settings['mongodb.db_name']
        self.config = testing.setUp(settings={'mongodb_conn':conn,
            'mongodb.url':db_uri, 'db':conn[db_name]})

    def tearDown(self):
        self._getUnwrappedCollection().drop()
        testing.tearDown()

    def _getDb(self):
        from pyramid.threadlocal import get_current_registry
        return get_current_registry().settings['db']

    def _getUnwrappedCollection(self):
        return self._getDb()['test']

    def test_find_item(self):
        """
        Test that our find() wrapper method works
        """
        a = {'a':1, 'b':'b unit', 'c':[{'g':1},{'g':2},{'g':3}], 'd':'a'}
        b = {'a':0, 'b':'g unit', 'c':[], 'd':'a'}
        # use regular db to not poison test
        unwrapped_coll = self._getUnwrappedCollection()
        unwrapped_coll.insert(a)
        unwrapped_coll.insert(b)
        coll = self._makeOne(unwrapped_coll)
        # now use coll for finding
        # find both
        self.assertEquals(len(list(coll.find())), 2)
        # find b
        cur = list(coll.find({'a':0}))
        self.assertEquals(len(cur), 1)
        self.assertEquals(cur[0]['a'], 0)
        self.assertEquals(cur[0].__parent__, coll)
        # find complex a
        cur = list(coll.find({'c':{'$elemMatch': {'g':1}}}))
        self.assertEquals(len(cur), 1)
        self.assertTrue({'g':1} in cur[0]['c'])

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
