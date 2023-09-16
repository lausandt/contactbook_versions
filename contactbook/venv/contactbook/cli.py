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

from contactbook import ERRORS, __app_name__, __version__, config, database, contactbook, manage_contacts

app = typer.Typer()
app.add_typer(manage_contacts.app, name='contacts')
console = Console()

@app.command(name='init')
def init_program(
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
            'Config file not found. Please, run "init" on contactbook first',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return contactbook.ContactManager(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "init" on contactbookfirst',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    
@app.command(name='load')
def load_contacts(path: Annotated[str, typer.Argument(help='the path to the file you want to load')])->None:
    '''load csv file with contacts'''
    cm = _get_contact_manager()
    _, error = cm.load_contacts_from_csv(path)
    if error:
        typer.secho(f'Loading failed with error: {ERRORS[error]}', fg=typer.colors.red)
        raise typer.Exit(1)
    else:
        list_all()
    

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
    table = Table("ID", "Name", "Occupation", "Phone", "Email", "dangerous", title='my contacts', box=box.ROUNDED)
    for id, contact in enumerate(contact_list, 1):
        name, occupation, phone, email, dangerous = contact._asdict().values()
        table.add_row(str(id), name, occupation, phone, email, str(dangerous), style="magenta")
    console.print(table)


@app.command(name='dump')
def dump_contacts_to_csv():
    '''dump all contacts to a csv file'''
    cm = _get_contact_manager()
    s = cm.dump_contacts()
    typer.secho(f'Your contacts are send to {s}', fg=typer.colors.BLUE)

@app.command(name='email')
def send_mail()->None:
    '''send a simple email message from the contactbook app'''
    list_all()
    id = typer.prompt('please select the id of the contact you want to send an email to')
    cm = _get_contact_manager()
    contact_list = cm.get_contact_list()
    contact = contact_list[int(id)-1]
    message = typer.prompt('Please insert the message to send')
    res = cm.send_mail(contact.email, message)
    typer.secho(f'{res}', fg=typer.colors.BLUE)
    
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