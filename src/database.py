#This module handles connecting to Aura and implements node creation, 
# relationship creation, reading, filtering, updating, and deletion.

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load configuration from the project-root .env file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Neo4jDatabase:
    """Reusable CRUD operations for a Neo4j Student graph."""

    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")

        if not all([uri, username, password]):
            raise ValueError("Configure NEO4J_URI, NEO4J_USERNAME "
                             "and NEO4J_PASSWORD in .env")

        self.driver = GraphDatabase.driver(
            uri, auth=(username, password)
        )
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def _run(self, query, **parameters):
        """Execute a parameterized Cypher query."""
        records, _, _ = self.driver.execute_query(
            query,
            parameters_=parameters,
            database_=self.database,
        )
        return [record.data() for record in records]

    # 1. CREATE NODE
    def create_student(self, student_id, name, age, city):
        query = """
        CREATE (s:Student {
            student_id: $student_id,
            name: $name,
            age: $age,
            city: $city
        })
        RETURN s
        """
        return self._run(
            query,
            student_id=student_id,
            name=name,
            age=age,
            city=city,
        )

    # 2. CREATE RELATIONSHIP
    def create_relationship(self, from_id, to_id):
        query = """
        MATCH (a:Student {student_id: $from_id})
        MATCH (b:Student {student_id: $to_id})
        CREATE (a)-[r:KNOWS]->(b)
        RETURN a.name AS from_student,
               type(r) AS relationship,
               b.name AS to_student
        """
        return self._run(query, from_id=from_id, to_id=to_id)

    # 3. READ NODES
    def read_students(self):
        query = """
        MATCH (s:Student)
        RETURN s.student_id AS student_id,
               s.name AS name,
               s.age AS age,
               s.city AS city
        ORDER BY s.name
        """
        return self._run(query)

    # 4. SEARCH / FILTER
    def search_students_by_city(self, city):
        query = """
        MATCH (s:Student)
        WHERE toLower(s.city) = toLower($city)
        RETURN s.student_id AS student_id,
               s.name AS name,
               s.age AS age,
               s.city AS city
        ORDER BY s.name
        """
        return self._run(query, city=city)

    # 5. UPDATE PROPERTIES
    def update_student(self, student_id, age=None, city=None):
        updates = {}
        if age is not None:
            updates["age"] = age
        if city is not None:
            updates["city"] = city

        if not updates:
            raise ValueError("Provide at least one property to update")

        query = """
        MATCH (s:Student {student_id: $student_id})
        SET s += $updates
        RETURN s
        """
        return self._run(
            query, student_id=student_id, updates=updates
        )

    # 6. DELETE RELATIONSHIP
    def delete_relationship(self, from_id, to_id):
        query = """
        MATCH (a:Student {student_id: $from_id})
              -[r:KNOWS]->
              (b:Student {student_id: $to_id})
        DELETE r
        RETURN count(r) AS deleted_relationships
        """
        return self._run(query, from_id=from_id, to_id=to_id)

    # 7. DELETE NODE
    def delete_student(self, student_id):
        # DETACH DELETE also removes any remaining relationships.
        query = """
        MATCH (s:Student {student_id: $student_id})
        DETACH DELETE s
        RETURN count(s) AS deleted_nodes
        """
        # With DELETE, the node no longer exists to return.
        # Use the follow-up count to report the operation.
        self._run(query, student_id=student_id)
        return {"deleted_student_id": student_id}
