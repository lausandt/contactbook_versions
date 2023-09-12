"""
This module provides the command line interface for the project
This is the view in the MVC pattern
"""

from typing import Optional, Any
from typing_extensions import Annotated

from pathlib import Path

from rich.table import Table
from rich.console import Console
from rich import box

import typer

from contactbook import ERRORS, __app_name__, __version__, config, database, contactbook

app = typer.Typer()
console = Console()

@app.command()
def init(
    db_path: str = typer.Option( # typer.Option for we have a default path
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="database location?", 
    ),
) -> None:
    """Initialize the contact database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The contact database is {db_path}", fg=typer.colors.MAGENTA)

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

@app.command()
def add( 
    name: Annotated[str, typer.Argument()],
    occupation: Annotated[str, typer.Option(help='The occupation of the contact written in between "quotation marks"')] = '',
    phone: Annotated[str, typer.Option(help='The phonenumber of the contact written in between quotation marks "212-5555-7777"')] = '',
    email:Annotated[str, typer.Option(help='the contact`s email address')]='',
    professional: Annotated[bool, typer.Option(help='Is the contact a professional contact False or True')] = False
) -> None:
    """Add a new contact with at minimal a name."""
    cm = _get_contact_manager()
    contact, error = cm.add(name, occupation, phone, email, professional)
    if error: 
        typer.secho(
            f'Adding contact failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""contact: "{contact.name}" was added"""
            f""" with occupation: {contact.occupation} phone: {contact.phone} email: {contact.email} professional:{contact.professional}""",
            fg=typer.colors.MAGENTA,
        )

@app.command(name="list")
def list_all() -> None:
    """List all contacts."""
    cm = _get_contact_manager()
    contact_list = cm.get_contact_list()
    if len(contact_list) == 0:
        typer.secho(
            "There are no contacts in the list yet", fg=typer.colors.RED
        )
        raise typer.Exit()
    typer.secho("\n")
    table = Table("ID", "Name", "Occupation", "Phone", "Email", "Professional", title='my contacts', box=box.ROUNDED)
    for id, contact in enumerate(contact_list, 1):
        name, occupation, phone, email, professional = contact._asdict().values()
        table.add_row(str(id), name, occupation, phone, email, str(professional), style="magenta")
    console.print(table)

@app.command()
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
            f""" occupation: {contact.occupation} phone: {contact.phone} email: {contact.email} professional:{contact.professional}""",
            fg=typer.colors.MAGENTA,
        )
    else:
        typer.secho(f"There are multiple contacts named {name}", fg=typer.colors.GREEN)
        table = Table("ID", "Name", "Occupation", "Phone","Email", "Professional", title='find results', box=box.ROUNDED)
        for id, contact in enumerate(contacts, 1):
            name, occupation, phone, email, professional = contact._asdict().values()
            table.add_row(str(id), name, occupation, phone, email, str(professional), style="yellow")
        console.print(table)
        id = typer.prompt('Please choose per ID')
        contact = contacts[int(id)-1]
        typer.secho(
            f"""contact: "{contact.name}" """
            f""" occupation: {contact.occupation} phone: {contact.phone} email: {contact.email} professional:{contact.professional}""",
            fg=typer.colors.MAGENTA,
        )

@app.command()
def remove()->None:
    """Remove a contact from the list"""
    cm = _get_contact_manager()
    contacts = cm.get_contact_list()
    if len(contacts) == 0:
        typer.secho(
            f"There are no contacts", fg=typer.colors.RED
        )
        raise typer.Exit()
    table = Table("ID", "Name", "Occupation", "Phone", "Email", "Professional", title='current contacts', box=box.ROUNDED)
    for id, contact in enumerate(contacts, 1):
        name, occupation, phone, email, professional = contact._asdict().values()
        table.add_row(str(id), name, occupation, email, phone, str(professional), style="yellow")
    console.print(table)
    id = typer.prompt('which contact do you want to remove? Please select an ID')
    contact = contacts[int(id)-1]
    typer.secho(
            f"""contact: "{contact.name}" """
            f""" occupation: {contact.occupation} phone: {contact.phone} email: {contact.email} professional:{contact.professional}""",
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
    table = Table("ID", "name", "occupation", "phone","email", "professional", title='current contacts', box=box.ROUNDED)
    for id, contact in enumerate(contacts, 1):
        name, occupation, phone, email, professional = contact._asdict().values()
        table.add_row(str(id), name, occupation, phone, email, str(professional), style="yellow")
    console.print(table)
    id = typer.prompt('which contact do you want to change? Please choose per ID')
    attr = typer.prompt('What attribute do you want to change?')
    value = typer.prompt('what should the value be?')
    contact, error = cm.change_contact(int(id), attr.lower(), value)
    if error:
        print(error)
    else:
        typer.secho(f'''contact: {contact.name} occupation: {contact.occupation} phone: {contact.phone} 
                    email: {contact.email} professional: {contact.professional}''', fg=typer.colors.MAGENTA)
                 
    
def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return