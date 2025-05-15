import mysql.connector
import pytest
from test_init_Sigutova import create_test_table

@pytest.fixture(scope="session", autouse=True)
def set_up_test():
    create_test_table()

@pytest.fixture(scope="module")
def pripojeni_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password= "1111",
        database= "ukoly_test"
    )
    yield conn
    conn.close()

def test_pridat_ukol(pripojeni_db):
    cursor = pripojeni_db.cursor()
    cursor.execute("INSERT INTO Ukoly (Název, Popis, Stav) VALUES ('Testovací ukol', 'Popis test', 1)")
    pripojeni_db.commit()
    
    cursor.execute("SELECT * FROM Ukoly WHERE Název = 'Testovací ukol'")
    result = cursor.fetchone()

    # smazání testovacího ukolu
    cursor.execute("DELETE FROM Ukoly WHERE Název = 'Testovací ukol'")
    pripojeni_db.commit()

    cursor.close()
    assert result is not None

def test_pridat_ukol_neg(pripojeni_db):
    cursor = pripojeni_db.cursor()
    with pytest.raises(Exception):
        
        cursor.execute("INSERT INTO Ukoly (Popis, Stav) VALUES ('Popis test', 1)")
        pripojeni_db.commit()
    cursor.close()



def test_aktualizovat_ukol(pripojeni_db):
    cursor = pripojeni_db.cursor()

    # vloží testovací úkol
    cursor.execute("INSERT INTO Ukoly (Název, Popis, Stav) VALUES ('Testovací úkol', 'Původní popis', 0)")
    pripojeni_db.commit()

    # aktualizace testovacího úkolu
    cursor.execute("UPDATE Ukoly SET Popis = 'Aktualizovaný popis', Stav = 1 WHERE Název = 'Testovací úkol'")
    pripojeni_db.commit()

    # ověří aktualizaci
    cursor.execute("SELECT Popis, Stav FROM Ukoly WHERE Název = 'Testovací úkol'")
    result = cursor.fetchone()

    # smaže testovací úkol
    cursor.execute("DELETE FROM Ukoly WHERE Název = 'Testovací úkol'")
    pripojeni_db.commit()

    cursor.close()
    assert result == ('Aktualizovaný popis', 1)


def test_aktualizovat_ukol_neg(pripojeni_db):
    cursor = pripojeni_db.cursor()
    cursor.execute("UPDATE Ukoly SET Popis = 'Neexistuje', Stav = 1 WHERE Název = 'Neexistující úkol'")
    pripojeni_db.commit()

    cursor.execute("SELECT * FROM Ukoly WHERE Název = 'Neexistující úkol'")
    result = cursor.fetchone()
    cursor.close()
    assert result is None



def test_odstranit_ukol(pripojeni_db):
    cursor = pripojeni_db.cursor()

    # vloží testovací úkol
    cursor.execute("INSERT INTO Ukoly (Název, Popis, Stav) VALUES ('Testovací úkol', 'Popis test', 0)")
    pripojeni_db.commit()

    # odstranění testovacího úkolu
    cursor.execute("DELETE FROM Ukoly WHERE Název = 'Testovací úkol'")
    pripojeni_db.commit()

    # ověří odstranění testovacího úkolu
    cursor.execute("SELECT * FROM Ukoly WHERE Název = 'Testovací úkol'")
    result = cursor.fetchone()

    cursor.close()
    assert result is None

def test_odstranit_ukol_neg(pripojeni_db):
    cursor = pripojeni_db.cursor()
    cursor.execute("DELETE FROM Ukoly WHERE Název = 'Úkol který není v DB'")
    pripojeni_db.commit()

    cursor.execute("SELECT * FROM Ukoly WHERE Název = 'Úkol který není v DB'")
    result = cursor.fetchone()
    cursor.close()
    assert result is None