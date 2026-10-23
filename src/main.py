
# src/main.py

from uuid import uuid4

from database import Neo4jDatabase


def main():
    db = Neo4jDatabase()

    # Unique IDs let you rerun the demonstration safely.
    run_id = uuid4().hex[:8]
    alice_id = f"alice-{run_id}"
    bob_id = f"bob-{run_id}"

    try:
        print("\nConnected successfully to Neo4j Aura!")

        # 1. Create nodes
        print("\n1. CREATE NODES")
        print(db.create_student(
            alice_id, "Alice", 21, "Pune"
        ))
        print(db.create_student(
            bob_id, "Bob", 22, "Mumbai"
        ))

        # 2. Create relationship
        print("\n2. CREATE RELATIONSHIP")
        print(db.create_relationship(alice_id, bob_id))

        # 3. Read nodes
        print("\n3. READ STUDENTS")
        print(db.read_students())

        # 4. Search/filter
        print("\n4. SEARCH STUDENTS BY CITY: Pune")
        print(db.search_students_by_city("Pune"))

        # 5. Update properties
        print("\n5. UPDATE ALICE")
        print(db.update_student(
            alice_id, age=23, city="Bengaluru"
        ))

        print("\nVERIFY UPDATED DATA")
        print(db.read_students())

        # 6. Delete relationship
        print("\n6. DELETE RELATIONSHIP")
        print(db.delete_relationship(alice_id, bob_id))

        # 7. Delete nodes
        print("\n7. DELETE DEMO NODES")
        print(db.delete_student(alice_id))
        print(db.delete_student(bob_id))

        print("\nCRUD DEMONSTRATION COMPLETED!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
