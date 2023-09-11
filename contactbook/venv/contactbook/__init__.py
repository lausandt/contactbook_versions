"""Top level package for the contactbook project """

__app_name__ = "contactbook"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    NO_SUCH_CONTACT_ERROR
) = range(8)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "contact id error",
    NO_SUCH_CONTACT_ERROR: 'There is no contact with that name'
}