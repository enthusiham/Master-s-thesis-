from time import time
import json
import ast
from pymongo import MongoClient

DATADIR = ""
DATAFILE = "dblp_v11.txt"


def parse_file(datafile, num_lines=5):
    data_ls = []  # List to store entry dictionaries
    with open(datafile, "r", encoding='utf-8') as file:
        counter = 0
        while counter < num_lines:
            line = file.readline()
            # Convert line into json in 3 steps:
            # 1. json dumps converts to string,
            # 2. literal_eval takes string literal,
            # 3. json.loads converts to json
            line = json.loads(ast.literal_eval(json.dumps(line)))
            # and add to data_ls
            data_ls.append(line)
            counter += 1
    return data_ls


def make_abstract(indexed_abstract):
    abs_length = indexed_abstract["IndexLength"]
    abstract_ls = ["" for _ in range(abs_length)]
    ind_abs = indexed_abstract["InvertedIndex"]
    ind_abs_keys = list(ind_abs.keys())
    ind_abs_vals = list(ind_abs.values())
    for token, pos_ls in zip(ind_abs_keys, ind_abs_vals):
        for pos in pos_ls:
            abstract_ls[pos] = token
    abstract = " ".join(abstract_ls)
    return abstract


if __name__ == "__main__":
    # md "\data\db"

    # LAUNCH SERVER:
    # mongod --dbpath="c:\data\db"

    # mongoimport c:\data\books.json -d bookdb -c books --drop

    # ADD FILE TO MONGODB:
    # mongoimport dblp_v11.json -d paperdb -c papers --drop

    client = MongoClient("localhost", 27017)

    print(client.list_database_names())

    # db = client.paperdb
    # collection = db.papers
    # filter_id = {"_id": {"$exists": 1}}
    # print(db.papers.count_documents(filter_id))

    # TODO: rather than mongoimport, load json line by line and put try catch around it

    db = client.paperdb
    papers = db.papers
    print(client.list_database_names())

    t0 = time()
    print("started at:", t0)

    with open(DATAFILE, "r", encoding='utf-8') as f:
        # counter = 0
        for line in f:
            """if counter > 5:
                break"""
            data = json.loads(ast.literal_eval(json.dumps(line)))
            if "indexed_abstract" in list(data.keys()):
                abstract = make_abstract(data["indexed_abstract"])
                data["abstract"] = abstract
                data.pop("indexed_abstract")
            # print(type(data))
            # print(data)
            try:
                # Try inserting one line of data
                db.papers.insert_one(data)
            except TypeError as e:
                print(e)
                # Create and write data line to text file
                with open("bad_lines.txt", "a", encoding="utf-8") as error_file:
                    error_file.write(str(data))
            # counter += 1

    t1 = time()
    print("done in %0.3fs" % (t1 - t0))

    """

    filter_id = {"_id": {"$exists": 1}}
    print(db.papers.count_documents(filter_id))

    for i in papers.find():
        print(i)

    """

    """db = client.bookdb
    collection = db.books
    for i in collection.find({"_id": 1}):
        print(i)"""
