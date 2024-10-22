#!/usr/bin/env python3
"""List all documents in a collection
"""


def list_all(mongo_collection):
    """
    List all documents in mongo_collection
    """
    return mongo_collection.find()
