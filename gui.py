import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from database import Databaze

class MotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moto Maintenance Manager 🏍")
        self.root.geometry("800x600")

        self.db = Databaze()

        nadpis = tk.Label(root, text="Moje Garáž", font=("Comic Sans MS", 18 , "bold"))
        nadpis.pack(pady=10)

        self.frame_vstupy = tk.Frame(self.root)
        self.frame_vstupy.pack(pady=10)

        tk.Label(self.frame_vstupy, text="Značka:").grid(row=0, column=0, padx=5)
        self.vstup_znacka = tk.Entry(self.frame_vstupy)
        self.vstup_znacka.grid(row=0, column=1, padx=5)
        
        tk.Label(self.frame_vstupy, text="Model:").grid(row=0, column=2, padx=5)
        self.vstup_model = tk.Entry(self.frame_vstupy)
        self.vstup_model.grid(row=0, column=3, padx=5)

        tk.Label(self.frame_vstupy, text="Nájezd:").grid(row=0, column=4, padx=5)
        self.vstup_najezd = tk.Entry(self.frame_vstupy)
        self.vstup_najezd.grid(row=0, column=5, padx=5)

        tk.Button(self.frame_vstupy, text="Přidat Motorku", bg="#4CAF50", fg="white",
                  command=self.pridat_motorku).grid(row=0, column=6, padx=15)

        columns = ("poradi", "znacka", "model", "najezd")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=10)

        self.tree.heading("poradi", text="#") 
        self.tree.heading("znacka", text="Značka")
        self.tree.heading("model", text="Model")
        self.tree.heading("najezd", text="Najeto (km)")

        self.tree.column("poradi", width=30, anchor="center")
        self.tree.column("znacka", width=150, anchor="center")
        self.tree.column("model", width=100, anchor="center")
        self.tree.column("najezd", width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tree.bind("<Double-1>", self.otevrit_detail)

        frame_akce = tk.Frame(root)
        frame_akce.pack(pady=10)

        tk.Button(frame_akce, text="✏️ Aktualizovat tachometr", command=self.zmenit_km).pack(side="left", padx=10)
        tk.Button(frame_akce, text="🗑️ Smazat motorku", bg="#ffcccc", command=self.smazat_motorku).pack(side="left", padx=10)

        self.nacist_data()

    def nacist_data(self):
        for polozka in self.tree.get_children():
            self.tree.delete(polozka)
        
        radky = self.db.dej_vsechny_motorky()
        
        for i, radek in enumerate(radky, start=1):
            realne_id = radek[0]
            
            zobrazene_hodnoty = (i, radek[1], radek[2], radek[3])
            
            self.tree.insert("", "end", iid=realne_id, values=zobrazene_hodnoty)
    
    def pridat_motorku(self):
        znacka = self.vstup_znacka.get()
        model = self.vstup_model.get()
        km_text = self.vstup_najezd.get()

        if not znacka or not model or not km_text:
            messagebox.showwarning("Pozor!", "Vyplň prosím všechna pole")
            return

        try:
            km = int(km_text)
            self.db.uloz_motorku(znacka, model, km)
            self.nacist_data()
            
            self.vstup_znacka.delete(0, 'end')
            self.vstup_model.delete(0, 'end')
            self.vstup_najezd.delete(0, 'end')
        except ValueError:
            messagebox.showwarning("Chyba!", "Nájezd musí být číslo")

    def zmenit_km(self):
        vyber = self.tree.selection()
        if not vyber:
            messagebox.showwarning("Chyba", "Vyber motorku v tabulce!")
            return
        
        moto_id = vyber[0]
        item = self.tree.item(vyber)['values']
        stare_km = item[3]

        vstup = simpledialog.askstring(
            "Tachometr", 
            f"Aktuální stav: {stare_km} km\n\n"
            "Možnosti:\n"
            "1. Zadej nový stav (např. 16500)\n"
            "2. Zadej kolik jsi ujel (např. +250)"
        )

        if vstup:
            try:
                vstup = vstup.strip()
                nove_km = 0
                if vstup.startswith("+"):
                    pridavek = int(vstup.replace("+", ""))
                    nove_km = stare_km + pridavek
                else:
                    nove_km = int(vstup)

                if nove_km < stare_km:
                    messagebox.showwarning("Chyba", f"Nemůžeš snížit kilometry!\nStaré: {stare_km}, Nové: {nove_km}")
                else:
                    self.db.aktualizuj_tachometr(moto_id, nove_km)
                    self.nacist_data()
                    messagebox.showinfo("Uloženo", f"Tachometr aktualizován na {nove_km} km.")

            except ValueError:
                messagebox.showerror("Chyba", "Musíš zadat číslo!")

    def smazat_motorku(self):
        vyber = self.tree.selection()
        if not vyber:
            messagebox.showwarning("Chyba", "Vyber motorku!")
            return

        moto_id = vyber[0]
        item = self.tree.item(vyber)['values']
        nazev = f"{item[1]} {item[2]}"

        odpoved = messagebox.askyesno("Potvrdit smazání", f"Opravdu chceš smazat motorku {nazev}?")
        
        if odpoved:
            self.db.smaz_motorku(moto_id)
            self.nacist_data()

    def otevrit_detail(self, event):
        vybrany = self.tree.selection()
        if not vybrany: return
        
        moto_id = vybrany[0]
        hodnoty = self.tree.item(vybrany)['values']
        moto_km = hodnoty[3]
        nazev = f"{hodnoty[1]} {hodnoty[2]}"

        okno = tk.Toplevel(self.root)
        okno.title(f"Servis: {nazev}")
        okno.geometry("700x550")

        tk.Label(okno, text=f"Servisní plán: {nazev}", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(okno, text=f"Aktuální stav tachometru: {moto_km} km", fg="gray").pack()

        cols = ("ukon", "interval", "posledni", "stav")
        ts = ttk.Treeview(okno, columns=cols, show="headings", height=10)
        for c in cols: ts.heading(c, text=c)
        
        ts.column("ukon", width=150)
        ts.column("interval", width=80, anchor="center")
        ts.column("posledni", width=100, anchor="center")
        ts.column("stav", width=200)

        ts.tag_configure("ok", background="#dfffdf")
        ts.tag_configure("pozor", background="#ffcccc")
        
        ts.pack(fill="both", expand=True, padx=10, pady=5)

        def nacti_servis_tabulku():
            for row in ts.get_children():
                ts.delete(row)
            
            servisy = self.db.dej_servis_pro_id(moto_id)
            for s in servisy:
                nazev_ukonu, interval, posledni = s
                zbyva = (posledni + interval) - moto_km
                
                stav_text = f"OK (zbývá {zbyva} km)"
                barva = "ok"
                if zbyva < 0:
                    stav_text = f"PŘETAŽENO O {-zbyva} km!"
                    barva = "pozor"
                
                ts.insert("", "end", values=(nazev_ukonu, interval, posledni, stav_text), tags=(barva,))

        def oznacit_hotovo():
            vybrane_radky = ts.selection()
            if not vybrane_radky:
                messagebox.showwarning("Chyba", "Vyber alespoň jeden servis!")
                return
            
            pocet = 0
            for radek_id in vybrane_radky:
                hodnoty_radku = ts.item(radek_id)['values']
                nazev_ukonu = hodnoty_radku[0]
                self.db.proved_servis(moto_id, nazev_ukonu, moto_km)
                pocet += 1
            
            nacti_servis_tabulku()
            messagebox.showinfo("Hotovo", f"Úspěšně zaznamenáno {pocet} úkonů.")

        def exportovat_knizku():
            slozka = "Servisni_knizky"

            if not os.path.exists(slozka):
                os.makedirs(slozka)

            nazev_souboru = f"Servisni_knizka_{hodnoty[1]}_{hodnoty[2]}.txt".replace(" ", "_")
            cesta_k_souboru = os.path.join(slozka, nazev_souboru)
            
            servisy = self.db.dej_servis_pro_id(moto_id)

            try:
                with open(cesta_k_souboru, "w", encoding="utf-8") as f:
                    f.write("="*50 + "\n")
                    f.write(f"SERVISNÍ KNÍŽKA: {nazev}\n")
                    f.write(f"Aktuální stav: {moto_km} km\n")
                    f.write("="*50 + "\n\n")
                    f.write(f"{'ÚKON':<25} | {'INTERVAL':<10} | {'POSLEDNÍ':<10} | {'DALŠÍ SERVIS':<15}\n")
                    f.write("-" * 75 + "\n")
                    
                    for s in servisy:
                        nazev_ukonu, interval, posledni = s
                        dalsi = posledni + interval
                        f.write(f"{nazev_ukonu:<25} | {interval:<10} | {posledni:<10} | {dalsi:<15}\n")
                    
                    f.write("\n" + "-" * 75 + "\n")
                    f.write("Vygenerováno aplikací Moto Maintenance Manager 🏍\n")
                
                os.startfile(cesta_k_souboru)
                
            except Exception as e:
                messagebox.showerror("Chyba", f"Nepodařilo se vytvořit soubor:\n{e}")

        frame_btn = tk.Frame(okno)
        frame_btn.pack(pady=10)

        tk.Button(frame_btn, text="✅ Provést servis", bg="#4CAF50", fg="white", command=oznacit_hotovo).pack(side="left", padx=5)
        tk.Button(frame_btn, text="🖨️ Tisk servisní knížky", command=exportovat_knizku).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Zavřít", command=okno.destroy).pack(side="left", padx=5)

        nacti_servis_tabulku()

    def __del__(self):
        self.db.zavrit()