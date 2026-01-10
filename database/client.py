import os
import json
import logging
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from sqlmodel import SQLModel, create_engine, Session, text
from typing import Any, Dict, List, Optional, Tuple, Iterable

from ingestion.models import raw_data


logging.basicConfig(level=logging.INFO, filename='logs/info.log', filemode='a', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')


class DatabaseClient(ABC):
    """Abstract base class for database clients."""
    
    @abstractmethod
    def connect(self) -> Any:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a SQL query."""
        pass

    @abstractmethod
    def insert(self, table: str, records: Iterable[dict]) -> None:
        """Insert data into a specified table."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    def __enter__(self) -> "DatabaseClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # Propagate exceptions if any

class SQLModelClient(DatabaseClient):
    """SQLModel client for database operations."""
    
    def __init__(self, database_url: str, echo: bool = False):
        logging.info(f"Initializing SQLModelClient with database URL: {database_url}")
        self.engine = create_engine(database_url, echo=echo)

        logging.info("Creating database tables if they do not exist")
        SQLModel.metadata.create_all(self.engine)

        self.session = None

    def connect(self) -> None:
        self.session = Session(self.engine)

    def close(self) -> None:
        if self.session:
            self.session.close()

    def execute(self, query: str, params=None):
        if not self.session:
            raise RuntimeError("Database session is not established.")
        
        result = None
        try:
            with self.session as s:
                result = s.exec(text(query), params=params or {})
                s.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
        
        return result

    def insert(self, table: str, records: Iterable[dict]) -> None:
        if not self.session:
            raise RuntimeError("Database session is not established.")

        for record in records:
            logging.debug(f"Preparing to insert record into {table}")
            column_names = ", ".join(record.keys())
            placeholders = ", ".join(f":{key}" for key in record.keys())
            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

            logging.debug(f"Executing query: {sql} with params: {record}")
            self.execute(sql, record)

            logging.info(f"Inserted record into {table}")



class Client(ABC):
    def __init__(self, url: str = None):
        self.url = url
    @abstractmethod
    def execute(self, query: str, params=None):
        raise NotImplementedError("Subclasses must implement this method")
    @abstractmethod
    def save(self, **kwargs) -> None:
        pass
    
class SQLLiteClient(Client):
    def __init__(self, url: str = None):
        super().__init__(url=url)
        logging.info(f"Initializing SQLLiteClient with database URL: {self.url}")
        self.engine = create_engine(self.url)

        logging.info("Creating database tables if they do not exist")
        SQLModel.metadata.create_all(self.engine)

    def save(self, **kwargs) -> None:
        model = kwargs.get('model')
        data = kwargs.get('data')

        logging.info(f"Saving data to database using model {model.__name__}")
        with Session(self.engine) as session:
          asset = model(
              **data
          )
          session.add(asset)

          logging.info("Committing session to save data")
          session.commit()
    
    def execute(self, query: str, params=None):
        if not self.session:
            raise RuntimeError("Database session is not established.")
        
        result = None
        try:
            with self.session as s:
                result = s.exec(text(query), params=params or {})
                s.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
        
        return result
            
class JSONClient(Client):
    def __init__(self, url: str = None):
        super().__init__(url=url)
        if self.url and not os.path.exists(self.url):
            os.makedirs(self.url)

    def save(self, **kwargs) -> None:
        data = kwargs.get('data')
        with open(f"{self.url}/{data['source']}_data.json", "+w") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    
    # example usage
    db_url = "sqlite:///./test.db"
    client = SQLModelClient(db_url, echo=True)

    with client as db_client:
        db_client.execute("CREATE TABLE IF NOT EXISTS test_2 (id INTEGER, name TEXT)")
        db_client.insert("test", [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
        result = db_client.execute("SELECT * FROM test")
        for row in result:
            print(row)
    # client = SQLLiteClient(url="sqlite:///./data/test.db")
    # client.save(
    #     model=raw_data,
    #     data={
    #         "source": "test_source",
    #         "payload": '{"external_id": "123", "name": "Test Asset", "description": "This is a test asset"}'
    #     }
    # )