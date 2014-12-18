==========
mongoquery
==========

A utility library that provides a `MongoDB <http://www.mongodb.org>`_-like query
language for querying python collections. It's mainly intended to parse objects
structured as fundamental types in a similar fashion to what is produced by JSON
or YAML parsers.

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
