from unittest2 import TestCase
from mongoquery import Query

_FOOD = {
    "_id": 100,
    "type": "food",
    "item": "xyz",
    "qty": 25,
    "price": 2.5,
    "ratings": [5, 8, 9],
    "memos": [
        {"memo": "on time", "by": "shipping"},
        {"memo": "approved", "by": "billing"}
    ]
}

_FRUIT = {
    "_id": 101,
    "type": "fruit",
    "item": "jkl",
    "qty": 10,
    "price": 4.25,
    "ratings": [5, 9],
    "memos": [
        {"memo": "on time", "by": "payment"},
        {"memo": "delayed", "by": "shipping"}]
}

_ALL = [_FOOD, _FRUIT]


class TestQuery(TestCase):

    def _query(self, definition):
        return filter(
            Query(definition).match,
            _ALL
        )

    def test_simple_lookup(self):
        self.assertEqual([_FRUIT], self._query({"type": "fruit"}))
        self.assertEqual(_ALL, self._query({"memos.memo": "on time"}))
        self.assertEqual([_FOOD], self._query({"memos.1.memo": "approved"}))
