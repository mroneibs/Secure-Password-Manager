import sqlite3
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import threading

def get_app_data_path():
    """Get the appropriate AppData path for storing the database"""
    app_name = "SecurePasswordManager"
    if os.name == 'nt':  # Windows
        app_data = os.getenv('APPDATA')
        if not app_data:
            app_data = os.path.expanduser('~\\AppData\\Roaming')
        base_path = os.path.join(app_data, app_name)
    else:  # Linux/Mac
        base_path = os.path.expanduser(f'~/.{app_name.lower()}')
    
    # Create directory if it doesn't exist
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    return base_path

class EncryptionManager:
    def __init__(self, master_key):
        # Generate a key from the master password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt',  # In production, use a random salt
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher_suite = Fernet(key)

    def encrypt(self, data: str) -> bytes:
        return self.cipher_suite.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        return self.cipher_suite.decrypt(encrypted_data).decode()

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                # Set database path in AppData
                db_path = os.path.join(get_app_data_path(), "passwords.db")
                cls._instance.db_path = db_path
                cls._instance.connection = None
                cls._instance.init_database()
            return cls._instance

    def init_database(self):
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Initialize database with connection pooling
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")  # Use Write-Ahead Logging
        self.connection.execute("PRAGMA synchronous=NORMAL")  # Faster synchronization
        self.connection.execute("PRAGMA cache_size=-2000")  # 2MB cache
        
        with self.connection:
            cursor = self.connection.cursor()
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
            ''')
            # Create passwords table with indexes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password BLOB NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Create indexes for faster searching
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON passwords(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON passwords(title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON passwords(username)')
            
            # Insert default admin user if not exists
            admin_password = "admin123"
            hashed = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash)
                VALUES (?, ?)
            ''', ('admin', hashed.decode()))

    def __del__(self):
        if self.connection:
            self.connection.close()

    def get_connection(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.connection

    def verify_user(self, username: str, password: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result:
                stored_hash = result[0].encode()
                return bcrypt.checkpw(password.encode(), stored_hash)
        return False

    def add_password(self, name: str, title: str, username: str, encrypted_password: bytes, description: str = ""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passwords (name, title, username, encrypted_password, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, title, username, encrypted_password, description))

    def get_all_passwords(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, title, username, encrypted_password, description, created_at
                FROM passwords
                ORDER BY created_at DESC
            ''')
            return cursor.fetchall()

    def search_passwords(self, search_term: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f'%{search_term}%'
            cursor.execute('''
                SELECT id, name, title, username, encrypted_password, description, created_at
                FROM passwords
                WHERE name LIKE ? OR title LIKE ? OR username LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
            ''', (search_pattern, search_pattern, search_pattern, search_pattern))
            return cursor.fetchall()

    def delete_password(self, password_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))

    def update_password(self, password_id: int, name: str, title: str, username: str, 
                       encrypted_password: bytes, description: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE passwords 
                SET name = ?, title = ?, username = ?, encrypted_password = ?, 
                    description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, title, username, encrypted_password, description, password_id)) 