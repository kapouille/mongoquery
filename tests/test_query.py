import re
from unittest import TestCase

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
    def setUp(self):
        self.maxDiff = None

    def _query(self, definition, collection=_ALL):
        return list(filter(
            Query(definition).match,
            collection
        ))

    def test_simple_lookup(self):
        self.assertEqual([_FRUIT], self._query({"type": "fruit"}))
        self.assertEqual([], self._query({"type": "ham"}))
        self.assertEqual(_ALL, self._query({"memos.memo": "on time"}))
        self.assertEqual([_FRUIT], self._query({"memos.by": "payment"}))
        self.assertEqual([_FOOD], self._query({"memos.1.memo": "approved"}))

    def test_comparison(self):
        self.assertEqual(
            [_FOOD],
            self._query({"qty": {"$eq": 25}})
        )

        self.assertEqual(
            [_FOOD],
            self._query({"qty": {"$gt": 20}})
        )

        self.assertEqual(
            _ALL,
            self._query({"qty": {"$gte": 10}})
        )

        self.assertEqual(
            _ALL,
            self._query({"ratings": {"$in": [5, 6]}})
        )

        self.assertEqual(
            [_FRUIT],
            self._query({"qty": {"$in": [10, 42]}})
        )

        self.assertEqual(
            [_FRUIT],
            self._query({"qty": {"$lt": 20}})
        )

        self.assertEqual(
            [_FRUIT],
            self._query({"qty": {"$lte": 10}})
        )

        self.assertEqual(
            [_FOOD],
            self._query({"qty": {"$ne": 10}})
        )

        self.assertEqual(
            [_FOOD],
            self._query({"qty": {"$nin": [10, 42]}})
        )

    def test_element(self):
        self.assertEqual(
            _ALL,
            self._query({"qty": {"$type": 16}})  # 32bit int
        )

        self.assertEqual(
            [],
            self._query({"qty": {"$type": 2}})  # string
        )

        self.assertEqual(
            _ALL,
            self._query({"qty": {"$type": 'int'}})
        )

        self.assertEqual(
            _ALL,
            self._query({"qty": {"$type": 'number'}})
        )

        self.assertEqual(
            _ALL,
            self._query({"item": {"$type": 'string'}})
        )

        self.assertEqual(
            [],
            self._query({"qty": {"$type": 'string'}})
        )

        self.assertEqual(
            _ALL,
            self._query({"qty": {"$exists": True}})
        )

        self.assertEqual(
            [],
            self._query({"foo": {"$exists": True}})
        )

        records = [
            {"a": 5, "b": 5, "c": None},
            {"a": 3, "b": None, "c": 8},
            {"a": None, "b": 3, "c": 9},
            {"a": 1, "b": 2, "c": 3},
            {"a": 2, "c": 5},
            {"a": 3, "b": 2},
            {"a": 4},
            {"b": 2, "c": 4},
            {"b": 2},
            {"c": 6}
        ]

        self.assertEqual(
            records[:-3],
            self._query(
                {"a": {"$exists": True}},
                collection=records)
        )

        self.assertEqual(
            [records[4], records[6], records[9]],
            self._query(
                {"b": {"$exists": False}},
                collection=records)
        )

        self.assertEqual(
            [records[5], records[6], records[8]],
            self._query(
                {"c": {"$exists": False}},
                collection=records)
        )


    def test_evaluation(self):
        self.assertEqual(
            [_FOOD],
            self._query({"qty": {"$mod": [4, 1]}})
        )

        self.assertEqual(
            [_FRUIT],
            self._query({"qty": {"$mod": [4, 2]}})
        )

        self.assertEqual(
            [],
            self._query({"qty": {"$mod": [4, 3]}})
        )

        products = [
            {"_id": 100, "sku": "abc123",
             "description": "Single line description."},
            {"_id": 101, "sku": "abc789",
             "description": "First line\nSecond line"},
            {"_id": 102, "sku": "xyz456",
             "description": "Many spaces before     line"},
            {"_id": 103, "sku": "xyz789",
             "description": "Multiple\nline description"}
        ]

        self.assertEqual(
            products[:2],
            self._query({"sku": {"$regex": "/^ABC/i"}}, collection=products)
        )
        self.assertEqual(
            products[:2],
            self._query({"sku": {"$regex": re.compile("^ABC", re.IGNORECASE)}},
                        collection=products)
        )

        self.assertEqual(
            products[:2],
            self._query({"sku": {"$regex": "^abc"}}, collection=products)
        )

        self.assertEqual(
            products[:2],
            self._query(
                {"description": {"$regex": "/^S/m"}}, collection=products)
        )

        self.assertEqual(
            products[:1],
            self._query(
                {"description": {"$regex": "/^S/"}}, collection=products)
        )

        self.assertEqual(
            products[:2],
            self._query(
                {"description": {"$regex": "/S/"}}, collection=products)
        )

        self.assertEqual(
            products[2:4],
            self._query(
                {"description": {"$regex": "/m.*line/si"}},
                collection=products)
        )

        self.assertEqual(
            products[2:3],
            self._query(
                {"description": {"$regex": "/m.*line/i"}}, collection=products)
        )

        regex = """
        abc #category code
        123 #item number
        """

        self.assertEqual(
            products[:1],
            self._query({
                "sku": {
                    "$regex": "/{}/x".format(regex)
                }
            }, collection=products)
        )

    def test_array(self):
        self.assertEqual(
            [_FOOD],
            self._query({
                "memos": {
                    "$elemMatch": {
                        "memo": 'on time',
                        "by": 'shipping'
                    }
                }
            })
        )

        self.assertEqual(
            [_FOOD],
            self._query({
                "ratings": [5, 8, 9]
            })
        )

        self.assertEqual(
            [_FOOD],
            self._query({
                "ratings": {
                    "$size": {
                        "$gt" : 2
                    }
                }
            })
        )

        self.assertEqual(
            [],
            self._query({
                "memos": {
                    "$elemMatch": {
                        "memo": 'on time',
                        "by": 'billing'
                    }
                }
            })
        )

        inventory = [
            {
                "_id": "5234cc89687ea597eabee675",
                "code": "xyz",
                "tags": ["school", "book", "bag", "headphone", "appliance"],
                "qty": [
                    {"size": "S", "num": 10, "color": "blue"},
                    {"size": "M", "num": 45, "color": "blue"},
                    {"size": "L", "num": 100, "color": "green"}
                ]
            },
            {
                "_id": "5234cc8a687ea597eabee676",
                "code": "abc",
                "tags": ["appliance", "school", "book"],
                "qty": [
                    {"size": "6", "num": 100, "color": "green"},
                    {"size": "6", "num": 50, "color": "blue"},
                    {"size": "8", "num": 100, "color": "brown"}
                ]
            },
            {
                "_id": "5234ccb7687ea597eabee677",
                "code": "efg",
                "tags": ["school", "book"],
                "qty": [
                    {"size": "S", "num": 10, "color": "blue"},
                    {"size": "M", "num": 100, "color": "blue"},
                    {"size": "L", "num": 100, "color": "green"}
                ]
            },
            {
                "_id": "52350353b2eff1353b349de9",
                "code": "ijk",
                "tags": ["electronics", "school"],
                "qty": [
                    {"size": "M", "num": 100, "color": "green"}
                ]
            }
        ]

        self.assertEqual(
            inventory[:2],
            self._query(
                {"tags": {"$all": ["appliance", "school", "book"]}},
                collection=inventory
            )
        )

        self.assertEqual(
            inventory[2:],
            self._query(
                {"qty": {"$all": [
                    {"$elemMatch": {"size": "M", "num": {"$gt": 50}}},
                    {"$elemMatch": {"num": 100, "color": "green"}}
                ]}},
                collection=inventory
            )
        )

        self.assertEqual(
            inventory[1:2],
            self._query(
                {"qty.num": {"$all": [50]}},
                collection=inventory
            )
        )

        self.assertEqual(
            inventory[3:],
            self._query(
                {"qty": {"$size": 1}},
                collection=inventory
            )
        )

        self.assertEqual(
            inventory[:3],
            self._query(
                {"qty": {"$size": 3}},
                collection=inventory
            )
        )

        self.assertEqual(
            [],
            self._query(
                {"qty": {"$size": 2}},
                collection=inventory
            )
        )

        self.assertEqual(
            [],
            self._query(
                {"code": {"$size": 3}},
                collection=inventory
            )
        )

    def test_integer_mapping_key_exists(self):
        collection = [{1: 'foo'}, {2: 'bar'}]
        self.assertEqual([], self._query({3: {"$exists": True}}, collection))
        self.assertEqual(
            collection[:1], self._query({1: {"$exists": True}}, collection))
        self.assertEqual(
            collection[1:], self._query({1: {"$exists": False}}, collection))

    def test_query_integer_keyed(self):
        collection = [{1: {"banana": 3}}]
        self.assertEqual([], self._query(
            {2: {"banana": {"$gt": 2}}}, collection))
        self.assertEqual(collection, self._query(
            {1: {"banana": {"$gt": 2}}}, collection))
        self.assertEqual([], self._query(
            {1: {"banana": {"$gt": 4}}}, collection))

    def test_query_subfield_not_found(self):
        collection = [
            {"turtle": True}
        ]

        self.assertEqual(
            [], self._query({"turtle": {"neck": True}}, collection)
        )

    def test_bad_query_doesnt_infinitely_recurse(self):
        collection = [{"turtles": "swim"}]
        self.assertEqual(
            [], self._query({"turtles": {"value": "swim"}}, collection))

    def test_query_string(self):
        collection = [{"a": "5"}, {"a": "567"}]
        self.assertEqual([], self._query({"a": 5}, collection))
        self.assertEqual([{"a": "5"}], self._query({"a": "5"}, collection))
