from decouple import config
import psycopg2

def set_db_table(file_name):
    prod_files = ['index.py', 'get_result.py']
    test_files = ['index_test.py', 'get_result_test.py']

    if file_name in prod_files:
        return config('DB_TABLE')
    elif file_name in test_files:
        return config('DB_TABLE_TEST')
    else:
        raise Exception('Invalid filename')

def set_conn():
    return psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASS'),
        host=config('DB_HOST')
    )

def sql_command(cur, conn, statement):
    cur.execute(statement)
    conn.commit()