#!/usr/bin/env python3
"""Insert a document in a collection
"""


def insert_school(mongo_collection, **kwargs):
    """insert a document in mongo_collection
    Arg:
      mongo_collection: the collection to insert the document into
      kwargs: the key word arguments to insert into the collection
    """
    document = mongo_collection.insert_one(kwargs)
    return document.inserted_id
