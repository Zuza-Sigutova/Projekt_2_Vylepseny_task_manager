import mysql.connector

def pripojeni_db():
    """Tato funkce umožní propojení s databází."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password= "1111",
        database= "ukoly"
    )
def pripojeni_test_db():
    """Připojení do testovací databáze."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="ukoly_test"
    )

def vytvoreni_tabulky(conn=None):
    """Tato funkce vytvoří tabulku ukoly v zadané databázi."""
    close_conn = False
    if conn is None:
        conn = pripojeni_db()
        close_conn = True

    kurzor = conn.cursor()
    kurzor.execute("""
    CREATE TABLE IF NOT EXISTS ukoly (
        ID INT PRIMARY KEY AUTO_INCREMENT,
        Název VARCHAR(50) NOT NULL,
        Popis VARCHAR(500) NOT NULL,
        Stav BOOLEAN DEFAULT TRUE,
        Datum_vytvoření DATE DEFAULT NULL
    )
    """)
    conn.commit()
    kurzor.close()
    if close_conn:
        conn.close()
   


def pridat_ukol_db(nazev, popis, conn=None):
    if not nazev.strip():
        raise ValueError("Název nesmí být prázdný")
    if not popis.strip():
        raise ValueError("Popis nesmí být prázdný")
    
    close_conn=False
    if conn is None:
        conn=pripojeni_db()
        close_conn=True

    kurzor = conn.cursor()
    kurzor.execute("INSERT INTO ukoly (Název, Popis) VALUES (%s, %s)", (nazev, popis))
    conn.commit()
    kurzor.close()
    if close_conn:
        conn.close()

def pridat_ukol():
    while True:
        nazev_ukol = input("\nZadejte název úkolu:").strip()
        if nazev_ukol:
            break
        print("\nPole název nesmí být prázdné, zadejte prosím znovu.")
    while True:
        popis_ukol = input("Zadejte popis úkolu:").strip()
        if popis_ukol:
            break
        print("\nPopis úkolu nesmí být prázdný,zadejte prosím znovu.")
    pridat_ukol_db(nazev_ukol, popis_ukol)
    print("Úkol přidán.")



def zobrazit_ukoly(filtr_stav=None):
    """Tato funkce zobrazí seznam úkolů."""
    try:
        conn = pripojeni_db()
        kurzor = conn.cursor()

        dotaz = "SELECT ID, Název, Popis, Stav FROM ukoly"
        hodnoty = ()

        if filtr_stav is not None:
            dotaz += " WHERE Stav = %s"
            hodnoty = (filtr_stav,)

        kurzor.execute(dotaz, hodnoty)
        vysledky = kurzor.fetchall()

        if not vysledky:
            print("Seznam je prázdný.")
        else:
            for ukol in vysledky:
                stav_raw = ukol[3]
                stav_text = (
                    "Probíhá" if stav_raw == 1
                    else "Hotovo" if stav_raw == 0
                    else "Nezahájeno"
                )
                print(f"ID: {ukol[0]}, Název: {ukol[1]}, Popis: {ukol[2]}, Stav: {stav_text}")

    except mysql.connector.Error as err:
        print(f"Chyba při připojení nebo dotazu: {err}")
    finally:
        if conn.is_connected():
            kurzor.close()
            conn.close()


def aktualizovat_ukol_db(ID_ukolu: int, novy_stav: int, conn=None):
    close_conn = False
    if conn is None:
        conn = pripojeni_db()
        close_conn = True

    kurzor = conn.cursor()
    try:
        kurzor.execute("SELECT * FROM ukoly WHERE id = %s", (ID_ukolu,))
        if not kurzor.fetchone():
            print(f"Úkol s ID {ID_ukolu} neexistuje.")
            return False
        
        if novy_stav not in (0, 1):
            print("Neplatný stav, zadej 0 nebo 1.")
            return False
        
        kurzor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, ID_ukolu))
        conn.commit()
        print("Stav úkolu byl úspěšně aktualizován.")
        return True
    except Exception as e:
        print("Chyba při aktualizaci stavu úkolu:", e)
        return False
    finally:
        kurzor.close()
        if close_conn:
            conn.close()


def aktualizovat_ukol():
    """Interaktivní funkce pro změnu stavu úkolu."""
    conn = pripojeni_db()
    kurzor = conn.cursor()
    try:
        kurzor.execute("SELECT ID, Název, Stav FROM ukoly")
        ukoly = kurzor.fetchall()
        if not ukoly:
            print("V databázi nejsou žádné úkoly k aktualizaci.")
            return

        print("\nSeznam úkolů:")
        for u in ukoly:
            stav_text = (
                "Probíhá" if u[2] == 1
                else "Hotovo" if u[2] == 0
                else "Nezahájeno"
            )
            print(f"ID: {u[0]} | Název: {u[1]} | Stav: {stav_text}")

        while True:
            try:
                ID_ukolu = int(input("\nZadej ID úkolu, jehož stav chceš změnit: "))
                kurzor.execute("SELECT * FROM ukoly WHERE ID = %s", (ID_ukolu,))
                if kurzor.fetchone():
                    break
                else:
                    print("Úkol s tímto ID neexistuje. Zkus to znovu.")
            except ValueError:
                print("Zadej platné číslo ID.")

        while True:
            try:
                novy_stav = int(input("Zadej nový stav (0=Hotovo, 1=Probíhá): "))
                if novy_stav in (0, 1):
                    break
                else:
                    print("Zadej buď 0 nebo 1.")
            except ValueError:
                print("Zadej platné číslo (0 nebo 1).")

        aktualizovat_ukol_db(ID_ukolu, novy_stav)

    except Exception as e:
        print("Chyba při aktualizaci stavu úkolu:", e)
    finally:
        kurzor.close()
        conn.close()


def odstranit_ukol():
    """Funkce pro odstranění úkolu."""
    conn = pripojeni_db()
    kurzor = conn.cursor()
    try:
        kurzor.execute("SELECT ID, Název FROM ukoly")
        ukoly = kurzor.fetchall()

        if not ukoly:
            print("Žádné úkoly k odstranění.")
            return

        print("Seznam úkolů:")
        for idx, (ID, nazev) in enumerate(ukoly, start=1):
            print(f"{idx}. {nazev} (ID: {ID})")

        while True:
            try:
                cislo = int(input("\nZadejte číslo úkolu, které chcete odstranit: "))
                if 1 <= cislo <= len(ukoly):
                    id_odstranit = ukoly[cislo - 1][0]
                    break
                else:
                    print("Zadaný úkol neexistuje. Zkuste to znovu.")
            except ValueError:
                print("Zadejte platné číslo.")

        kurzor.execute("SELECT Název FROM ukoly WHERE ID = %s", (id_odstranit,))
        nazev = kurzor.fetchone()[0]

        kurzor.execute("DELETE FROM ukoly WHERE ID = %s", (id_odstranit,))
        conn.commit()
        print(f"Úkol '{nazev}' byl odstraněn.")
        
    except Exception as e:
        print("Chyba při odstraňování úkolu:", e)
    finally:
        kurzor.close()
        conn.close()


def odstranit_ukol_db(id_odstranit: int, conn=None) -> bool:
    close_conn = False
    if conn is None:
        conn = pripojeni_db()
        close_conn = True
    kurzor = conn.cursor()
    try:
        kurzor.execute("SELECT Název FROM ukoly WHERE ID = %s", (id_odstranit,))
        zaznam = kurzor.fetchone()
        if not zaznam:
            print(f"Úkol s ID {id_odstranit} neexistuje.")
            return False

        kurzor.execute("DELETE FROM ukoly WHERE ID = %s", (id_odstranit,))
        conn.commit()
        print(f"Úkol '{zaznam[0]}' byl odstraněn.")
        return True
    except Exception as e:
        print("Chyba při odstraňování úkolu:", e)
        return False
    finally:
        kurzor.close()
        if close_conn:
            conn.close()
      
      


def hlavni_menu():
    """Tato funkce zobrazí Hlavní menu."""
    while True:
       print("\nHlavní nabídka:")
       print("1. Přidat úkol \n2. Zobrazit úkoly \n3. Aktualizovat úkol \n4. Odtsranit úkol \n5. Ukončit program")
       ukol_moznost=input("Vyberte možnost (1-5): ")
       if ukol_moznost == "1":
          pridat_ukol()  
       elif ukol_moznost == "2":
            print("\nMožnosti filtru:")
            print("1. Všechny úkoly")
            print("2. Jen nezahájené")
            print("3. Jen probíhající")
            print("4. Jen hotové")

            volba = input("Vyberte možnost (1-4): ")

            if volba == "1":
                zobrazit_ukoly()
            elif volba == "2":
                zobrazit_ukoly(None) # stav je NULL -> nezahájeno
            elif volba == "3":
                zobrazit_ukoly(1) # True -> probíhá
            elif volba == "4":
                zobrazit_ukoly(0) # False -> hotovo
            else:
                print("Neplatná volba. Zobrazuji všechny úkoly.")
                zobrazit_ukoly()
          
       elif ukol_moznost == "3":
          aktualizovat_ukol()
       elif ukol_moznost == "4":
          odstranit_ukol()
       elif ukol_moznost == "5":
          print("Konec programu.") 
          break
       else:
           print("\nZadaná neplatná volba. Zadejte prosím znovu.")


if __name__ == "__main__":
    vytvoreni_tabulky()
    hlavni_menu()