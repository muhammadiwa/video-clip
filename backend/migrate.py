#!/usr/bin/env python
"""
Database Migration CLI - Laravel Artisan Style
Usage: python migrate.py <command>

Commands:
  migrate              - Run all pending migrations (php artisan migrate)
  migrate:fresh        - Drop all tables and re-run all migrations (php artisan migrate:fresh)
  migrate:rollback     - Rollback the last migration (php artisan migrate:rollback)
  migrate:status       - Show migration status (php artisan migrate:status)
  make:migration <name> - Create new migration file (php artisan make:migration)
  
Examples:
  python migrate.py migrate
  python migrate.py migrate:fresh
  python migrate.py make:migration add_users_table
"""

import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def run_alembic(args):
    """Run alembic command"""
    from alembic.config import main as alembic_main
    original_argv = sys.argv
    sys.argv = ['alembic'] + args
    try:
        alembic_main(args)
    finally:
        sys.argv = original_argv

def cmd_migrate():
    """Run all pending migrations"""
    print_header("Running Migrations")
    run_alembic(['upgrade', 'head'])
    print("\n[OK] Migrations completed!")

def cmd_migrate_fresh():
    """Drop all tables and re-run migrations"""
    print_header("Fresh Migration (Drop & Recreate)")
    print("WARNING: This will drop all tables and data!")
    response = input("Are you sure? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Cancelled.")
        return
    
    print("\n[1/2] Rolling back all migrations...")
    run_alembic(['downgrade', 'base'])
    
    print("\n[2/2] Running all migrations...")
    run_alembic(['upgrade', 'head'])
    print("\n[OK] Fresh migration completed!")

def cmd_migrate_rollback():
    """Rollback the last migration"""
    print_header("Rolling Back Last Migration")
    run_alembic(['downgrade', '-1'])
    print("\n[OK] Rollback completed!")

def cmd_migrate_status():
    """Show migration status"""
    print_header("Migration Status")
    run_alembic(['current'])
    print("\nHistory:")
    run_alembic(['history'])

def cmd_make_migration(name):
    """Create new migration file"""
    print_header(f"Creating Migration: {name}")
    run_alembic(['revision', '--autogenerate', '-m', name])
    print(f"\n[OK] Migration file created!")

def show_help():
    """Show help message"""
    print(__doc__)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    commands = {
        'migrate': cmd_migrate,
        'migrate:fresh': cmd_migrate_fresh,
        'migrate:rollback': cmd_migrate_rollback,
        'migrate:status': cmd_migrate_status,
        'help': show_help,
        '--help': show_help,
        '-h': show_help,
    }
    
    if command == 'make:migration':
        if len(sys.argv) < 3:
            print("Error: Migration name required")
            print("Usage: python migrate.py make:migration <name>")
            return
        cmd_make_migration(sys.argv[2])
    elif command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
