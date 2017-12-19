import pymysql

from Create import exec_sql_file

cnx = pymysql.connect(user='root',
                      password='root',
                      host='localhost',
                      charset='utf8mb4')

try:
    cnx = pymysql.connect(user='root',
                          password='root',
                          host='localhost',
                          charset='utf8mb4',
                          db='openfoodfacts')
except pymysql.InternalError:
    print("No database detected, creating database...")
    cur = cnx.cursor()
    exec_sql_file(cur, 'openfoodfacts_create.sql')

