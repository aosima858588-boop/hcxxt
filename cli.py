#!/usr/bin/env python3
"""
Command-line interface for the query system.
查询系统的命令行界面
"""

import argparse
import sys
import json
from query_system import QuerySystem


def main():
    parser = argparse.ArgumentParser(description='Simple Query System - 简单查询系统')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from file')
    import_parser.add_argument('file', help='Path to CSV or JSON file')
    import_parser.add_argument('table', help='Table name to import into')
    import_parser.add_argument('--db', default='data.db', help='Database file path')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query data from table')
    query_parser.add_argument('table', help='Table name to query')
    query_parser.add_argument('--limit', type=int, help='Limit number of results')
    query_parser.add_argument('--db', default='data.db', help='Database file path')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search data in table')
    search_parser.add_argument('table', help='Table name to search')
    search_parser.add_argument('column', help='Column to search in')
    search_parser.add_argument('value', help='Value to search for')
    search_parser.add_argument('--db', default='data.db', help='Database file path')
    
    # List tables command
    list_parser = subparsers.add_parser('list-tables', help='List all tables')
    list_parser.add_argument('--db', default='data.db', help='Database file path')
    
    # Show schema command
    schema_parser = subparsers.add_parser('schema', help='Show table schema')
    schema_parser.add_argument('table', help='Table name')
    schema_parser.add_argument('--db', default='data.db', help='Database file path')
    
    # Execute SQL command
    sql_parser = subparsers.add_parser('sql', help='Execute custom SQL query')
    sql_parser.add_argument('query', help='SQL query to execute')
    sql_parser.add_argument('--db', default='data.db', help='Database file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize query system
    qs = QuerySystem(args.db)
    
    try:
        if args.command == 'import':
            # Determine file type
            if args.file.endswith('.csv'):
                qs.import_csv(args.file, args.table)
            elif args.file.endswith('.json'):
                qs.import_json(args.file, args.table)
            else:
                print("Error: Only CSV and JSON files are supported.")
                sys.exit(1)
        
        elif args.command == 'query':
            results = qs.query_table(args.table, args.limit)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        
        elif args.command == 'search':
            results = qs.search(args.table, args.column, args.value)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        
        elif args.command == 'list-tables':
            tables = qs.list_tables()
            print("Tables in database:")
            for table in tables:
                print(f"  - {table}")
        
        elif args.command == 'schema':
            schema = qs.get_table_schema(args.table)
            print(f"Schema for table '{args.table}':")
            print(json.dumps(schema, indent=2, ensure_ascii=False))
        
        elif args.command == 'sql':
            results = qs.query(args.query)
            print(json.dumps(results, indent=2, ensure_ascii=False))
    
    finally:
        qs.close()


if __name__ == '__main__':
    main()
