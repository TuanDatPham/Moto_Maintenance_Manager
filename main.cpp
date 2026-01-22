#include <iostream>
#include <string>
#include <vector>
#include "sqlite3.h"

using namespace std;

void sqlExec(sqlite3* db, const string& sql) {
    char* err;
    if (sqlite3_exec(db, sql.c_str(), 0, 0, &err) != SQLITE_OK) {
        cerr << "SQL Chyba: " << err << endl;
        sqlite3_free(err);
    }
}

class ServisniUkon {
public:
    int id;          
    int motorkaId;     
    string nazev;       
    int intervalKm;     
    int posledniServis; 

    ServisniUkon(int id_db, int moto_id, string n, int interval, int posledni) 
        : id(id_db), motorkaId(moto_id), nazev(n), intervalKm(interval), posledniServis(posledni) {}

    bool jePotreba(int aktualniNajezd, int varovaniPredem = 500) const {
        int dalsiServisV = posledniServis + intervalKm;
        int zbyva = dalsiServisV - aktualniNajezd;
        return zbyva <= varovaniPredem;
    }

    string dejStatus(int aktualniNajezd) const {
        int dalsiServisV = posledniServis + intervalKm;
        int zbyva = dalsiServisV - aktualniNajezd;

        if (zbyva < 0) return " [!!!] PRETAHENO O " + to_string(-zbyva) + " km!";
        if (zbyva <= 500) return " [!] Nutny servis za " + to_string(zbyva) + " km";
        return " OK (zbyva " + to_string(zbyva) + " km)";
    }
};

class Motorka {
public:
    int id;
    string znacka;
    string model;
    int aktualniNajezd;
    vector<ServisniUkon> servisniHistorie;
    sqlite3* dbRef;

    Motorka(int id_db, string z, string m, int najezd, sqlite3* db) 
        : id(id_db), znacka(z), model(m), aktualniNajezd(najezd), dbRef(db) {
        nactiServisyZDB();
    }

    void nactiServisyZDB() {
        servisniHistorie.clear();
        string sql = "SELECT ID, MotorkaID, Nazev, IntervalKm, PosledniServisKm FROM Servis WHERE MotorkaID = " + to_string(id) + ";";
        sqlite3_stmt* stmt;
        
        if (sqlite3_prepare_v2(dbRef, sql.c_str(), -1, &stmt, 0) == SQLITE_OK) {
            while (sqlite3_step(stmt) == SQLITE_ROW) {
                int sId = sqlite3_column_int(stmt, 0);
                int mId = sqlite3_column_int(stmt, 1);
                string nazev = (const char*)sqlite3_column_text(stmt, 2);
                int interval = sqlite3_column_int(stmt, 3);
                int posledni = sqlite3_column_int(stmt, 4);
                
                servisniHistorie.emplace_back(sId, mId, nazev, interval, posledni);
            }
        }
        sqlite3_finalize(stmt);
    }

    void pridejUkonDoDB(string nazev, int interval, int posledni) {
        string sql = "INSERT INTO Servis (MotorkaID, Nazev, IntervalKm, PosledniServisKm) VALUES (" +
                     to_string(id) + ", '" + nazev + "', " + to_string(interval) + ", " + to_string(posledni) + ");";
        sqlExec(dbRef, sql);
        nactiServisyZDB();
    }

    void provedServis(int indexUkonu) {
        if (indexUkonu >= 0 && indexUkonu < servisniHistorie.size()) {
            ServisniUkon& ukon = servisniHistorie[indexUkonu];
            
            // Update v DB
            string sql = "UPDATE Servis SET PosledniServisKm = " + to_string(aktualniNajezd) + " WHERE ID = " + to_string(ukon.id) + ";";
            sqlExec(dbRef, sql);

            // Update v pameti
            ukon.posledniServis = aktualniNajezd;
            cout << ">>> Servis '" << ukon.nazev << "' byl zaznamenan a ulozen do DB." << endl;
        }
    }

    void vypisStav() const {
        cout << "\n========================================" << endl;
        cout << " MOTORKA: " << znacka << " " << model << " (Najeto: " << aktualniNajezd << " km)" << endl;
        cout << "========================================" << endl;
        
        bool nutnaPozornost = false;
        for (size_t i = 0; i < servisniHistorie.size(); i++) {
            cout << i + 1 << ". " << servisniHistorie[i].nazev 
                 << ": " << servisniHistorie[i].dejStatus(aktualniNajezd) << endl;
            if (servisniHistorie[i].jePotreba(aktualniNajezd)) nutnaPozornost = true;
        }
        if (nutnaPozornost) cout << "\nPOZOR: Tato motorka vyzaduje udrzbu!" << endl;
    }
};

class GarazManager {
    sqlite3* db;
    vector<Motorka> garaz;

public:
    GarazManager() {
        if (sqlite3_open("motorky.db", &db)) {
            cerr << "Chyba DB: " << sqlite3_errmsg(db) << endl;
            exit(1);
        }
        string sql = 
            "CREATE TABLE IF NOT EXISTS Motorky ("
            "ID INTEGER PRIMARY KEY AUTOINCREMENT, Znacka TEXT, Model TEXT, Najezd INTEGER);"
            "CREATE TABLE IF NOT EXISTS Servis ("
            "ID INTEGER PRIMARY KEY AUTOINCREMENT, MotorkaID INTEGER, Nazev TEXT, IntervalKm INTEGER, PosledniServisKm INTEGER,"
            "FOREIGN KEY(MotorkaID) REFERENCES Motorky(ID) ON DELETE CASCADE);";
        sqlExec(db, sql);
    }

    ~GarazManager() {
        sqlite3_close(db);
    }

    void obnovitDataZDB() {
        garaz.clear();
        sqlite3_stmt* stmt;
        string sql = "SELECT ID, Znacka, Model, Najezd FROM Motorky;";

        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, 0) == SQLITE_OK) {
            while (sqlite3_step(stmt) == SQLITE_ROW) {
                int id = sqlite3_column_int(stmt, 0);
                string znacka = (const char*)sqlite3_column_text(stmt, 1);
                string model = (const char*)sqlite3_column_text(stmt, 2);
                int km = sqlite3_column_int(stmt, 3);
                
                garaz.emplace_back(id, znacka, model, km, db);
            }
        }
        sqlite3_finalize(stmt);
    }

    void pridatMotorku() {
        string znacka, model;
        int km;

        cout << "\n--- PRIDANI NOVE MOTORKY ---" << endl;
        cout << "Zadej znacku: "; cin >> znacka;
        cout << "Zadej model: "; cin >> model;
        cout << "Zadej aktualni najezd (km): "; cin >> km;

        string sql = "INSERT INTO Motorky (Znacka, Model, Najezd) VALUES ('" + znacka + "', '" + model + "', " + to_string(km) + ");";
        sqlExec(db, sql);
        
        int noveId = (int)sqlite3_last_insert_rowid(db);

        Motorka m(noveId, znacka, model, km, db);
        m.pridejUkonDoDB("Motorovy olej + filtr", 6000, km);
        m.pridejUkonDoDB("Brzdova kapalina", 12000, km);
        m.pridejUkonDoDB("Chladici kapalina", 24000, km);
        m.pridejUkonDoDB("Vzduchovy filtr", 12000, km);
        m.pridejUkonDoDB("Retezova sada", 20000, km);
        m.pridejUkonDoDB("Predni pneu", 10000, km);
        m.pridejUkonDoDB("Zadni pneu", 8000, km);

        cout << "Motorka ulozena do databaze!" << endl;
    }

    void vypisVsechnyMotorky() {
        obnovitDataZDB();
        if (garaz.empty()) {
            cout << "\nGaraz je prazdna." << endl;
            return;
        }
        for (size_t i = 0; i < garaz.size(); i++) {
            cout << "\n[" << i + 1 << "] " << garaz[i].znacka << " " << garaz[i].model << endl;
        }
    }

    void detailMotorky() {
        vypisVsechnyMotorky();
        if (garaz.empty()) return;

        cout << "\nVyber cislo motorky pro detail (0 pro navrat): ";
        int volba;
        cin >> volba;

        if (volba > 0 && volba <= garaz.size()) {
            Motorka& m = garaz[volba - 1];
            
            while (true) {
                m.nactiServisyZDB();
                m.vypisStav();
                cout << "\nAKCE:" << endl;
                cout << "1. Aktualizovat najezd motorky" << endl;
                cout << "2. Provest servis" << endl;
                cout << "3. Odstranit motorku" << endl;
                cout << "0. Zpet" << endl;
                cout << "Volba: ";
                
                int akce;
                cin >> akce;

                if (akce == 0) break;
                else if (akce == 1) {
                    cout << "Zadej novy stav tachometru: ";
                    int noveKm; cin >> noveKm;
                    if (noveKm >= m.aktualniNajezd) {
                        m.aktualniNajezd = noveKm;
                        string sql = "UPDATE Motorky SET Najezd = " + to_string(noveKm) + " WHERE ID = " + to_string(m.id) + ";";
                        sqlExec(db, sql);
                        cout << "Najezd aktualizovan a ulozen." << endl;
                    } else cout << "Chyba: Km nelze snizovat!" << endl;
                }
                else if (akce == 2){

                }
                else if (akce == 3) {
                    cout << "Zadej cislo ukonu: ";
                    int idUkonu; cin >> idUkonu;
                    m.provedServis(idUkonu - 1);
                }
                else if (akce == 4) {
                    string sqlServis = "DELETE FROM Servis WHERE MotorkaID = " + to_string(m.id) + ";";
                    sqlExec(db, sqlServis);
                    string sqlMoto = "DELETE FROM Motorky WHERE ID = " + to_string(m.id) + ";";
                    sqlExec(db, sqlMoto);
                    
                    cout << "Motorka odstranena z databaze." << endl;
                    break; 
                }
            }
        }
    }
};

int main() {
    GarazManager manager;
    int volba = 0;

    while (true) {
        cout << "\n=== MOTO MANAGER (SQLITE VERZE) ===" << endl;
        cout << "1. Pridat motorku" << endl;
        cout << "2. Vybrat motorku (Detail / Servis / Smazat)" << endl;
        cout << "0. Ukoncit" << endl;
        cout << "Volba: ";
        cin >> volba;
        if (cin.fail()) { 
            cin.clear();
            cin.ignore(9999, '\n');
            continue;
        }

        switch (volba) {
            case 1: manager.pridatMotorku(); break;
            case 2: manager.detailMotorky(); break;
            case 0: cout << "Ukoncuji..." << endl; return 0;
            default: cout << "Neplatna volba!" << endl;
        }
    }
}