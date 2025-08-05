import os
import sqlite3
import json
from typing import Union, List, Dict, Any
from pydantic import BaseModel
from repo.repository_exceptions import UidNotUnique, UidNotFound, NoConfigurationChosen
from src.metaclasses.singleton import Singleton


class SQLiteRepo(metaclass=Singleton):
    def __init__(self, db_name):
        super().__init__()
        self._configuration_path = ''
        self.databaseName = db_name
        self.db_path: Union[str, None] = None
        self.table_name = db_name
        self.db = None  # For compatibility with existing code

    @property
    def configuration_path(self):
        return self._configuration_path

    @configuration_path.setter
    def configuration_path(self, value):
        self._configuration_path = value

    def set_db(self, configuration_name):
        if configuration_name:
            path = f"{os.getcwd()}/config_db/{configuration_name}"
        else:
            path = f"{os.getcwd()}/config_db"

        try:
            os.listdir(path)
        except FileNotFoundError:
            os.makedirs(path, exist_ok=True)

        self.configuration_path = path
        self.db_path = os.path.join(path, f"{self.databaseName}.db")
        
        # Initialize database and create table if it doesn't exist
        self._init_table()

    def _init_table(self):
        """Initialize the table with a generic schema for JSON storage"""
        if self.db_path:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS "{self.table_name}" (
                        uid TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()

    def _get_connection(self):
        """Get database connection"""
        if not self.db_path:
            raise NoConfigurationChosen
        return sqlite3.connect(self.db_path)

    def reset_db(self):
        self.db_path = None
        self._configuration_path = ''

    def get_configuration_path(self):
        return self._configuration_path

    def read_all(self) -> List[Dict[str, Any]]:
        """Read all records from the table"""
        if not self.db_path:
            return []
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT data FROM "{self.table_name}"')
                rows = cursor.fetchall()
                return [json.loads(row[0]) for row in rows]
        except sqlite3.Error:
            return []

    def create(self, model: BaseModel):
        """Create a new record"""
        if not self.db_path:
            raise NoConfigurationChosen

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if uid already exists
            cursor.execute(f'SELECT uid FROM "{self.table_name}" WHERE uid = ?', (model.uid,))
            if cursor.fetchone():
                raise UidNotUnique

            # Insert new record
            data_json = json.dumps(model.model_dump())
            cursor.execute(f'''
                INSERT INTO "{self.table_name}" (uid, data) 
                VALUES (?, ?)
            ''', (model.uid, data_json))
            conn.commit()

    def read_id(self, uid: str) -> Dict[str, Any]:
        """Read a record by uid"""
        if not self.db_path:
            raise NoConfigurationChosen

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT data FROM "{self.table_name}" WHERE uid = ?', (uid,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            else:
                raise UidNotFound

    def update(self, model: BaseModel):
        """Update an existing record"""
        if not self.db_path:
            raise NoConfigurationChosen

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute(f'SELECT uid FROM "{self.table_name}" WHERE uid = ?', (model.uid,))
            if not cursor.fetchone():
                raise UidNotFound

            # Update record
            data_json = json.dumps(model.model_dump())
            cursor.execute(f'''
                UPDATE "{self.table_name}" 
                SET data = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE uid = ?
            ''', (data_json, model.uid))
            conn.commit()

    def update_field(self, uid: str, field_name: str, value: Any):
        """Update a specific field of a record"""
        model_dict = self.read_id(uid)
        model = self.convert_dict_to_model(model_dict)
        updated_model = model.copy(update={field_name: value})
        self.update(updated_model)

    def convert_dict_to_model(self, data: dict) -> BaseModel:
        """Convert dictionary to model - to be implemented by subclasses"""
        pass

    def delete(self, uid: str):
        """Delete a record by uid"""
        if not self.db_path:
            raise NoConfigurationChosen

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute(f'SELECT uid FROM "{self.table_name}" WHERE uid = ?', (uid,))
            if not cursor.fetchone():
                raise UidNotFound

            # Delete record
            cursor.execute(f'DELETE FROM "{self.table_name}" WHERE uid = ?', (uid,))
            conn.commit()

    def find_by_query(self, condition_func) -> List[Dict[str, Any]]:
        """Find records by a condition function"""
        all_records = self.read_all()
        return [record for record in all_records if condition_func(record)]

    def execute_raw_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute raw SQL query for advanced operations"""
        if not self.db_path:
            raise NoConfigurationChosen

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

