
# src/learning_platform.py

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


class LearningPlatformGraph:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")

        if not all([uri, username, password]):
            raise ValueError("Set Neo4j credentials in the project-root .env")

        self.driver = GraphDatabase.driver(
            uri, auth=(username, password)
        )
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def run(self, query, **params):
        records, summary, _ = self.driver.execute_query(
            query,
            parameters_=params,
            database_=self.database,
        )
        return [record.data() for record in records]

    def seed_graph(self):
        # 4 nodes per label = 24 nodes total.
        node_groups = [
            ("Student", [
                {"id": "S1", "name": "Aarav", "city": "Pune"},
                {"id": "S2", "name": "Diya", "city": "Mumbai"},
                {"id": "S3", "name": "Kabir", "city": "Delhi"},
                {"id": "S4", "name": "Meera", "city": "Bengaluru"},
            ]),
            ("Course", [
                {"id": "C1", "title": "Python Programming", "level": "Beginner"},
                {"id": "C2", "title": "Data Science", "level": "Intermediate"},
                {"id": "C3", "title": "Graph Databases", "level": "Intermediate"},
                {"id": "C4", "title": "Machine Learning", "level": "Advanced"},
            ]),
            ("Mentor", [
                {"id": "M1", "name": "Neha", "expertise": "Python"},
                {"id": "M2", "name": "Rahul", "expertise": "Data Science"},
                {"id": "M3", "name": "Ananya", "expertise": "Graph Databases"},
                {"id": "M4", "name": "Vikram", "expertise": "Machine Learning"},
            ]),
            ("Skill", [
                {"id": "SK1", "name": "Python"},
                {"id": "SK2", "name": "SQL"},
                {"id": "SK3", "name": "Data Analysis"},
                {"id": "SK4", "name": "Neo4j"},
            ]),
            ("Project", [
                {"id": "P1", "title": "Sales Dashboard", "status": "Completed"},
                {"id": "P2", "title": "Fraud Detection", "status": "In Progress"},
                {"id": "P3", "title": "Course Recommender", "status": "Completed"},
                {"id": "P4", "title": "Skill Matcher", "status": "In Progress"},
            ]),
            ("Company", [
                {"id": "CO1", "name": "TechNova", "industry": "Technology"},
                {"id": "CO2", "name": "DataWorks", "industry": "Analytics"},
                {"id": "CO3", "name": "GraphLabs", "industry": "Software"},
                {"id": "CO4", "name": "AI Ventures", "industry": "Artificial Intelligence"},
            ]),
        ]

        # Labels are fixed in the source code; property values are parameters.
        for label, items in node_groups:
            query = f"""
            UNWIND $items AS item
            MERGE (n:{label} {{id: item.id}})
            SET n += item
            RETURN count(n) AS processed
            """
            self.run(query, items=items)

        # 32 relationships, created idempotently with MERGE.
        relationship_groups = [
            (
                "Student", "S", "Course", "C", "ENROLLED_IN",
                [("S1", "C1"), ("S1", "C3"), ("S2", "C2"),
                 ("S2", "C4"), ("S3", "C3"), ("S4", "C1")]
            ),
            (
                "Mentor", "M", "Course", "C", "TEACHES",
                [("M1", "C1"), ("M2", "C2"),
                 ("M3", "C3"), ("M4", "C4")]
            ),
            (
                "Course", "C", "Skill", "SK", "TEACHES_SKILL",
                [("C1", "SK1"), ("C1", "SK2"), ("C2", "SK2"),
                 ("C2", "SK3"), ("C3", "SK4"), ("C4", "SK3")]
            ),
            (
                "Student", "S", "Project", "P", "BUILT",
                [("S1", "P1"), ("S2", "P2"),
                 ("S3", "P3"), ("S4", "P4")]
            ),
            (
                "Project", "P", "Skill", "SK", "USES",
                [("P1", "SK1"), ("P1", "SK2"), ("P2", "SK1"),
                 ("P2", "SK3"), ("P3", "SK4"), ("P4", "SK3")]
            ),
            (
                "Student", "S", "Company", "CO", "INTERESTED_IN",
                [("S1", "CO1"), ("S1", "CO3"), ("S2", "CO2"),
                 ("S2", "CO4"), ("S3", "CO3"), ("S4", "CO1")]
            ),
        ]

        for left_label, left_prefix, right_label, right_prefix, rel, pairs in relationship_groups:
            query = f"""
            UNWIND $pairs AS pair
            MATCH (a:{left_label} {{id: pair[0]}})
            MATCH (b:{right_label} {{id: pair[1]}})
            MERGE (a)-[:{rel}]->(b)
            RETURN count(*) AS processed
            """
            self.run(query, pairs=[list(pair) for pair in pairs])

        print("Seed complete: 24 nodes and 32 relationships requested.")

    # READ: count nodes by label and all relationships.
    def graph_summary(self):
        return self.run("""
        MATCH (n)
        WITH labels(n) AS labels, count(*) AS total
        RETURN labels, total
        ORDER BY labels
        """)

    def relationship_summary(self):
        return self.run("""
        MATCH ()-[r]->()
        RETURN type(r) AS relationship, count(r) AS total
        ORDER BY relationship
        """)

    # READ: inspect connected learning journeys.
    def learning_journeys(self):
        return self.run("""
        MATCH (s:Student)-[:ENROLLED_IN]->(c:Course)
              -[:TEACHES_SKILL]->(sk:Skill)
        RETURN s.name AS student, c.title AS course,
               sk.name AS skill
        ORDER BY student, course, skill
        """)

    # CREATE: create a student using parameters.
    def create_student(self, student_id, name, city):
        return self.run("""
        CREATE (s:Student {id: $id, name: $name, city: $city})
        RETURN s
        """, id=student_id, name=name, city=city)

    # CREATE: link a student to a course.
    def enroll_student(self, student_id, course_id):
        return self.run("""
        MATCH (s:Student {id: $student_id})
        MATCH (c:Course {id: $course_id})
        CREATE (s)-[r:ENROLLED_IN]->(c)
        RETURN s.name AS student, c.title AS course, type(r) AS relationship
        """, student_id=student_id, course_id=course_id)

    # READ: find students by city.
    def search_students(self, city):
        return self.run("""
        MATCH (s:Student)
        WHERE toLower(s.city) = toLower($city)
        RETURN s.id AS id, s.name AS name, s.city AS city
        ORDER BY s.name
        """, city=city)

    # UPDATE: change a student's city.
    def update_student_city(self, student_id, city):
        return self.run("""
        MATCH (s:Student {id: $student_id})
        SET s.city = $city
        RETURN s.id AS id, s.name AS name, s.city AS city
        """, student_id=student_id, city=city)

    # DELETE: remove one specific relationship.
    def delete_enrollment(self, student_id, course_id):
        return self.run("""
        MATCH (s:Student {id: $student_id})
              -[r:ENROLLED_IN]->
              (c:Course {id: $course_id})
        WITH collect(r) AS relationships
        FOREACH (r IN relationships | DELETE r)
        RETURN size(relationships) AS deleted_relationships
        """, student_id=student_id, course_id=course_id)

    # DELETE: remove a node and any relationships attached to it.
    def delete_student(self, student_id):
        return self.run("""
        MATCH (s:Student {id: $student_id})
        WITH collect(s) AS students
        FOREACH (s IN students | DETACH DELETE s)
        RETURN size(students) AS deleted_nodes
        """, student_id=student_id)


def main():
    graph = LearningPlatformGraph()

    try:
        print("\n=== 1. CREATE GRAPH ===")
        graph.seed_graph()

        print("\n=== 2. READ NODE COUNTS ===")
        print(graph.graph_summary())

        print("\n=== 3. READ RELATIONSHIP COUNTS ===")
        print(graph.relationship_summary())

        print("\n=== 4. READ LEARNING JOURNEYS ===")
        print(graph.learning_journeys()[:10])

        # Use a temporary student to demonstrate CRUD without
        # altering the four seeded students.
        demo_id = "S-DEMO-CRUD"

        print("\n=== 5. CREATE NODE ===")
        print(graph.create_student(demo_id, "Demo Student", "Pune"))

        print("\n=== 6. CREATE RELATIONSHIP ===")
        print(graph.enroll_student(demo_id, "C1"))

        print("\n=== 7. SEARCH / FILTER ===")
        print(graph.search_students("Pune"))

        print("\n=== 8. UPDATE PROPERTY ===")
        print(graph.update_student_city(demo_id, "Hyderabad"))

        print("\n=== 9. DELETE RELATIONSHIP ===")
        print(graph.delete_enrollment(demo_id, "C1"))

        print("\n=== 10. DELETE NODE ===")
        print(graph.delete_student(demo_id))

        print("\n=== 11. FINAL GRAPH COUNTS ===")
        print(graph.graph_summary())
        print(graph.relationship_summary())

        print("\nAll demonstration operations completed.")

    finally:
        graph.close()


if __name__ == "__main__":
    main()
