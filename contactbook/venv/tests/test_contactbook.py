import pytest
import json
from typer.testing import CliRunner


from contactbook import DB_READ_ERROR, SUCCESS, __app_name__, __version__, cli, contactbook



runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def mock_json_file(tmp_path):
    contact = [{"Name": "Croc", "Occupation": "Salty", "Email":"peckish@snacking.gov ", "Dangerous": True}]
    db_file = tmp_path / "test.json"
    with db_file.open("w") as db:
        json.dump(contact, db, indent=4)
    return db_file

test_data1 = contactbook.Contact(
        name= "George",
        occupation= "Physicist & big bed theorist",
        phone="0612055453",
        email="george@sleepy_genius.org",
        dangerous= False,
    )

test_data2 = contactbook.Contact(
        name= "Rhino",
        occupation= "Slacker God",
        phone= "06-i-am-in-your-head",
        email= "running_around_naked@snorting_loudly.god",
        dangerous= False
    )

test_data3 = contactbook.Contact(
    name="Croc", 
    occupation= "Salty",
    phone="0644378446",
    email='snacking@delicous_herons.com',
    dangerous= True
)

test_data4 = contactbook.Contact(
    name="Rhino",
    occupation= "Purple fashionista",
    phone= "06-PURPLE",
    email='purple@fashionista.god',
    dangerous= True,        
)

@pytest.mark.parametrize(
    "name, occupation, phone, email, expected",
    [
        pytest.param(
            "George",
            "Physicist & big bed theorist",
            "0612055453",
            "george@sleepy_genius.org",   
            (test_data1, SUCCESS),
        ),
            pytest.param(
            "Rhino",
            "Slacker God",
             "06-i-am-in-your-head",
             "running_around_naked@snorting_loudly.god",
            (test_data2, SUCCESS),
        ),
    ],
)
def test_add(mock_json_file, name, occupation, phone, email, expected):
    cm = contactbook.ContactManager(mock_json_file)
    assert cm.add(name, occupation, phone, email) == expected
    read = cm._db_handler.read_contacts()
    assert len(read.contact_list) == 2

@pytest.fixture
def mock_json_file_two(tmp_path):
    contact = [
        test_data1._asdict(), test_data2._asdict(), test_data3._asdict(), test_data4._asdict()    
    ]
    db_file = tmp_path / "test.json"
    with db_file.open("w") as db:
        json.dump(contact, db, indent=4)
    return db_file

@pytest.mark.parametrize('input, expected', [
    pytest.param('George', 1),
    pytest.param('Croc', 1),
    pytest.param('Ente', 0),
    pytest.param('Rhino',2)
])
def test_find(mock_json_file_two, input, expected):
    cm = contactbook.ContactManager(mock_json_file_two)
    assert len(cm.find_contact(input)) == expected

@pytest.mark.parametrize('input, expected', [
    pytest.param(1, [
        test_data2._asdict(),
        test_data3._asdict(),
        test_data4._asdict()
            ]),
    pytest.param(3, [  
        test_data1._asdict(),            
        test_data2._asdict(),
        test_data4._asdict() 
            ]),
    
])
def test_remove_contact(mock_json_file_two, input, expected):
    cm = contactbook.ContactManager(mock_json_file_two)
    cm.remove_contact(input)
    assert cm.get_contact_list() == expected


@pytest.mark.parametrize('id, attr, value, expected', [
    pytest.param(1, 'dangerous', True, 
        {"name": "George",
         "occupation": "Physicist & big bed theorist",
         "phone":"0612055453",
         "email":"george@sleepy_genius.org",
         "dangerous": True}),
    pytest.param(3, "email", "ineed@coteduboeuf.fr", {
    "name":"Croc", 
    "occupation": "Salty",
    "phone":"0644378446",
    "email":"ineed@coteduboeuf.fr",
    "dangerous": True
})
])
def test_change_contact(mock_json_file_two, id, attr, value, expected):
    cm = contactbook.ContactManager(mock_json_file_two)
    con, _ = cm.change_contact(id, attr, value)
    assert con._asdict() == expected

    
    