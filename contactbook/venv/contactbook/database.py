'''
   instead of using a real database we store the data persistent with a JSON
'''

import configparser
import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from contactbook import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS


DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_contact.json"
)

def get_database_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    """Create the database."""
    try:
        db_path.write_text("[]")  
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
class DBResponse(NamedTuple):
    '''Data container that allows you to send data to and retrieve data from the contact database'''
    contact_list: List[Dict[str, Any]]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_contacts(self) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:  # Catch wrong JSON format
                    return DBResponse([], JSON_ERROR)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)

    def write_contacts(self, contact_list: List[Dict[str, Any]]) -> DBResponse:
        try:
            with self._db_path.open("w") as db:
                json.dump(contact_list, db, indent=4)
            return DBResponse(contact_list, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(contact_list, DB_WRITE_ERROR)