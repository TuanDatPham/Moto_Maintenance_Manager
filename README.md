# Moto-Maintenance-Manager
Konzolová aplikace v C++ pro správu udržby motocyklů. V aplikaci se může evidovat více strojů, sledovat jejich nájezd a automaticky upozorňuje na blížíce se nebo 
končíci termín na servis.
Data se ukládají v lokální databázi SQLite takže se nesmažou po vypnutí.
________________________________________________________________________________________________
🚀 Hlavní funkce
Evidence motocyklů: Přidávání libovolného počtu motorek (Značka, Model, Nájezd).

Servisní plán: Automatické generování servisních prvků pro motorku (Olej, Brzdová kapalina, Řetězová sada, Pneu, atd.).

Chytrá upozornění:

[!] Nutný servis (zbývá méně než 500 km).

[!!!] Přetažený servis (zobrazí o kolik km).

OK V pořádku.

Databáze: Veškerá data se ukládají do souboru motorky.db.
________________________________________________________________________________________________
📂 Struktura souborů
main.cpp - Hlavní zdrojový kód aplikace.

sqlite3.c - Zdrojový kód SQLite (Amalgamation).

sqlite3.h - Hlavičkový soubor SQLite.

motorky.db - Databázový soubor (vytvoří se automaticky po prvním spuštění).

README.md - Dokumentace projektu.
________________________________________________________________________________________________
🗄️ Správa databáze
Soubor motorky.db je binární SQL databáze. Pro ruční prohlížení nebo úpravu dat doporučujeme použít program SQLite viewer přímo ve VS.
