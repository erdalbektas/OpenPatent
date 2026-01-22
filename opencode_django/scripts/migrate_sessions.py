#!/usr/bin/env python3
"""
Migration script to import sessions from the existing TypeScript server.

This script reads session data from the TS server's JSON storage and imports
it into the new PostgreSQL-backed Django server.

Usage:
    python migrate_sessions.py --source /path/to/ts/sessions --users /path/to/users.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import Json


def parse_args():
    parser = argparse.ArgumentParser(description='Migrate sessions from TS server to Django')
    parser.add_argument('--source', required=True, help='Path to TS sessions directory')
    parser.add_argument('--users', required=True, help='Path to users JSON file')
    parser.add_argument('--host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--port', default=5432, type=int, help='PostgreSQL port')
    parser.add_argument('--db', default='openpatent', help='Database name')
    parser.add_argument('--user', default='openpatent', help='Database user')
    parser.add_argument('--password', default='openpatent', help='Database password')
    return parser.parse_args()


def get_connection(args):
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        database=args.db,
        user=args.user,
        password=args.password,
    )


def load_users(users_file):
    """Load user mapping from JSON file."""
    with open(users_file, 'r') as f:
        return json.load(f)


def load_sessions(sessions_dir):
    """Load all session files from directory."""
    sessions = []
    for filename in Path(sessions_dir).glob('*.json'):
        try:
            with open(filename, 'r') as f:
                session = json.load(f)
                sessions.append(session)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return sessions


def migrate_sessions(conn, sessions, user_mapping):
    """Import sessions into PostgreSQL."""
    cursor = conn.cursor()
    
    sessions_imported = 0
    messages_imported = 0
    
    for session_data in sessions:
        try:
            user_email = session_data.get('user_email')
            if user_email and user_email in user_mapping:
                user_id = user_mapping[user_email]
            else:
                print(f"Skipping session {session_data.get('id')}: user not found")
                continue
            
            cursor.execute("""
                INSERT INTO sessions_session 
                (id, user_id, title, is_shared, share_secret, version, 
                 time_created, time_updated, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, [
                session_data.get('id'),
                user_id,
                session_data.get('title', 'Imported Session'),
                session_data.get('is_shared', False),
                session_data.get('share_secret'),
                session_data.get('version', '0.0.1'),
                session_data.get('time', {}).get('created', 0),
                session_data.get('time', {}).get('updated', 0),
            ])
            
            if cursor.rowcount > 0:
                sessions_imported += 1
            
            messages = session_data.get('messages', [])
            for msg in messages:
                cursor.execute("""
                    INSERT INTO sessions_message 
                    (session_id, message_id, role, content, parts, tokens_input, 
                     tokens_output, tokens_reasoning, cost, provider_id, model_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    ON CONFLICT (session_id, message_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        parts = EXCLUDED.parts,
                        tokens_input = EXCLUDED.tokens_input,
                        tokens_output = EXCLUDED.tokens_output,
                        tokens_reasoning = EXCLUDED.tokens_reasoning,
                        cost = EXCLUDED.cost,
                        updated_at = NOW()
                """, [
                    session_data.get('id'),
                    msg.get('id'),
                    msg.get('role'),
                    Json(msg.get('content', [])),
                    Json(msg.get('parts', [])),
                    msg.get('tokens', {}).get('input', 0),
                    msg.get('tokens', {}).get('output', 0),
                    msg.get('tokens', {}).get('reasoning', 0),
                    msg.get('cost', 0),
                    msg.get('provider_id'),
                    msg.get('model_id'),
                ])
                
                if cursor.rowcount > 0:
                    messages_imported += 1
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Error importing session {session_data.get('id')}: {e}")
    
    cursor.close()
    return sessions_imported, messages_imported


def main():
    args = parse_args()
    
    print(f"Connecting to PostgreSQL at {args.host}:{args.port}...")
    conn = get_connection(args)
    
    print(f"Loading users from {args.users}...")
    user_mapping = load_users(args.users)
    print(f"Loaded {len(user_mapping)} users")
    
    print(f"Loading sessions from {args.source}...")
    sessions = load_sessions(args.source)
    print(f"Found {len(sessions)} sessions")
    
    print("Migrating sessions...")
    sessions_imported, messages_imported = migrate_sessions(conn, sessions, user_mapping)
    
    print(f"Migration complete!")
    print(f"  Sessions imported: {sessions_imported}")
    print(f"  Messages imported: {messages_imported}")
    
    conn.close()


if __name__ == '__main__':
    main()
