#!/usr/bin/env python3

# Simple script to copy collection from one collection to another

from pymongo import MongoClient
import random
import uuid

def main():
        
    # Open a connection to the mongo database, read the blog collection and copy the results to the photo collection
    client_a = MongoClient('localhost', 27017)
    db_a = client_a.visualintrigue

    client_b = MongoClient('localhost', 27017)
    db_b = client_b.visualintrigue

    for blog in db_a.blog.find():
        db_b.photos.insert(blog)

if __name__ == '__main__':
    main()

