import pymysql

global connection, cursor

def connexion_mysql():
    try:
        connection = pymysql.connect(host='localhost', user='sql', password='UserSQL', db='chat')
        cursor = connection.cursor()

    except pymysql.err.OperationalError:
        connection = None
        cursor = None