'''Contactbook is the controller in our MVC pattern'''
import pandas as pd
import csv
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
from contactbook import DB_READ_ERROR, ID_ERROR
from contactbook.database import DatabaseHandler, DEFAULT_DB_FILE_PATH
from contactbook.email import send_mail

DUMP_PATH = Path.home().joinpath("." + Path.home().stem + "_contact.csv")

class Contact(NamedTuple):
    name: str
    occupation: Optional[str]
    phone: Optional[str]
    email:Optional[str]
    dangerous: bool

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

    def load_contacts_from_csv(self, csvFilePath:Path)->Tuple[List[Contact],int]:
        '''Method to add multiple contacts from a csv'''
        read = self._db_handler.read_contacts()
        if read.error:
            return ([], read.error)
        contact_list = read.contact_list
        with open(csvFilePath, 'r', encoding='utf-8-sig') as csvf: 
            csvReader = csv.DictReader(csvf) 
            
            for row in csvReader:              
                del row[''] # csv module is designed to add an empty string for an empty csv cell            
                contact_list.append(row)
        write = self._db_handler.write_contacts(contact_list)
        return ([Contact(**c) for c in contact_list], write.error)

    def dump_contacts(self, path:Path=DUMP_PATH)->str:
        '''Method to dump all contacts to a csv file'''
        df = pd.read_json(DEFAULT_DB_FILE_PATH)
        df.to_csv(DUMP_PATH, index=False)
        return DUMP_PATH
      
    def get_contact_list(self)->List[Contact]:
        '''get the current contact_list'''
        read = self._db_handler.read_contacts()
        return [Contact(**c) for c in read.contact_list]
    
    def find_contact(self, name:str)->List[Contact]:
        '''finds a contact by name may return multiple if the name appears more than once'''
        return [c for c in self.get_contact_list() if c.name == name ]
    
    def remove_contact(self, id:int)->(Contact, int):
        '''removes a contact from the contact list'''
        read = self._db_handler.read_contacts()
        if read.error:
            return (None,read.error)
        try:
            contact = read.contact_list.pop(id - 1)
        except IndexError:
            return (None, ID_ERROR)
        write = self._db_handler.write_contacts(read.contact_list) 
        return (Contact(**contact), write.error)
    
    def change_contact(self,id:int, attr=str, value=Any)->Tuple[Contact, int]:
        read = self._db_handler.read_contacts()
        if read.error:
            return (None,read.error)
        try:
            contact = read.contact_list.pop(id-1)
        except IndexError:
            return (None, ID_ERROR)
        if attr in contact.keys():
            contact[attr] = value
            read.contact_list.append(contact)
            write = self._db_handler.write_contacts(read.contact_list) 
            return (Contact(**contact),write.error)
        else:
            return (None, AttributeError(f'{attr} not an an attribute'))

    def send_mail(self, receiver_mail:str, message:str)->str:
        return send_mail(receiver_mail, message)

        
    
    

