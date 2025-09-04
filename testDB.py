import os
import psycopg2
from datetime import date
from dbutil import add_order, move_order_to_income, mark_order_delivered

# Set this environment variable in your script or OS before running
#os.environ['SUPABASE_CONN_STRING'] = "postgresql://postgres:VibrantCakes12@db.tmmyrqbojigzfzykjtyo.supabase.co:5432/postgres?sslmode=require"

def test_connection_and_fetch():
    conn_string = os.environ.get('SUPABASE_CONN_STRING')
    if not conn_string:
        print("SUPABASE_CONN_STRING environment variable not set.")
        return

    try:
        conn = psycopg2.connect(conn_string)
        print("Connection successful.")

        cur = conn.cursor()

        tables = ['expenses', 'income', 'orders']

        for table in tables:
            print(f"\nData from {table}:")
            cur.execute(f"SELECT * FROM {table} LIMIT 5;")  # Limit to 5 rows for testing
            rows = cur.fetchall()
            for row in rows:
                print(row)

        cur.close()
        conn.close()
        print("\nConnection closed.")

    except Exception as e:
        print("Error connecting or fetching data:", e)

def test_add_order():
    try:
        delivery_date=date.today()
        customer="AAAAA"
        item="IIII"
        price=2345.0
        advance=123.0
        description="asdasdasdsd"
        
        add_order(delivery_date, customer, item, price, advance, description)


    except Exception as e:
        print("Error connecting or fetching data:", e)

if __name__ == '__main__':
    #test_add_order()
    #move_order_to_income("1")
    test_connection_and_fetch()
    mark_order_delivered(7)

