import mysql.connector

_host = 'localhost'
_user = 'root'
_password = 'password'
_database = 'datasys'


def main(argument, commit=False):
    mydb = mysql.connector.connect(
        host=_host,
        user=_user,
        password=_password,
        database=_database
    )

    mycursor = mydb.cursor()

    mycursor.execute(argument)

    myresult = mycursor.fetchall()
    if commit:
        mydb.commit()
    return myresult