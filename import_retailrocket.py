import argparse
import os
import sys

import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(description="Import RetailRocket events into Neo4j.")
    parser.add_argument("-u", "--user", default="neo4j", help="Neo4j username")
    parser.add_argument("-p", "--password", default="neo4j", help="Neo4j password")
    parser.add_argument("-b", "--bolt", default="neo4j://127.0.0.1:7687", help="Neo4j URI")
    parser.add_argument("-s", "--source", default="data", help="Data folder")
    parser.add_argument("-f", "--file", default="events.csv", help="CSV file name")
    parser.add_argument("--batch-size", type=int, default=5000, help="Rows per batch")
    return parser.parse_args()


def create_constraints(session):
    session.run("CREATE CONSTRAINT visitor_id IF NOT EXISTS FOR (v:Visitor) REQUIRE v.visitorId IS UNIQUE")
    session.run("CREATE CONSTRAINT item_id IF NOT EXISTS FOR (i:Item) REQUIRE i.itemId IS UNIQUE")


def import_batch(tx, batch):
    cypher_query = """
    UNWIND $batch AS row
    MERGE (v:Visitor {visitorId: row.visitorid})
    MERGE (i:Item {itemId: row.itemid})

    WITH v, i, row
    CALL {
        WITH v, i, row
        WITH v, i, row WHERE row.event = 'view'
        CREATE (v)-[:VIEWED {timestamp: row.timestamp}]->(i)

        UNION ALL

        WITH v, i, row
        WITH v, i, row WHERE row.event = 'addtocart'
        CREATE (v)-[:ADDED_TO_CART {timestamp: row.timestamp}]->(i)

        UNION ALL

        WITH v, i, row
        WITH v, i, row WHERE row.event = 'transaction'
        CREATE (v)-[:BOUGHT {timestamp: row.timestamp, transactionId: row.transactionid}]->(i)
    }
    """
    tx.run(cypher_query, batch=batch)


def clean_transaction_id(value):
    return "" if pd.isna(value) else str(int(value))


def main():
    args = parse_arguments()
    csv_file_path = os.path.join(args.source, args.file)

    if not os.path.exists(csv_file_path):
        print(f"Error: file '{csv_file_path}' not found!")
        sys.exit(1)

    try:
        driver = GraphDatabase.driver(args.bolt, auth=(args.user, args.password))
        driver.verify_connectivity()
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        sys.exit(1)

    batch_size = args.batch_size
    with open(csv_file_path, encoding="utf-8") as f:
        total_rows = sum(1 for _ in f) - 1
    total_chunks = (total_rows // batch_size) + 1

    with driver.session() as session:
        create_constraints(session)
        chunks = pd.read_csv(csv_file_path, chunksize=batch_size)
        for chunk in tqdm(chunks, total=total_chunks, desc="Importing batches"):
            chunk["transactionid"] = chunk["transactionid"].apply(clean_transaction_id)
            session.execute_write(import_batch, chunk.to_dict(orient="records"))

    driver.close()
    print("Import finished.")


if __name__ == "__main__":
    main()
