import pytest
import mysql.connector
from Projekt_2_Sigutova import pridat_ukol_db, aktualizovat_ukol_db, pripojeni_test_db, odstranit_ukol_db


def test_pripojeni_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password= "1111",
        database= "ukoly_test"
    )

@pytest.fixture(scope="module")
def test_db_conn():
    conn = pripojeni_test_db()
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
    
    pridat_ukol_db(nazev, popis)


def test_pridat_ukol_db_negativni():
    # Test s prázdným názvem
    with pytest.raises(ValueError):
        pridat_ukol_db("", "Popis")

    # Test s prázdným popisem
    with pytest.raises(ValueError):
        pridat_ukol_db("Název", "")




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