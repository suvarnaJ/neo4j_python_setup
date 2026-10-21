
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# Load .env from the project root, regardless of the working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def main():
    if not all([URI, USERNAME, PASSWORD]):
        raise RuntimeError(
            "Missing Neo4j settings. Check your local .env file."
        )

    try:
        with GraphDatabase.driver(
            URI, auth=(USERNAME, PASSWORD)
        ) as driver:
            # Verify authentication and connectivity.
            driver.verify_connectivity()
            print("SUCCESS: Connected to Neo4j Aura!")

            # Execute a read-only test query.
            records, summary, keys = driver.execute_query(
                "RETURN 1 AS result",
                database_=DATABASE,
            )

            print(f"Test query result: {records[0]['result']}")
            print("SUCCESS: Query executed successfully.")

    except Exception as exc:
        print(f"Neo4j connection failed: {type(exc).__name__}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
