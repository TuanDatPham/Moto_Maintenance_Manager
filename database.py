import sqlite3

class Databaze:
    def __init__(self):
        self.conn = sqlite3.connect("motorky.db")
        self.cursor = self.conn.cursor()
        self.vytvor_tabulky()

    def vytvor_tabulky(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Motorky (ID INTEGER PRIMARY KEY AUTOINCREMENT, Znacka TEXT, Model TEXT, Najezd INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Servis (ID INTEGER PRIMARY KEY AUTOINCREMENT, MotorkaID INTEGER, Nazev TEXT, IntervalKm INTEGER, PosledniServisKm INTEGER)")
        self.conn.commit()

    def uloz_motorku(self, znacka, model, km):
        self.cursor.execute("INSERT INTO Motorky (Znacka, Model, Najezd) VALUES (?, ?, ?)", (znacka, model, km))
        nove_id = self.cursor.lastrowid
        
        ukony = [
            ("Motorový olej", 6000), 
            ("Brzdová kapalina", 12000),
            ("Vzduchový filtr", 12000), 
            ("Řetězová sada", 20000),
            ("Pneu přední", 10000), 
            ("Pneu zadní", 8000)
        ]
        for nazev, interval in ukony:
            self.cursor.execute("INSERT INTO Servis (MotorkaID, Nazev, IntervalKm, PosledniServisKm) VALUES (?,?,?,?)", (nove_id, nazev, interval, km))
        
        self.conn.commit()

    def dej_vsechny_motorky(self):
        self.cursor.execute("SELECT ID, Znacka, Model, Najezd FROM Motorky")
        return self.cursor.fetchall()

    def dej_servis_pro_id(self, moto_id):
        self.cursor.execute("SELECT Nazev, IntervalKm, PosledniServisKm FROM Servis WHERE MotorkaID=?", (moto_id,))
        return self.cursor.fetchall()

    def proved_servis(self, moto_id, nazev_ukonu, aktualni_km):
        self.cursor.execute("UPDATE Servis SET PosledniServisKm = ? WHERE MotorkaID = ? AND Nazev = ?", (aktualni_km, moto_id, nazev_ukonu))
        self.conn.commit()

    def smaz_motorku(self, moto_id):
        self.cursor.execute("DELETE FROM Motorky WHERE ID=?", (moto_id,))
        self.conn.commit()

    def aktualizuj_tachometr(self, moto_id, nove_km):
        self.cursor.execute("UPDATE Motorky SET Najezd=? WHERE ID=?", (nove_km, moto_id))
        self.conn.commit()

    def zavrit(self):
        self.conn.close()