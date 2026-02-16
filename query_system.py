#!/usr/bin/env python3
"""
Simple Query System - 简单查询系统

This module provides a simple data import and query system using SQLite.
可以导入数据并进行查询的简单系统
"""

import sqlite3
import csv
import json
import os
from typing import List, Dict, Any, Optional


class QuerySystem:
    """Simple query system for data import and retrieval."""
    
    def __init__(self, db_path: str = "data.db"):
        """
        Initialize the query system.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_table(self, table_name: str, columns: Dict[str, str]):
        """
        Create a new table in the database.
        
        Args:
            table_name: Name of the table to create
            columns: Dictionary of column names and their SQL types
                    e.g., {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
        """
        columns_def = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        self.cursor.execute(sql)
        self.conn.commit()
        print(f"Table '{table_name}' created successfully.")
    
    def import_csv(self, csv_path: str, table_name: str, create_if_not_exists: bool = True):
        """
        Import data from CSV file.
        
        Args:
            csv_path: Path to CSV file
            table_name: Target table name
            create_if_not_exists: If True, create table automatically based on CSV headers
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                print("No data to import.")
                return
            
            # Create table if needed
            if create_if_not_exists:
                columns = {col: "TEXT" for col in rows[0].keys()}
                self.create_table(table_name, columns)
            
            # Insert data
            column_names = list(rows[0].keys())
            placeholders = ", ".join(["?" for _ in column_names])
            columns_str = ", ".join(column_names)
            
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            for row in rows:
                values = [row[col] for col in column_names]
                self.cursor.execute(sql, values)
            
            self.conn.commit()
            print(f"Imported {len(rows)} rows into '{table_name}' from {csv_path}")
    
    def import_json(self, json_path: str, table_name: str, create_if_not_exists: bool = True):
        """
        Import data from JSON file.
        
        Args:
            json_path: Path to JSON file (should contain array of objects)
            table_name: Target table name
            create_if_not_exists: If True, create table automatically based on JSON keys
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list) or not data:
            print("JSON file should contain a non-empty array of objects.")
            return
        
        # Create table if needed
        if create_if_not_exists:
            columns = {col: "TEXT" for col in data[0].keys()}
            self.create_table(table_name, columns)
        
        # Insert data
        column_names = list(data[0].keys())
        placeholders = ", ".join(["?" for _ in column_names])
        columns_str = ", ".join(column_names)
        
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        for row in data:
            values = [str(row.get(col, '')) for col in column_names]
            self.cursor.execute(sql, values)
        
        self.conn.commit()
        print(f"Imported {len(data)} rows into '{table_name}' from {json_path}")
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.
        
        Args:
            sql: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            List of dictionaries representing query results
        """
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def query_table(self, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query all data from a table.
        
        Args:
            table_name: Name of the table to query
            limit: Maximum number of rows to return
            
        Returns:
            List of dictionaries representing query results
        """
        sql = f"SELECT * FROM {table_name}"
        if limit:
            sql += f" LIMIT {limit}"
        return self.query(sql)
    
    def search(self, table_name: str, column: str, value: str) -> List[Dict[str, Any]]:
        """
        Search for records where column matches value.
        
        Args:
            table_name: Name of the table to search
            column: Column name to search in
            value: Value to search for
            
        Returns:
            List of matching records
        """
        sql = f"SELECT * FROM {table_name} WHERE {column} LIKE ?"
        return self.query(sql, (f"%{value}%",))
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [dict(row) for row in self.cursor.fetchall()]
