"""
database.py

Data access layer for application
Handles all SQLite operations including setup, insert and retrieval
"""

# python's built-in libraries
import sqlite3
import pandas as pd

# stores database filename as constant variable
DB_NAME = "campaign.db"

# 
def init_db():
    # opens connection to database file
    conn = sqlite3.connect(DB_NAME)
    # cursor used to execute SQL commands
    c = conn.cursor()

    # creates table if it doesn't exist
    c.execute()

    # saves changes permanently
    conn.commit()
    # closes connection
    conn.close()


def insert_dataframe(df):
    conn = sqlite3.connect(DB_NAME)

    # normalises column names by removing whitespace and converting to lowercase
    df.columns = df.columns.str.strip().str.lower()

    # select the columns needed
    required_columns = ["name", "industry", "market_size", "pipeline", "engagement"]
    df = df[required_columns]
    # where to insert to, add new rows rather than replace, don't add index columns
    df.to_sql("accounts", conn, if_exists="append", index=False)

    conn.close()

# runs SQL query and convert results to table
def get_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM accounts", conn)
    conn.close()
    return df
