#!/usr/bin/python3
"""
Convert contact email addresses to lowercase

In these tables convert all email address values in the email column to lowercase:
- contact_automatic
- contact
- email_status
- email_tag

Not necessary:
- email_annotation: That's a view
"""
import psycopg2

def main():
    from contactdb_api.contactdb_api.serve import read_configuration
    conn = psycopg2.connect(dsn=read_configuration()["libpg conninfo"])
    try:
        with conn:
            for table in ('contact_automatic', 'contact', 'email_status', 'email_tag'):
                with conn.cursor() as cur:
                    cur.execute(f"UPDATE {table} SET email = LOWER(email) WHERE email != LOWER(email)'")
    finally:
        # Have to manually close connection even when using with-statement:
        # https://www.psycopg.org/docs/usage.html#with-statement
        conn.close()

if __name__ == '__main__':
    main()
