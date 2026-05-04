#!/usr/bin/env python
"""
Cleanup Script for Specula - Remove Old/Unavailable Threat Logs
Safely delete logs from the database and their associated screenshots
"""

import os
import sys
from app.web.db import LogStore

def print_header():
    print("\n" + "="*60)
    print("🧹 Specula Log Cleanup Utility")
    print("="*60 + "\n")

def print_menu():
    print("Choose an option:")
    print("1. Remove unavailable/missing screenshot logs")
    print("2. Remove logs older than X days")
    print("3. Delete specific log by ID")
    print("4. View log statistics")
    print("5. Clear ALL logs (⚠️ WARNING - Cannot undo!)")
    print("0. Exit")
    print()

def get_log_stats(logger):
    """Display statistics about current logs"""
    import sqlite3
    with sqlite3.connect(logger.db_path) as con:
        cur = con.execute("SELECT COUNT(*) FROM events")
        total_logs = cur.fetchone()[0]
        
        cur = con.execute("SELECT SUM(CAST((SELECT LENGTH(image_path)) AS INTEGER)) FROM events")
        result = cur.fetchone()
        # Get approximate size
        screenshot_dir = logger.screenshot_dir
        if os.path.exists(screenshot_dir):
            total_size = sum(os.path.getsize(os.path.join(screenshot_dir, f)) 
                           for f in os.listdir(screenshot_dir) if os.path.isfile(os.path.join(screenshot_dir, f)))
        else:
            total_size = 0
    
    print(f"\n📊 Log Statistics:")
    print(f"   Total logs: {total_logs}")
    print(f"   Screenshot directory: {screenshot_dir}")
    print(f"   Approximate storage: {total_size / (1024*1024):.2f} MB")
    print()
    return total_logs

def option_1_remove_unavailable(logger):
    """Remove logs with missing screenshots"""
    print("\n🔍 Scanning for unavailable screenshots...")
    deleted = logger.delete_unavailable_screenshots()
    print(f"✓ Removed {deleted} logs with unavailable screenshots\n")

def option_2_remove_old(logger):
    """Remove logs older than X days"""
    try:
        days = int(input("Enter number of days to keep (e.g., 7 for last 7 days): "))
        if days < 1:
            print("✗ Please enter a positive number\n")
            return
        
        print(f"\n🗑️  Removing logs older than {days} days...")
        deleted = logger.delete_old_events(days=days)
        print(f"✓ Removed {deleted} old logs\n")
    except ValueError:
        print("✗ Invalid input. Please enter a number.\n")

def option_3_delete_specific(logger):
    """Delete a specific log by ID"""
    try:
        event_id = int(input("Enter log ID to delete: "))
        # Check if exists
        import sqlite3
        with sqlite3.connect(logger.db_path) as con:
            cur = con.execute("SELECT id FROM events WHERE id = ?", (event_id,))
            if not cur.fetchone():
                print(f"✗ Log ID {event_id} not found\n")
                return
        
        confirm = input(f"⚠️  Are you sure? This will delete log {event_id} and its screenshot (y/n): ")
        if confirm.lower() == 'y':
            logger.delete_event(event_id)
            print("✓ Log deleted\n")
        else:
            print("✗ Cancelled\n")
    except ValueError:
        print("✗ Invalid input. Please enter a number.\n")

def option_5_clear_all(logger):
    """Clear all logs (with confirmation)"""
    confirm = input("⚠️  WARNING: This will DELETE ALL logs and screenshots! Type 'YES' to confirm: ")
    if confirm == "YES":
        double_confirm = input("Are you ABSOLUTELY sure? (Type 'DELETE ALL'): ")
        if double_confirm == "DELETE ALL":
            logger.clear_all_logs()
            print("✓ All logs cleared\n")
        else:
            print("✗ Cancelled\n")
    else:
        print("✗ Cancelled\n")

def main():
    print_header()
    
    # Initialize logger
    logger = LogStore()
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-5): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!\n")
            break
        elif choice == "1":
            option_1_remove_unavailable(logger)
        elif choice == "2":
            option_2_remove_old(logger)
        elif choice == "3":
            option_3_delete_specific(logger)
        elif choice == "4":
            get_log_stats(logger)
        elif choice == "5":
            option_5_clear_all(logger)
        else:
            print("✗ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Cleanup cancelled by user\n")
        sys.exit(0)
