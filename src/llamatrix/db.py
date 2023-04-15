database = None


def load_db(db_file):
    with open(db_file, "r") as f:
        database = eval(f.read())

    return database


def save_db(db_file, database):
    with open(db_file, "w") as f:
        f = open(db_file, "w")
        f.write(str(database))
        f.close()


def init_db(db_file):
    global database
    
    try:
        database = load_db(db_file)
        
    except FileNotFoundError:
        database = {}
        save_db(db_file, database)
