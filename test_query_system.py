#!/usr/bin/env python3
"""
Tests for the query system.
"""

import os
import unittest
import tempfile
import json
import csv
from query_system import QuerySystem


class TestQuerySystem(unittest.TestCase):
    """Test cases for QuerySystem class."""
    
    def setUp(self):
        """Set up test database."""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.qs = QuerySystem(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.qs.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_create_table(self):
        """Test table creation."""
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "age": "INTEGER"
        }
        self.qs.create_table("test_table", columns)
        
        tables = self.qs.list_tables()
        self.assertIn("test_table", tables)
    
    def test_import_csv(self):
        """Test CSV import."""
        # Create temporary CSV file
        csv_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='')
        csv_writer = csv.DictWriter(csv_file, fieldnames=['name', 'age', 'city'])
        csv_writer.writeheader()
        csv_writer.writerow({'name': 'Alice', 'age': '25', 'city': 'Beijing'})
        csv_writer.writerow({'name': 'Bob', 'age': '30', 'city': 'Shanghai'})
        csv_file.close()
        
        try:
            self.qs.import_csv(csv_file.name, "people")
            results = self.qs.query_table("people")
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['name'], 'Alice')
            self.assertEqual(results[1]['name'], 'Bob')
        finally:
            os.unlink(csv_file.name)
    
    def test_import_json(self):
        """Test JSON import."""
        # Create temporary JSON file
        json_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        data = [
            {'id': '1', 'product': 'Laptop', 'price': '1000'},
            {'id': '2', 'product': 'Mouse', 'price': '20'}
        ]
        json.dump(data, json_file)
        json_file.close()
        
        try:
            self.qs.import_json(json_file.name, "products")
            results = self.qs.query_table("products")
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['product'], 'Laptop')
            self.assertEqual(results[1]['product'], 'Mouse')
        finally:
            os.unlink(json_file.name)
    
    def test_query(self):
        """Test basic query."""
        columns = {"id": "INTEGER", "name": "TEXT"}
        self.qs.create_table("test", columns)
        
        self.qs.cursor.execute("INSERT INTO test (id, name) VALUES (?, ?)", (1, "Test"))
        self.qs.conn.commit()
        
        results = self.qs.query("SELECT * FROM test WHERE id = ?", (1,))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Test')
    
    def test_search(self):
        """Test search functionality."""
        columns = {"id": "INTEGER", "name": "TEXT", "description": "TEXT"}
        self.qs.create_table("items", columns)
        
        self.qs.cursor.execute("INSERT INTO items VALUES (?, ?, ?)", (1, "Apple", "Red fruit"))
        self.qs.cursor.execute("INSERT INTO items VALUES (?, ?, ?)", (2, "Banana", "Yellow fruit"))
        self.qs.cursor.execute("INSERT INTO items VALUES (?, ?, ?)", (3, "Cherry", "Red fruit"))
        self.qs.conn.commit()
        
        results = self.qs.search("items", "description", "Red")
        self.assertEqual(len(results), 2)
    
    def test_list_tables(self):
        """Test listing tables."""
        self.qs.create_table("table1", {"id": "INTEGER"})
        self.qs.create_table("table2", {"id": "INTEGER"})
        
        tables = self.qs.list_tables()
        self.assertIn("table1", tables)
        self.assertIn("table2", tables)
    
    def test_get_table_schema(self):
        """Test getting table schema."""
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "age": "INTEGER"
        }
        self.qs.create_table("people", columns)
        
        schema = self.qs.get_table_schema("people")
        self.assertEqual(len(schema), 3)
        column_names = [col['name'] for col in schema]
        self.assertIn('id', column_names)
        self.assertIn('name', column_names)
        self.assertIn('age', column_names)


if __name__ == '__main__':
    unittest.main()
