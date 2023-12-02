import pymysql

global connection, cursor

def connexion_mysql():
    try:
        connection = pymysql.connect(host='localhost', user='root', password='rootroot', db='chat')
        cursor = connection.cursor()

    except pymysql.err.OperationalError:
        connection = None
        cursor = None
        