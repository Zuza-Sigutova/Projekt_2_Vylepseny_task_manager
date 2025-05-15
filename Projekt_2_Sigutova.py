import mysql.connector

def pripojeni_db ():
    """Tato funkce umožní propojení s databází."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password= "1111",
        database= "ukoly"
    )

def vytvoreni_tabulky():
    """Tato funkce umožní vytvořit tabulku a propojení s databází."""
    conn = pripojeni_db()
    kurzor = conn.cursor()

    kurzor.execute("""
    create table if not exists ukoly (
        ID INT primary key auto_increment,
        Název varchar (50) not null,
        Popis varchar (500) not null,
        Stav boolean default True,
        Datum_vytvoření date default null
    )
    """)
    
    conn.commit()
    kurzor.close()
    conn.close()
    print("Tabulka je vytvořena")

def pridat_ukol():
    """Tato funkce umožní přidat úkol."""
    conn = pripojeni_db()
    kurzor = conn.cursor()

    while True:
      nazev_ukol=input("\nZadejte název úkolu:").strip()
      if nazev_ukol:
         break
      else:
        print("\nPole název nesmí být prázdné, zadejte prosím znovu.")

    while True:  
      popis_ukol=input("Zadejte popis úkolu:").strip()
      if popis_ukol:
         break
      else:
         print("\nPopis úkolu nesmí být prázdný,zadejte prosím znovu.")

    kurzor.execute("INSERT INTO ukoly (Název, Popis) Values (%s, %s)", (nazev_ukol, popis_ukol))
    conn.commit()
    kurzor.close()
    conn.close()
    print("Úkol přidán.")

def zobrazit_ukoly(filtr_stav=None):
    """Tato funkce zobrazí seznam úkolů."""
    try:
        conn = pripojeni_db() 
        kurzor = conn.cursor()

        if filtr_stav in ("Nezahájeno", "Probíhá"):
            kurzor.execute("SELECT ID, Název, Popis, Stav FROM ukoly WHERE Stav = %s", (filtr_stav,))
        else:
            kurzor.execute("SELECT ID, Název, Popis, Stav FROM ukoly")

        vysledky = kurzor.fetchall()

        if not vysledky:
            print("Seznam je prázdný.")
        else:
            for ukol in vysledky:
                stav = "Probíhá" if ukol[3] else "Nezahájeno"
                print(f"ID: {ukol[0]}, Název: {ukol[1]}, Popis: {ukol[2]}, Stav: {ukol[3]}")

    except mysql.connector.Error as err:
        print(f"Chyba při připojení nebo dotazu: {err}")
    finally:
        if conn.is_connected():
            kurzor.close()
            conn.close()

def aktualizovat_ukol():
    """Tato funkce umožní změnu stavu úkolu."""
    conn = pripojeni_db()
    kurzor = conn.cursor()
    try:
        while True:
            try:
                ID_ukolu = int(input("Zadej ID úkolu, jehož stav chceš změnit: "))
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
        
        kurzor.execute("UPDATE ukoly SET stav = %s WHERE ID = %s", (novy_stav, ID_ukolu))
        conn.commit()
        print("Stav úkolu byl úspěšně aktualizován.")
    except Exception as e:
        print("Chyba při aktualizaci stavu úkolu:", e)
    finally:
        kurzor.close()
        conn.close()


def odstranit_ukol():
    """Tato funkce umožní odstranit úkoly ze seznamu."""
    conn = pripojeni_db()
    kurzor = conn.cursor()
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
                Název = ukoly[cislo - 1][1]
                kurzor.execute("DELETE FROM ukoly WHERE ID = %s", (id_odstranit,))
                conn.commit()
                print(f"Úkol '{Název}' byl odstraněn.")
                break 
            else:
                print("Zadaný úkol neexistuje. Zkuste to znovu.")
        except ValueError:
            print("Zadejte platné číslo.")
        except Exception as e:
            print("Chyba při odstraňování úkolu:", e)
            break

    kurzor.close()
    conn.close()
    print("Úkol odstraněn.")
      
      


def hlavni_menu():
    """Tato funkce zobrazí Hlavní menu."""
    while True:
       print("\nHlavní nabídka:")
       print("1. Přidat úkol \n2. Zobrazit úkoly \n3. Aktualizovat úkol \n4. Odtsranit úkol \n5. Ukončit program")
       ukol_moznost=input("Vyberte možnost (1-5): ")
       if ukol_moznost == "1":
          pridat_ukol()  
       elif ukol_moznost == "2":
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