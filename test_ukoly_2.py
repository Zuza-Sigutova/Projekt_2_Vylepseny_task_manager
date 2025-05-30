import pytest
import mysql.connector
from Projekt_2_Sigutova import pridat_ukol_db, aktualizovat_ukol_db, pripojeni_test_db, odstranit_ukol_db, vytvoreni_tabulky 


def test_pripojeni_db():
    conn = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="ukoly_test"
        )
        assert conn.is_connected()
    finally:
        if conn:
            conn.close()

@pytest.fixture(scope="module")
def test_db_conn():
    conn = pripojeni_test_db()
    vytvoreni_tabulky(conn)
    yield conn
    conn.close()

@pytest.fixture
def vlozit_ukol(test_db_conn):
    cursor = test_db_conn.cursor()
    cursor.execute("INSERT INTO ukoly (Název, Popis, Stav) VALUES (%s, %s, %s)",
                   ("Testovací úkol", "Popis testovacího úkolu", 1))
    test_db_conn.commit()
    id_ukolu = cursor.lastrowid
    cursor.close()
    yield id_ukolu
    
    # Po testu smaže záznam
    cursor = test_db_conn.cursor()
    cursor.execute("DELETE FROM ukoly WHERE ID = %s", (id_ukolu,))
    test_db_conn.commit()
    cursor.close()



def test_pridat_ukol_db_pozitivni():
    nazev = "Test úkol"
    popis = "Test popisu úkolu"
    conn = pripojeni_test_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM ukoly WHERE Název = %s", (nazev,))
        conn.commit()

        pridat_ukol_db(nazev, popis, conn=conn)

        cursor.execute("SELECT Název, Popis FROM ukoly WHERE Název = %s", (nazev,))
        vysledek = cursor.fetchone()
        assert vysledek is not None
        assert vysledek[0] == nazev
        assert vysledek[1] == popis

    finally:
        
        cursor.execute("DELETE FROM ukoly WHERE Název = %s", (nazev,))
        conn.commit()
        cursor.close()
        conn.close()


def test_pridat_ukol_db_negativni():
    conn = pripojeni_test_db()

    # Test s prázdným názvem
    with pytest.raises(ValueError):
        pridat_ukol_db("", "Popis", conn=conn)

    # Test s prázdným popisem
    with pytest.raises(ValueError):
        pridat_ukol_db("Název", "", conn=conn)

    conn.close()




def test_aktualizovat_ukol_db_pozitivni(vlozit_ukol, test_db_conn):
    id_ukolu = vlozit_ukol
    vysledek = aktualizovat_ukol_db(id_ukolu, 0, conn=test_db_conn)
    assert vysledek is True

def test_aktualizovat_ukol_db_negativni(test_db_conn):
    # Pokus o aktualizaci neexistujícího úkolu
    vysledek = aktualizovat_ukol_db(999999, 1, conn=test_db_conn)
    assert vysledek is False



def test_odstranit_ukol_db_pozitivni(vlozit_ukol, test_db_conn):
    id_ukolu = vlozit_ukol
    vysledek = odstranit_ukol_db(id_ukolu, conn=test_db_conn)
    assert vysledek is True

def test_odstranit_ukol_db_negativni(test_db_conn):
    vysledek = odstranit_ukol_db(999999, conn=test_db_conn) # neexistující ID
    assert vysledek is False    