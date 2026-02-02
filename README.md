Moto-Maintenance-Manager

Aplikace slouží jako digitální servisní knížka. Umožňuje evidovat více motocyklů najednou a pro každý z nich automaticky generuje základní servisní plán (olej, brzdová kapalina, řetězovka, pneu).

Stačí pouze aktualizovat stav tachometru a program sám barevně zvýrazní, co je potřeba udělat, nebo kolik kilometrů zbývá do další výměny.

Hlavní funkce
Evidenc motocyklů: Přidávání nových strojů (Značka, Model, Nájezd) a jejich mazání.

Automatický servisní plán: Po přidání motorky se automaticky vytvoří sledované úkony s přednastavenými intervaly.

Aktualizace tachometru: Možnost zadat nový stav tachometru nebo jen přičíst ujeté kilometry (např. +200 km po vyjížďce).

Hromadný servis: Možnost označit více úkonů najednou a potvrdit jejich provedení. Interval se automaticky resetuje podle aktuálního nájezdu.

Tisk servisní knížky: Export aktuálního stavu a historie do textového souboru ve složce "Servisni_knizky".

Jak aplikaci spustit
1. Ujistěte se, že máte ve složce všechny tři soubory:

main.py

gui.py

database.py

2. Spusťte soubor main.py.

Aplikace si při prvním spuštění sama vytvoří databázový soubor motorky.db.

Struktura projektu
main.py – Hlavní spouštěcí soubor aplikace.

gui.py – Obsahuje veškerou grafiku, okna, tlačítka a logiku uživatelského rozhraní.

database.py – Stará se o komunikaci s databází (SQLite), ukládání a načítání dat.

Servisni_knizky/ – Složka, která se vytvoří automaticky při prvním exportu servisní knížky.

Poznámka
Data jsou ukládána lokálně do souboru motorky.db. Pokud tento soubor smažete, přijdete o všechna uložená data.
