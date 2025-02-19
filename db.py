retimport pymysql


try:
    connection = pymysql.connect(host='server121.hosting.reg.ru',
                            user='u0114376_project',
                            password='secret',
                            database='u0114376_project1',
                            cursorclass=pymysql.cursors.DictCursor)
except:
    print('connection: error *404*')
    exit(11)

# https://server121.hosting.reg.ru/phpmyadmin
