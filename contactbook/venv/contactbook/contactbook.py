'''Contactbook is the controller in our MVC pattern'''

from pathlib import Path
from typing import Any, Dict, List, Union, NamedTuple, Optional, Tuple

from contactbook import DB_READ_ERROR, ID_ERROR, NO_SUCH_CONTACT_ERROR, SUCCESS
from contactbook.database import DatabaseHandler

class Contact(NamedTuple):
    name: str
    occupation: Optional[str]
    phone: Optional[str]
    email:Optional[str]
    dangerous:bool

class ContactManager:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, name: str, occupation: str='', phone: str='', email:str='', dangerous:bool=False) -> Tuple[Contact, int]:
        """Add a contact to the database."""
        contact = Contact(name=name, occupation=occupation, phone=phone, email=email, dangerous=dangerous)
        read = self._db_handler.read_contacts()
        if read.error == DB_READ_ERROR:
            return (contact, read.error)
        read.contact_list.append(contact._asdict())
        write = self._db_handler.write_contacts(read.contact_list)
        return (contact, write.error)
    
    def get_contact_list(self)->List[Dict[str, Any]]:
        '''get the current contact_list'''
        read = self._db_handler.read_contacts()
        return read.contact_list
    
    def find_contact(self, name:str)->List[Contact]:
        return [Contact(**c) for c in self.get_contact_list() if c['name'] == name ]
    
    def remove_contact(self, id:int)->(Contact, int):
        '''removes a contact with from the contact_list'''
        read = self._db_handler.read_contacts()
        if read.error:
            return (None,read.error)
        try:
            contact = read.contact_list.pop(id - 1)
        except IndexError:
            return (None, ID_ERROR)
        write = self._db_handler.write_contacts(read.contact_list) 
        return (Contact(**contact), write.error)
    
    def remove_all(self)->None:
        ...

    def change_contact(self,id:int, attr=str, value=Any)->(Contact, int):
        read = self._db_handler.read_contacts()
        if read.error:
            return (None,read.error)
        try:
            contact = read.contact_list.pop(id-1)
        except IndexError:
            return (None, ID_ERROR)
        contact[attr] = value
        read.contact_list.append(contact)
        write = self._db_handler.write_contacts(read.contact_list) 
        return (Contact(**contact),write.error)       

        



        
    
    

