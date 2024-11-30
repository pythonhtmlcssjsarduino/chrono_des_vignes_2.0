import os
from dotenv import load_dotenv
load_dotenv()

import pymysql

connection = pymysql.connect(host='localhost',
                             user='root',
                             password=os.environ['db_password'])

with connection:
    '''with connection.cursor() as cursor:
        # Create a new record
        sql = "CREATE DATABASE site_mysql"
        cursor.execute(sql)
    connection.commit()'''

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    with connection.cursor() as cursor:
        cursor.execute('SHOW DATABASES')
        for db in cursor:
            print(db)
