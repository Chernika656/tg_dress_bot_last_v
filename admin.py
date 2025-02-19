import db


def admins_db_id(user_id):
    with db.connection.cursor() as cursor:
        cursor.execute('SELECT admin FROM users_settings WHERE id = %s', user_id)
        result = cursor.fetchone()
        if result['admin'] == 1:
            return True
        else:
            return False

def add_admin(user_id):
    with db.connection.cursor() as cursor:
        cursor.execute("UPDATE users_settings SET admin = 1 WHERE id = %s", user_id)
        db.connection.commit()
