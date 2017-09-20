==========
mongoquery
==========

.. image:: https://travis-ci.org/kapouille/mongoquery.svg?branch=master
    :target: https://travis-ci.org/kapouille/mongoquery

A utility library that provides a `MongoDB <http://www.mongodb.org>`_-like query
language for querying python collections. It's mainly intended to parse objects
structured as fundamental types in a similar fashion to what is produced by `JSON`
or `YAML` parsers. It follows the specification of queries for MongoDB version 3.4.


-----
Usage
-----

Example:

.. code-block:: python

    from mongoquery import Query, QueryError

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

    a_is_3 = Query({"a": 3})

    # match a single object
    matched = a_is_3.match(record[1])
    assert matched

    matched = a_is_3.match(record[0])
    assert not matched

    # filter elements
    filtered = filter(
        a_is_3.match,
        records
    )
    assert filtered == [records[1], records[5]]

    # incorrect filters raise QueryError
    try:
        matched = query({"$foo": 2}).match(record[1])
    except QueryError:
        pass  # => "$foo" operator isn't supported


------------
Query syntax
------------

The syntax of queries matches closely the one of
`MongoDB queries <http://docs.mongodb.org/manual/tutorial/query-documents/>`_,
and translates it to python using the following rules:

  - operators and field identifiers are expressed as strings. For instance,
    the following MongoDB query:

    .. code-block:: javascript

      {
          memos: {
              $elemMatch: {
                  memo: 'on time',
                  by: 'billing'
              }
          }
      }

    Translates straightforwardly to the following Python dict:

    .. code-block:: python

      {
          "memos": {
              "$elemMatch": {
                  "memo": 'on time',
                  "by": 'billing'
              }
          }
      }

  - regular expressions are expected to be expressed as string containing
    the MongoDB regular expression syntax. For instance:

    .. code-block:: javascript

      {description: {$regex: /^S/m}}

    Translates to the following Python dict:

    .. code-block:: python

      {"description": {"$regex": "/^S/m"}}

  - the boolean, null syntax used in MongoDB follows the JavaScript syntax.
    It is expected the python equivalents are used. For instance:

    .. code-block:: javascript

      {a: {$exists: true}, b: null}

    Translates to the following Python dict:

    .. code-block:: python

      {"a": {"$exists": True}, "b": None}


---------------------------------------------
Functional differences with MongoDB's queries
---------------------------------------------

There are a few features that are not supported by ``mongoquery``:
    - Only the ``"/pattern/<options>"`` syntax is supported for ``$regex``. As
      a consequence, ``$options`` isn't supported.
    - ``$text`` hasn't been implemented.
    - Due to the pure python nature of this library, ``$where`` isn't supported.
    - The `Geospatial` operators ``$geoIntersects``, ``$geoWithin``,
      ``$nearSphere``, and ``$near`` are not implemented.
    - Projection operators `$``, ``$elemMatch``, ``$meta``, and ``$slice`` are
      not implemented (only querying is implemented)
    - ``$type`` is limited to recognising generic python types, it won't look
      into recognising the format of the data (for instance, it doesn't check
      Object ID's format, only that they are strings)
