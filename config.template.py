flask_secret_key = 'super secret key'

db_login     = 'admin'
db_password  = 'admin'
db_name      = 'kadath'
server_name  = 'localhost'
charset      = 'utf8mb4'
conn_string  = 'mysql://{0}:{1}@{2}/{3}?charset={4}'.format(db_login, db_password, server_name, db_name, charset)