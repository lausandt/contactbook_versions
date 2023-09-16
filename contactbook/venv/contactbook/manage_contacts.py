'''a module containing the code to manage contacts'''
from typing import Optional, Any
from typing_extensions import Annotated

from rich.table import Table
from rich.console import Console
from rich import box

import typer

from contactbook import ERRORS, __app_name__, __version__, config, database, contactbook


app = typer.Typer()
console = Console()

def _get_contact_manager() -> contactbook.ContactManager:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "contactbook init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return contactbook.ContactManager(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "contactbook init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


@app.command('add')
def add( 
    name: Annotated[str, typer.Argument()],
    occupation: Annotated[str, typer.Option(help='The occupation of the contact written in between "quotation marks"')] = '',
    phone: Annotated[str, typer.Option(help='The phonenumber of the contact written in between quotation marks "212-5555-7777"')] = '',
    email:Annotated[str, typer.Option(help='the contact`s email address')]='',
    dangerous: Annotated[bool, typer.Option(help='Is the contact a dangerous contact False or True')] = False
) -> None:
    """Add a new contact with at minimal a name."""
    cm = _get_contact_manager()
    contact, error = cm.add(name, occupation, phone, email, dangerous)
    if error: 
        typer.secho(
            f'Adding contact failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""contact: "{contact.name}" was added"""
            f""" with occupation: {contact.occupation} phone: {contact.phone} email: {contact.email} dangerous:{contact.dangerous}""",
            fg=typer.colors.MAGENTA,
        )

@app.command('find')
def find(name: Annotated[str,typer.Argument(help='the name of the contact you are looking for')])->None:
    """find all contacts with the given name."""
    cm = _get_contact_manager()
    contacts = cm.find_contact(name)
    if len(contacts) == 0:
        typer.secho(
            f"There are no contacts named {name}", fg=typer.colors.RED
        )
        raise typer.Exit()
    elif len(contacts)==1:
        contact = contacts[0]
        typer.secho(
            f"""contact: "{contact.name}" """
            f""" occupation: {contact.occupation} phone: {contact.phone} email: {contact.email} dangerous:{contact.dangerous}""",
            fg=typer.colors.MAGENTA,
        )
    else:
        typer.secho(f"There are multiple contacts named {name}", fg=typer.colors.GREEN)
        table = Table("ID", "Name", "Occupation", "Phone","Email", "dangerous", title='find results', box=box.ROUNDED)
        for id, contact in enumerate(contacts, 1):
            name, occupation, phone, email, dangerous = contact._asdict().values()
            table.add_row(str(id), name, occupation, phone, email, str(dangerous), style="magenta")
        console.print(table)
        

@app.command('remove')
def remove_contact()->None:
    """Remove a contact from the list"""
    cm = _get_contact_manager()
    contacts = cm.get_contact_list()
    if len(contacts) == 0:
        typer.secho(
            f"There are no contacts", fg=typer.colors.RED
        )
        raise typer.Exit()
    table = Table("ID", "Name", "Occupation", "Phone", "Email", "dangerous", title='current contacts', box=box.ROUNDED)
    for id, contact in enumerate(contacts, 1):
        name, occupation, phone, email, dangerous = contact._asdict().values()
        table.add_row(str(id), name, occupation, email, phone, str(dangerous), style="yellow")
    console.print(table)
    id = typer.prompt('which contact do you want to remove? Please select an ID')
    contact = contacts[int(id)-1]
    typer.secho(
            f"""contact: "{contact.name}" """
            f""" occupation: {contact.occupation} phone: {contact.phone} email: {contact.email} dangerous:{contact.dangerous}""",
            fg=typer.colors.MAGENTA,
        )
    delete = typer.confirm(f"Are you sure you want to delete {contact.name} ?")
    if not delete:
        print("Not deleting")
        raise typer.Exit()
    contact, error = cm.remove_contact(int(id))
    if error:
        print(ERRORS[error])
    else:
        print(f"Deleting {contact.name}!")

@app.command(name='change')
def change_contact()->None:
    '''changes a contact's attribute to a new value '''
    cm = _get_contact_manager()
    contacts = cm.get_contact_list()
    if len(contacts) == 0:
        typer.secho(
            f"There are no contacts", fg=typer.colors.RED
        )
        raise typer.Exit()
    table = Table("ID", "name", "occupation", "phone","email", "dangerous", title='current contacts', box=box.ROUNDED)
    for id, contact in enumerate(contacts, 1):
        name, occupation, phone, email, dangerous = contact._asdict().values()
        table.add_row(str(id), name, occupation, phone, email, str(dangerous), style="yellow")
    console.print(table)
    id = typer.prompt('which contact do you want to change? Please choose per ID')
    attr = typer.prompt('What attribute do you want to change?')
    value = typer.prompt('what should the value be?')
    contact, error = cm.change_contact(int(id), attr.lower(), value)
    if error:
        print(error)
    else:
        typer.secho(f'''contact: {contact.name} occupation: {contact.occupation} phone: {contact.phone} 
                    email: {contact.email} dangerous: {contact.dangerous}''', fg=typer.colors.MAGENTA)
