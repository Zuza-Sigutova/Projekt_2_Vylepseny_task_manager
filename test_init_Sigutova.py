import mysql.connector
def create_test_table():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password= "1111",
        database= "ukoly_test"
    )
    cursor = conn.cursor()

    cursor.execute("""
    create table if not exists ukoly (
        ID INT primary key auto_increment,
        Název varchar (50) not null,
        Popis varchar (500) not null,
        Stav boolean default True,
        Datum_vytvoření date default null
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabulka je vytvořena")

if __name__ == "__main__":
    create_test_table()    