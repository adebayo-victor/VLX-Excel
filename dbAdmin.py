from cs50 import SQL

# 1. Connect to the database using the CS50 SQL function
# This uses the same syntax as in CS50 problem sets.
DB_FILE = "templates.db"
db = SQL(f"sqlite:///{DB_FILE}")

print(db.execute("SELECT key FROM template_data "))

