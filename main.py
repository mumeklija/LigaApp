import tkinter as tk
from tkinter import messagebox, ttk, font, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import * #sve za grafiku
import pickle #za sejvanje fajlova
from datetime import datetime, timedelta
import random 

#REPORTLAB ZA PDF GENERIRANJE

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas




class LigaAplikacija:
    def __init__(self, root):
        self.root = root
        self.root.title("FootyTracker")
        self.root.iconbitmap("ikonica.ico")
        self.root.state("zoomed")
        self.root.configure(bg="#9fbd9d")

        self.root.grid_propagate(False)
        

        self.klubovi = []
        self.praznici = []  
        self.statistika = {}
        self.gumbovi_utakmica = {}

        self.kalendar = []
        self.datumi = []
        self.trenutno_kolo = 0
        self.odigrano_u_kolu = set()
        self.rezultati_utakmica = {}
        self.pocetni_datum_lige = None 

        self.create_widgets()
        self.root.configure(bg="#9fbd9d")

        messagebox.showinfo("Dobrodošli", "Dobrodošli u FootyTracker! Počnite s unošenjem klubova ili učitavanjem postojeće lige.")

    # ---------------- UI ----------------

    def create_widgets(self):
        style = tb.Style()
        style.configure("Custom.TFrame", background="#9fbd9d")

        # Gornji dio: Unos kluba i gumbovi za save itd 
        self.entry_klub = tb.Entry(self.root, width=40)
        self.entry_klub.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        self.entry_klub.bind("<Return>", lambda event: self.dodaj_klub())
        self.entry_klub.grid_propagate(False)

        self.btn_dodaj_klub = tb.Button(self.root, text="Dodaj klub", command=self.dodaj_klub, bootstyle="success", width=15)
        self.btn_dodaj_klub.grid(row=0, column=0, padx=200, pady=10, sticky="w")
        self.btn_dodaj_klub.grid_propagate(False)  

        self.btn_pocni_ligu = tb.Button(self.root, text="Počni ligu", command=self.pocni_ligu, bootstyle="primary", width=30)
        self.btn_pocni_ligu.grid(row=0, column=1, padx=10, pady=10)
        self.btn_pocni_ligu.grid_propagate(False)

        self.btn_undo_kolo = tb.Button(self.root, text="Undo Kolo", command=self.undo_kolo, bootstyle="warning", width=15)
        self.btn_undo_kolo.grid(row=0, column=2, padx=10, pady=10)
        self.btn_undo_kolo.grid_propagate(False)

        self.btn_spremi_stanje = tb.Button(self.root, text="Spremi stanje", command=self.spremi_stanje, bootstyle="success", width=15)
        self.btn_spremi_stanje.grid(row=0, column=5, padx=10, pady=10)
        self.btn_spremi_stanje.grid_propagate(False)

        self.btn_ucitaj_stanje = tb.Button(self.root, text="Učitaj stanje", command=self.ucitaj_stanje, bootstyle="info", width=15)
        self.btn_ucitaj_stanje.grid(row=0, column=6, padx=5, pady=10)
        self.btn_ucitaj_stanje.grid_propagate(False)

        self.btn_izvezi_pdf = tb.Button(self.root, text="Izvezi raspored utakmica u PDF", command=self.izvezi_raspored_u_pdf, bootstyle="danger", width=30)
        self.btn_izvezi_pdf.grid(row=0, column=3, padx=10, pady=10)
        self.btn_izvezi_pdf.grid_propagate(False)

        self.btn_izvezi_tablicu_pdf = tb.Button(self.root, text="Izvezi tablicu poretka u PDF", command=self.izvezi_tablicu_u_pdf, bootstyle="dark", width=30)
        self.btn_izvezi_tablicu_pdf.grid(row=0, column=4, padx=10, pady=10)
        self.btn_izvezi_tablicu_pdf.grid_propagate(False)

        # Srednji dio: Klubovi i utakmice
        self.lbl_klubovi = tb.Label(self.root, text="Klubovi:", background="#9fbd9d", font=("Helvetica", 14, "bold"))
        self.lbl_klubovi.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.klub_frame_container = tb.Frame(self.root, height=500, width=300)
        self.klub_frame_container.grid(row=2, column=0, padx=10, pady=5, sticky="nsw")
        self.klub_frame_container.grid_propagate(False)
        self.klub_frame = self.create_scrollable_frame(self.klub_frame_container)

        self.lbl_utakmica = tb.Label(self.root, text="Unos utakmice", background="#9fbd9d", font=("Helvetica", 14, "bold"))
        self.lbl_utakmica.grid(row=1, column=1, columnspan=1, pady=5)

        self.utakmica_frame_container = tb.Frame(self.root, height=300, width=350)
        self.utakmica_frame_container.grid(row=2, column=1, columnspan=1, padx=10, pady=5, sticky="ns")
        self.utakmica_frame_container.grid_propagate(False)
        self.utakmica_frame = self.create_scrollable_frame(self.utakmica_frame_container)

        # Donji dio: Unos rezultata
        self.entry_gol1 = tb.Entry(self.root, width=10)
        self.entry_gol1.grid(row=3, column=1, padx=20, pady=10)

        self.lbl_goldomacina = tb.Label(self.root, text="Golovi domaćina", background="#9fbd9d", font=("Helvetica", 12, "bold"))
        self.lbl_goldomacina.grid(row=3, column=1, columnspan=2, padx=0, pady=5, sticky="w")




        self.entry_gol2 = tb.Entry(self.root, width=10)
        self.entry_gol2.grid(row=4, column=1, padx=0, pady=10)

        self.lbl_golgosta = tb.Label(self.root, text="Golovi gosta", background="#9fbd9d", font=("Helvetica", 12, "bold"))
        self.lbl_golgosta.grid(row=4, column=1, columnspan=2, padx=0, pady=5, sticky="w")



        self.btn_spremi = tb.Button(self.root, text="Spremi rezultat", command=self.spremi_rezultat, bootstyle="info", width=20)
        self.btn_spremi.grid(row=5, column=1, columnspan=1, padx=0, pady=10)

        # Okvir za prikaz razdoblja pauze
        self.pauze_frame = tb.Frame(self.root, style="Custom.TFrame", width=200, height=150)
        self.pauze_frame.grid(row=3, column=4, padx=10, pady=10, sticky="nsew")
        self.pauze_frame.grid_propagate(False)

        self.lbl_pauze = tb.Label(self.pauze_frame, text="Razdoblja pauze:", background="#9fbd9d", font=("Helvetica", 14, "bold"))
        self.lbl_pauze.pack(anchor="nw", padx=5, pady=5)

        self.lbl_pauze_lista = []

        # Pod-okvir za dinamički sadržaj pauza
        self.pauze_sadrzaj_frame = tb.Frame(self.pauze_frame, style="Custom.TFrame")
        self.pauze_sadrzaj_frame.pack(fill="both", expand=True, padx=5, pady=5)



        # Okvir za prikaz rezultata tekućeg kola
        self.rezultati_frame = tb.Frame(self.root, style="Custom.TFrame", width=200, height=200)
        self.rezultati_frame.grid(row=2, column=4, padx=10, pady=10, sticky="ns")
        self.rezultati_frame.grid_propagate(False)

        self.lbl_rezultati = tb.Label(self.rezultati_frame, text="Rezultati tekućeg kola:", background="#9fbd9d", font=("Helvetica", 14, "bold"), wraplength=200)
        self.lbl_rezultati.pack(anchor="nw", padx=5, pady=5)
        self.lbl_rezultati_lista = []

        # Pod-okvir za dinamički sadržaj rezultata
        self.rezultati_sadrzaj_frame = tb.Frame(self.rezultati_frame, style="Custom.TFrame")
        self.rezultati_sadrzaj_frame.pack(fill="both", expand=True, padx=5, pady=5)


        # Progress bar za prelazak na iduće kolo
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=250, mode="determinate")
        self.progress_bar.grid(row=5, column=4, padx=10, pady=10, sticky="w")
        self.progress_bar.grid_remove()  # Sakrij progress bar dok nije potreban




        # Scrollable frame - tablica za poredak
        self.tablica_frame_container = tb.Frame(self.root, height=200, width=500)
        self.tablica_frame_container.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.tablica_frame_container.grid_propagate(False)

        # Treeview za tablicu lige preko ttk
        styletablica = ttk.Style()
        styletablica.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))


        self.tablica = ttk.Treeview(self.tablica_frame_container, columns=("Pozicija", "Klub", "Bodovi", "Zabijeni", "Primljeni", "Gol razlika", "Odigrane Utakmice"), show="headings", height=10)
        self.tablica.heading("Pozicija", text="Pozicija")
        self.tablica.heading("Klub", text="Klub")
        self.tablica.heading("Bodovi", text="Bodovi")
        self.tablica.heading("Zabijeni", text="Zabijeni")
        self.tablica.heading("Primljeni", text="Primljeni")
        self.tablica.heading("Gol razlika", text="Gol razlika")
        self.tablica.heading("Odigrane Utakmice", text="Odigrane utakmice")

        self.tablica.column("Pozicija", width=80, anchor="center")
        self.tablica.column("Klub", width=200, anchor="center")
        self.tablica.column("Bodovi", width=100, anchor="center")
        self.tablica.column("Zabijeni", width=100, anchor="center")
        self.tablica.column("Primljeni", width=100, anchor="center")
        self.tablica.column("Gol razlika", width=100, anchor="center")
        self.tablica.column("Odigrane Utakmice", width=150, anchor="center")
        self.tablica.pack(fill="both", expand=False)


        self.povezi_dvoklik_na_tablicu()




        # Grid konfiguracija za raspodjelu prostora
        self.root.grid_rowconfigure(0, weight=0)  # Gornji dio (unos kluba)
        self.root.grid_rowconfigure(1, weight=0)  # Labele
        self.root.grid_rowconfigure(2, weight=1)  # Srednji dio (klubovi i utakmice)
        self.root.grid_rowconfigure(3, weight=0)  # Unos rezultata
        self.root.grid_rowconfigure(4, weight=0)  # Gumb "Spremi rezultat"
        self.root.grid_rowconfigure(5, weight=0)  # Donji dio (tablica)

        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=0)  
        self.root.grid_columnconfigure(2, weight=0) 
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(4, weight=0)
        self.root.grid_columnconfigure(5, weight=0)
        self.root.grid_columnconfigure(6, weight=0)

        self.root.grid_columnconfigure(4, minsize=250, weight=0)  # Fiksna širina za stupac 4





    # ---------------- FUNKCIJE ----------------


            #funkcija za gumb pocni ligu



    def pocni_ligu(self):
        if len(self.klubovi) < 2:
            messagebox.showerror("Greška", "Potrebna su barem 2 kluba za pokretanje lige.")
            return
        
        if len(self.klubovi) % 2 != 0:
            messagebox.showerror("Greška", "Ne može biti neparan broj klubova.")
            return

        izbor = messagebox.askyesno("Raspored utakmica", "Želite li ručno unijeti raspored utakmica? Ukoliko ne, program će sam generirati utakmice za Vas.")
        if izbor:
            self.unesi_raspored()
        else:
            pocetni_datum = simpledialog.askstring("Početni datum lige", "Unesite početni datum lige (dd.mm.yyyy):")
            try:
                self.pocetni_datum_lige = datetime.strptime(pocetni_datum, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Greška", "Neispravan format datuma. Koristite format dd.mm.yyyy.")
                return

            samo_vikendom = messagebox.askyesno("Raspored datuma", "Želite li da se utakmice igraju samo vikendom?")
            
            
            self.unesi_praznike()

            self.kalendar = self.generiraj_kalendar()
            self.datumi = self.generiraj_datume(len(self.kalendar), samo_vikendom)
            self.trenutno_kolo = 1
            self.prikazi_utakmice()

        self.entry_klub.config(state="disabled")
        self.btn_dodaj_klub.config(state="disabled")
        self.btn_pocni_ligu.config(state="disabled")
        self.izvezi_raspored_u_pdf()





    def prikazi_klubove(self):
        for widget in self.klub_frame.winfo_children():
            widget.destroy()

        for klub in self.klubovi:
            lbl = tb.Label(self.klub_frame, text=klub, font=("Helvetica", 12, "bold"))
            lbl.pack(anchor="w", pady=2)










        #funkcija za prikazanje utakmica, gasi gumbove nakon sto se iskoriste utakmice

    def prikazi_utakmice(self):
        for widget in self.utakmica_frame.winfo_children():
            widget.destroy()
        self.gumbovi_utakmica.clear()

        # Dohvati utakmice i datume za trenutno kolo
        if self.trenutno_kolo > len(self.kalendar):
            return 

        utakmice_kola = self.kalendar[self.trenutno_kolo - 1]
        datumi_kola = self.datumi[self.trenutno_kolo - 1]

        # Prikaz utakmica
        for (domacin, gost), datum in zip(utakmice_kola, datumi_kola):
            gumb_text = f"{datum}: {domacin} - {gost}"
            if (domacin, gost) in self.odigrano_u_kolu:
                gumb = tk.Button(self.utakmica_frame, text=gumb_text, state="disabled", bg="gray")
            else:
                gumb = tk.Button(self.utakmica_frame, text=gumb_text,
                                command=lambda d=domacin, g=gost: self.odaberi_utakmicu(d, g))
            
            
            gumb.pack(fill="x", padx=5, pady=2)
            self.gumbovi_utakmica[(domacin, gost)] = gumb

        # Ažuriraj naslov za trenutno kolo
        self.lbl_utakmica.config(text=f"Unos utakmica – kolo {self.trenutno_kolo}")




    #s desne strane za pauze i rez kola


    def prikazi_pauze(self):
        for widget in self.pauze_sadrzaj_frame.winfo_children():
            widget.destroy()

        # Prikaz razdoblja pauze
        if not self.praznici:
            tekst = "Nema unesenih pauza."
        else:
            tekst = "\n".join([f"{pocetni.strftime('%d.%m.%Y')} - {zavrsni.strftime('%d.%m.%Y')}" for pocetni, zavrsni in self.praznici])

        lbl = tb.Label(self.pauze_sadrzaj_frame, text=tekst, background="#9fbd9d", font=("Helvetica", 12), justify="left")
        lbl.pack(anchor="nw", padx=5, pady=5)
    

    def prikazi_rezultate_kola(self):
        for widget in self.rezultati_sadrzaj_frame.winfo_children():
            widget.destroy()

        # Prikaz rezultata tekućeg kola
        if self.trenutno_kolo > len(self.kalendar):
            tekst = "Nema više kola."
            lbl = tb.Label(self.rezultati_sadrzaj_frame, text=tekst, background="#9fbd9d", font=("Helvetica", 12), justify="left")
            lbl.pack(anchor="nw", padx=5, pady=5)
        else:
            utakmice_kola = self.kalendar[self.trenutno_kolo - 1]
            for domacin, gost in utakmice_kola:
                if (domacin, gost) in self.rezultati_utakmica:
                    gol1, gol2 = self.rezultati_utakmica[(domacin, gost)]
                    rezultat = f"{gol1}:{gol2}"
                else:
                    rezultat = "-:-"

                tekst = f"{domacin} - {gost}: {rezultat}"
                lbl = tb.Label(self.rezultati_sadrzaj_frame, text=tekst, background="#9fbd9d", font=("Helvetica", 12, "bold"), justify="left")
                lbl.pack(anchor="nw", padx=5, pady=5)




    def prikazi_progress_bar(self):
        self.progress_bar.grid() 
        self.progress_bar["value"] = 0

        # Funkcija za ažuriranje progress bara
        def update_progress(value):
            if value <= 100:
                self.progress_bar["value"] = value
                self.root.update_idletasks()
                self.root.after(50, update_progress, value + 10)  # Povećaj vrijednost svakih 10ms
            else:
                self.progress_bar.grid_remove()
                self.prebaci_na_iduce_kolo()

        # Pokreni progress bar
        update_progress(0)





    def prebaci_na_iduce_kolo(self):
        self.trenutno_kolo += 1
        if self.trenutno_kolo <= len(self.kalendar):
            self.odigrano_u_kolu.clear() 
            self.klub1 = None
            self.klub2 = None
            self.prikazi_utakmice() 
            self.prikazi_rezultate_kola() 
            self.prikazi_tablicu() 
        else:
            messagebox.showinfo("Kraj lige", "Sve utakmice su odigrane!")
            self.izvezi_tablicu_u_pdf() 
            izbor = messagebox.askyesno("Nova sezona", "Želite li započeti novu sezonu s istim klubovima?")
            if izbor:
                self.resetiraj_ligu()



    def undo_kolo(self):
        if self.trenutno_kolo <= 0 or self.trenutno_kolo > len(self.kalendar):
            messagebox.showerror("Greška", "Trenutno kolo nije valjano za poništavanje.")
            return

        
        utakmice_kola = self.kalendar[self.trenutno_kolo - 1]

        # Ukloni rezultate utakmica
        for domacin, gost in utakmice_kola:
            if (domacin, gost) in self.rezultati_utakmica:
                gol1, gol2 = self.rezultati_utakmica.pop((domacin, gost))

                # Resetiraj statistiku klubova
                self.statistika[domacin]["zabijeni"] -= gol1
                self.statistika[domacin]["primljeni"] -= gol2
                self.statistika[domacin]["gol_razlika"] = self.statistika[domacin]["zabijeni"] - self.statistika[domacin]["primljeni"]
                self.statistika[domacin]["bodovi"] -= 3 if gol1 > gol2 else (1 if gol1 == gol2 else 0)
                self.statistika[domacin]["odigrane_utakmice"] -= 1

                self.statistika[gost]["zabijeni"] -= gol2
                self.statistika[gost]["primljeni"] -= gol1
                self.statistika[gost]["gol_razlika"] = self.statistika[gost]["zabijeni"] - self.statistika[gost]["primljeni"]
                self.statistika[gost]["bodovi"] -= 3 if gol2 > gol1 else (1 if gol1 == gol2 else 0)
                self.statistika[gost]["odigrane_utakmice"] -= 1

        # Resetiraj odigrane utakmice za trenutno kolo
        self.odigrano_u_kolu.clear()

        # Ažuriraj
        self.prikazi_utakmice()
        self.prikazi_tablicu()
        self.prikazi_rezultate_kola()

        messagebox.showinfo("Undo Kolo", f"Kolo {self.trenutno_kolo} je poništeno. Možete ponovno unijeti rezultate.")



    def resetiraj_ligu(self):
        # Očisti sve
        self.kalendar = []
        self.datumi = []
        self.trenutno_kolo = 0
        self.odigrano_u_kolu.clear()
        self.rezultati_utakmica.clear()
        self.praznici = []

        # Resetiraj statistiku
        for klub in self.klubovi:
            self.statistika[klub] = {"bodovi": 0, "gol_razlika": 0, "zabijeni": 0, "primljeni": 0, "odigrane_utakmice": 0}

        # Generiraj novi raspored utakmica
        pocetni_datum = simpledialog.askstring("Početni datum lige", "Unesite početni datum lige (dd.mm.yyyy):")
        try:
            self.pocetni_datum_lige = datetime.strptime(pocetni_datum, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Greška", "Neispravan format datuma. Koristite format dd.mm.yyyy.")
            return

        samo_vikendom = messagebox.askyesno("Raspored datuma", "Želite li da se utakmice igraju samo vikendom?")
        self.unesi_praznike()
        self.kalendar = self.generiraj_kalendar()
        self.datumi = self.generiraj_datume(len(self.kalendar), samo_vikendom)
        self.trenutno_kolo = 1

        self.prikazi_tablicu()
        self.prikazi_utakmice()
        self.prikazi_rezultate_kola()

        self.btn_pocni_ligu.config(state="disabled")

        self.prikazi_pauze()

        messagebox.showinfo("Nova sezona", "Nova sezona je započela!")
        







    def prikazi_detalje_kluba(self, klub):
        # Kreiraj novi prozor za prikaz statistike kluba
        prozor = tk.Toplevel(self.root)
        prozor.title(f"Statistika kluba: {klub}")
        prozor.geometry("400x500")
        prozor.configure(bg="#9fbd9d")
        prozor.transient(self.root)  # Veže prozor za glavni prozor
        prozor.grab_set()  # Onemogućuje glavni prozor dok je ovaj otvoren

        # Prikaz naziva kluba
        lbl_naziv = tb.Label(prozor, text=f"Klub: {klub}", font=("Helvetica", 16, "bold"), background="#9fbd9d")
        lbl_naziv.pack(anchor="n", pady=10)

        # Prikaz statistike kluba
        statistika = self.statistika[klub]
        tb.Label(prozor, text=f"Pozicija: {self.dohvati_poziciju_kluba(klub)}", font=("Helvetica", 12), background="#9fbd9d").pack(anchor="w", padx=10, pady=5)
        tb.Label(prozor, text=f"Bodovi: {statistika['bodovi']}", font=("Helvetica", 12), background="#9fbd9d").pack(anchor="w", padx=10, pady=5)
        tb.Label(prozor, text=f"Gol razlika: {statistika['gol_razlika']}", font=("Helvetica", 12), background="#9fbd9d").pack(anchor="w", padx=10, pady=5)
        tb.Label(prozor, text=f"Zabijeni golovi: {statistika['zabijeni']}", font=("Helvetica", 12), background="#9fbd9d").pack(anchor="w", padx=10, pady=5)
        tb.Label(prozor, text=f"Primljeni golovi: {statistika['primljeni']}", font=("Helvetica", 12), background="#9fbd9d").pack(anchor="w", padx=10, pady=5)
        tb.Label(prozor, text=f"Odigrane utakmice: {statistika['odigrane_utakmice']}", font=("Helvetica", 12), background="#9fbd9d").pack(anchor="w", padx=10, pady=5)

        # Scrollable frame za povijest utakmica
        lbl_povijest = tb.Label(prozor, text="Povijest utakmica:", font=("Helvetica", 14, "bold"), background="#9fbd9d")
        lbl_povijest.pack(anchor="n", pady=10)

        povijest_frame = self.create_scrollable_frame(prozor)
        for (domacin, gost), rezultat in self.rezultati_utakmica.items():
            if klub in (domacin, gost):
                tekst = f"{domacin} - {gost}: {rezultat[0]}:{rezultat[1]}"
                tb.Label(povijest_frame, text=tekst, font=("Helvetica", 12), background="#FFFFFF").pack(anchor="w", padx=10, pady=2)



    def dohvati_poziciju_kluba(self, klub):
        # Sortiraj klubove prema bodovima i gol-razlici
        sortirano = sorted(self.statistika.items(), key=lambda x: (-x[1]["bodovi"], -x[1]["gol_razlika"]))
        
        # Pronađi poziciju kluba u sortiranoj listi
        for pozicija, (ime_kluba, _) in enumerate(sortirano, start=1):
            if ime_kluba == klub:
                return pozicija
        return "-"
    


    def povezi_dvoklik_na_tablicu(self):
        def on_double_click(event):
            odabrani = self.tablica.focus()
            if odabrani:
                vrijednosti = self.tablica.item(odabrani, "values")
                if vrijednosti:
                    klub = vrijednosti[1]
                    self.prikazi_detalje_kluba(klub)

        self.tablica.bind("<Double-1>", on_double_click)





    #funkcija za odabir utakmice preko gumbova

    def odaberi_utakmicu(self, domacin, gost):
        for (d, g), gumb in self.gumbovi_utakmica.items():
            if (d, g) in self.odigrano_u_kolu:
                gumb.config(bg="gray", state="disabled")  # Iskoristene utakmice postaju sive i neaktivne
            elif (d, g) == (domacin, gost):
                gumb.config(bg="green", state="normal")  # Trenutno odabrana utakmica
            else:
                gumb.config(bg="blue", state="normal")  # Ostale utakmice ostaju plave

        # Postavi trenutno odabrane klubove
        self.klub1 = domacin
        self.klub2 = gost




    #najveca funkcija koja se koristi za unos rezultata, provjerava greske i unosi rezultate u tablicu



    def spremi_rezultat(self):
        try:
            gol1 = int(self.entry_gol1.get())
            gol2 = int(self.entry_gol2.get())
        except ValueError:
            messagebox.showerror("Greška", "Molimo unesite valjane brojeve golova.")
            return

        if gol1 < 0 or gol2 < 0:
            messagebox.showerror("Greška", "Brojevi golova ne mogu biti negativni.")
            return

        if self.klub1 is None or self.klub2 is None:
            messagebox.showerror("Greška", "Nema odabranih klubova za utakmicu.")
            return

        if (self.klub1, self.klub2) in self.odigrano_u_kolu:
            messagebox.showerror("Greška", "Rezultat za ovu utakmicu je već unesen.")
            return

        # Ažuriraj statistiku
        self.statistika[self.klub1]["zabijeni"] += gol1
        self.statistika[self.klub2]["zabijeni"] += gol2
        self.statistika[self.klub1]["primljeni"] += gol2
        self.statistika[self.klub2]["primljeni"] += gol1
        self.statistika[self.klub1]["gol_razlika"] = self.statistika[self.klub1]["zabijeni"] - self.statistika[self.klub1]["primljeni"]
        self.statistika[self.klub2]["gol_razlika"] = self.statistika[self.klub2]["zabijeni"] - self.statistika[self.klub2]["primljeni"]

        if gol1 > gol2:
            self.statistika[self.klub1]["bodovi"] += 3
        elif gol2 > gol1:
            self.statistika[self.klub2]["bodovi"] += 3
        else:
            self.statistika[self.klub1]["bodovi"] += 1
            self.statistika[self.klub2]["bodovi"] += 1

        # Povećaj broj odigranih utakmica
        self.statistika[self.klub1]["odigrane_utakmice"] += 1
        self.statistika[self.klub2]["odigrane_utakmice"] += 1

        # Dodaj rezultat u rezultate utakmica
        self.rezultati_utakmica[(self.klub1, self.klub2)] = (gol1, gol2)

        # Pohranjuje koje utakmice su odigrane
        self.odigrano_u_kolu.add((self.klub1, self.klub2))

        # Očisti unos rezultata
        self.entry_gol1.delete(0, tk.END)
        self.entry_gol2.delete(0, tk.END)

        # Ažuriraj gumb za utakmicu
        if (self.klub1, self.klub2) in self.gumbovi_utakmica:
            self.gumbovi_utakmica[(self.klub1, self.klub2)].config(bg="gray", state="disabled")

        # Ažuriraj rezultate tekućeg kola
        self.prikazi_rezultate_kola()

        self.prikazi_tablicu()

        # Provjeri je li kolo završeno
        if self.odigrano_u_kolu == set(self.kalendar[self.trenutno_kolo - 1]):
            self.prikazi_progress_bar()  






    #funkcija za dodavanje kluba, provjerava greske i dodaje klub u listu


    def dodaj_klub(self):
        naziv = self.entry_klub.get().strip()
        
        if not naziv or naziv in self.klubovi:
            messagebox.showerror("Greška", "Naziv kluba je prazan ili već postoji.")
            return

        if len(naziv) > 20:
            messagebox.showerror("Greška", "Naziv kluba ne smije imati više od 20 znakova.")
            return

        # Dodaj klub u listu i statistiku
        self.klubovi.append(naziv)
        self.statistika[naziv] = {"bodovi": 0, "gol_razlika": 0, "zabijeni": 0, "primljeni": 0, "odigrane_utakmice": 0}
        lbl = tb.Label(self.klub_frame, text=naziv, font=("Helvetica", 12, "bold"))
        lbl.pack(anchor="w", pady=2)
        self.entry_klub.delete(0, tk.END)
        self.prikazi_klubove()









    #funkcija za prikazivanje tablice, sortira klubove po bodovima i gol razlici

    def prikazi_tablicu(self):
        for item in self.tablica.get_children():
            self.tablica.delete(item)

        # Sortiraj klubove po bodovima i gol razlici
        sortirano = sorted(self.statistika.items(), key=lambda x: (-x[1]["bodovi"], -x[1]["gol_razlika"]))

        # Dodaj podatke u tablicu
        for pozicija, (klub, stats) in enumerate(sortirano, start=1):
            self.tablica.insert("", "end", values=(
                pozicija, 
                klub,
                stats["bodovi"],
                stats["zabijeni"],
                stats["primljeni"],
                stats["gol_razlika"],
                stats["odigrane_utakmice"]
            ))





    #--------------KALENDARI---------------------



    def generiraj_kalendar(self):
        klubovi = self.klubovi.copy()
        broj_klubova = len(klubovi)
        broj_kola = (broj_klubova - 1) * 2
        broj_utakmica_po_kolu = broj_klubova // 2

        # Generiraj sve moguće parove (domaćin, gost)
        svi_parovi = [(domacin, gost) for domacin in klubovi for gost in klubovi if domacin != gost]
        random.shuffle(svi_parovi) 

        # Skup za praćenje svih odigranih utakmica
        odigrani_matchupi = set()

        # Lista za spremanje rasporeda
        kalendar = []

        for kolo_index in range(broj_kola):
            print(f"\n--- Generiranje kola {kolo_index + 1} ---")
            kolo = []
            dostupni_klubovi = set(klubovi)  # Klubovi dostupni za ovo kolo
            brojac = 0  # Brojač za praćenje popunjenih utakmica

            # Pokušaj generirati kolo dok ne bude ispravno popunjeno
            while brojac < broj_utakmica_po_kolu:
                valjani_par = None
                for par in svi_parovi:
                    domacin, gost = par
                    if (
                        domacin in dostupni_klubovi and
                        gost in dostupni_klubovi and
                        par not in odigrani_matchupi
                    ):
                        valjani_par = par
                        break

                if valjani_par is None:
                    break

                # Dodaj valjani par u kolo
                domacin, gost = valjani_par
                kolo.append(valjani_par)
                odigrani_matchupi.add(valjani_par)
                dostupni_klubovi.remove(domacin)
                dostupni_klubovi.remove(gost)
                brojac += 1

            # Ako kolo nije popunjeno, pokušaj do 5 puta popuniti preostale utakmice
            for _ in range(5):
                if brojac == broj_utakmica_po_kolu:
                    break  # Ako je kolo popunjeno, prekini pokušaje

                for par in svi_parovi:
                    domacin, gost = par
                    if (
                        domacin in dostupni_klubovi and
                        gost in dostupni_klubovi and
                        par not in odigrani_matchupi
                    ):
                        kolo.append(par)
                        odigrani_matchupi.add(par)
                        dostupni_klubovi.remove(domacin)
                        dostupni_klubovi.remove(gost)
                        brojac += 1
                        if brojac == broj_utakmica_po_kolu:
                            break

            # Ako kolo i dalje nije popunjeno, na silu upari preostale klubove
            if brojac < broj_utakmica_po_kolu:
                print(f"Kolo {kolo_index + 1} nije popunjeno nakon 5 pokušaja. Na silu uparujem preostale klubove...")
                slobodni_klubovi = list(dostupni_klubovi)
                while len(slobodni_klubovi) > 1:
                    domacin = slobodni_klubovi.pop(0)
                    gost = slobodni_klubovi.pop(0)
                    kolo.append((domacin, gost))
                    odigrani_matchupi.add((domacin, gost))
                    brojac += 1

            # Dodaj kolo u kalendar
            kalendar.append(kolo)
            print(f"Kolo {kolo_index + 1} završeno: {kolo}")

        return kalendar


    def generiraj_datume(self, broj_kola, samo_vikendom=True):
        datumi = []
        danas = self.pocetni_datum_lige  # Početni datum lige

        for _ in range(broj_kola):
            kolo_datumi = []

            if samo_vikendom:
                # Pronađi prvi slobodan vikend za cijelo kolo
                while True:
                    subota = danas if danas.weekday() == 5 else danas + timedelta(days=(5 - danas.weekday()))
                    nedjelja = subota + timedelta(days=1)

                    # Provjeri je li cijelo kolo unutar praznika
                    if any(pocetni <= subota <= zavrsni or pocetni <= nedjelja <= zavrsni for pocetni, zavrsni in self.praznici):
                        danas = nedjelja + timedelta(days=1)  # Pomakni na prvi ponedjeljak
                        continue
                    break

                # Dodaj utakmice za subotu i nedjelju naizmjenično
                utakmice_u_kolu = len(self.klubovi) // 2
                for i in range(utakmice_u_kolu):
                    if i % 2 == 0:  # Alterniraj: parne utakmice subotom
                        trenutni_datum = subota
                    else:  # Neparne utakmice nedjeljom
                        trenutni_datum = nedjelja

                    kolo_datumi.append(trenutni_datum.strftime("%d.%m.%Y"))

                danas = subota + timedelta(days=7)  # Pomakni na sljedeću subotu
            else:
                # Pronađi prvi slobodan ponedjeljak za cijelo kolo
                while danas.weekday() != 0 or any(pocetni <= danas <= zavrsni for pocetni, zavrsni in self.praznici):
                    danas += timedelta(days=1)

                # Dodaj utakmice za svaki dan u tjednu
                utakmice_u_kolu = len(self.klubovi) // 2
                for i in range(utakmice_u_kolu):
                    trenutni_datum = danas + timedelta(days=(i % 7))  # Rotiraj dane unutar tjedna
                    kolo_datumi.append(trenutni_datum.strftime("%d.%m.%Y"))

                danas += timedelta(days=7)  # Pomakni na sljedeći tjedan

            datumi.append(kolo_datumi)

        return datumi








    def unesi_praznike(self, parent=None):
        try:
            if parent is None:
                parent = self.root

            broj_razdoblja = simpledialog.askinteger("Unos praznika", "Koliko razdoblja pauze želite unijeti?", parent=parent)
            if broj_razdoblja is None or broj_razdoblja < 0:
                return

            praznici = []
            for i in range(broj_razdoblja):
                pocetni_datum = simpledialog.askstring("Unos praznika", f"Unesite početni datum za razdoblje {i + 1} (dd.mm.yyyy):", parent=parent)
                zavrsni_datum = simpledialog.askstring("Unos praznika", f"Unesite završni datum za razdoblje {i + 1} (dd.mm.yyyy):", parent=parent)

                try:
                    pocetni = datetime.strptime(pocetni_datum, "%d.%m.%Y")
                    zavrsni = datetime.strptime(zavrsni_datum, "%d.%m.%Y")
                    if pocetni > zavrsni:
                        messagebox.showerror("Greška", f"Početni datum za razdoblje {i + 1} ne može biti nakon završnog datuma.", parent=parent)
                        continue
                    praznici.append((pocetni, zavrsni))
                except ValueError:
                    messagebox.showerror("Greška", "Neispravan datum ili format datuma", parent=parent)

            # Spoji preklapajuće ili uzastopne praznike
            praznici.sort()
            spojeni_praznici = []
            for pocetni, zavrsni in praznici:
                if not spojeni_praznici or spojeni_praznici[-1][1] < pocetni - timedelta(days=1):
                    spojeni_praznici.append((pocetni, zavrsni))
                else:
                    spojeni_praznici[-1] = (spojeni_praznici[-1][0], max(spojeni_praznici[-1][1], zavrsni))

            self.praznici = spojeni_praznici
            self.prikazi_pauze()
        except Exception as e:
            messagebox.showerror("Greška", f"Došlo je do greške: {e}", parent=parent)








    #------------------ RUCNI UNOS RASPOREDA ------------------

    def unesi_raspored(self):
        self.kalendar = []
        self.datumi = []
        odigrane_utakmice = set()
        if hasattr(self, "lbl_pauze"):
            self.lbl_pauze.pack_forget()
        broj_kola = (len(self.klubovi) - 1)*2

        # Kreiraj novi prozor za unos
        prozor = tk.Toplevel(self.root)
        prozor.title("Ručni unos rasporeda")
        prozor.geometry("700x500")
        prozor.transient(self.root)
        prozor.grab_set()

        # Tablica za prikaz unosa
        tablica = ttk.Treeview(prozor, columns=("Kolo", "Domaćin", "Gost", "Datum"), show="headings", height=15)
        tablica.heading("Kolo", text="Kolo")
        tablica.heading("Domaćin", text="Domaćin")
        tablica.heading("Gost", text="Gost")
        tablica.heading("Datum", text="Datum")
        tablica.column("Kolo", width=50, anchor="center")
        tablica.column("Domaćin", width=200, anchor="center")
        tablica.column("Gost", width=200, anchor="center")
        tablica.column("Datum", width=150, anchor="center")
        tablica.pack(fill="both", expand=True, padx=10, pady=10)

        trenutno_kolo = 1
        odabrani_klubovi = set()
        domacin = None




        # Funkcija za odabir domaćina
        def otvori_prozor_domacina():
            prozor_domacin = tk.Toplevel(prozor)
            prozor_domacin.title("Odaberi domaćina")
            prozor_domacin.geometry("400x300")
            prozor_domacin.transient(prozor)
            prozor_domacin.grab_set()

            tk.Label(prozor_domacin, text="Odaberi domaćina:", font=("Helvetica", 14, "bold")).pack(pady=10)

            for klub in self.klubovi:
                # Provjeri je li klub već ugostio sve ostale klubove
                broj_gostiju = sum(1 for kolo in self.kalendar for (domacin, gost) in kolo if domacin == klub)
                if broj_gostiju >= len(self.klubovi) - 1:
                    # Onemogući gumb ako je klub već bio domaćin svim ostalim klubovima
                    gumb = tk.Button(prozor_domacin, text=f"{klub} (sve ugostio)", width=30, state="disabled", bg="gray")
                elif trenutno_kolo <= len(self.kalendar) and any(klub in (domacin, gost) for domacin, gost in self.kalendar[trenutno_kolo - 1]):
                    # Onemogući gumb ako je klub već igrao u trenutnom kolu
                    gumb = tk.Button(prozor_domacin, text=f"{klub} (već igra)", width=30, state="disabled", bg="gray")
                else:
                    # Omogući gumb za odabir domaćina
                    gumb = tk.Button(prozor_domacin, text=klub, width=20,
                                    command=lambda k=klub: [odaberi_domacina(k), prozor_domacin.destroy()])
                gumb.pack(pady=5)






        # Funkcija za odabir gosta
        def otvori_prozor_gosta(domacin):
            prozor_gost = tk.Toplevel(prozor)
            prozor_gost.title("Odaberi gosta")
            prozor_gost.geometry("400x300")
            prozor_gost.transient(prozor)
            prozor_gost.grab_set()

            tk.Label(prozor_gost, text="Odaberi gosta:", font=("Helvetica", 14, "bold")).pack(pady=10)

            for klub in self.klubovi:
                # Provjeri je li klub isti kao domaćin
                if klub == domacin:
                    continue
                # Provjeri je li klub već igrao u trenutnom kolu
                elif trenutno_kolo <= len(self.kalendar) and any(klub in (domacin, gost) for domacin, gost in self.kalendar[trenutno_kolo - 1]):
                    continue
                # Provjeri je li kombinacija domaćin-gost već unesena
                elif any((domacin, klub) in kolo for kolo in self.kalendar):
                    continue
                else:
                    # Omogući gumb za odabir gosta
                    gumb = tk.Button(prozor_gost, text=klub, width=20,
                                    command=lambda k=klub: [odaberi_gosta(k), prozor_gost.destroy()])
                gumb.pack(pady=5)






        # Funkcija za odabir domaćina
        def odaberi_domacina(klub):
            nonlocal domacin
            domacin = klub
            otvori_prozor_gosta(domacin)


        # Funkcija za odabir gosta
        def odaberi_gosta(klub):
            nonlocal trenutno_kolo
            nonlocal domacin
            gost = klub

            # Provjeri je li kombinacija domaćina i gosta već unesena
            for kolo in self.kalendar:
                if (domacin, gost) in kolo:
                    messagebox.showerror("Greška", f"Utakmica između {domacin} i {gost} već postoji u rasporedu.")
                    return

            # Unos datuma
            datum = simpledialog.askstring("Dodaj utakmicu", "Unesite datum (dd.mm.yyyy):", parent=prozor)
            try:
                datum_obj = datetime.strptime(datum, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Greška", "Neispravan format datuma. Koristite format dd.mm.yyyy.", parent=prozor)
                return

            # Dodaj utakmicu u tablicu i kalendar
            tablica.insert("", "end", values=(trenutno_kolo, domacin, gost, datum))
            while len(self.kalendar) < trenutno_kolo:
                self.kalendar.append([])
                self.datumi.append([])
            self.kalendar[trenutno_kolo - 1].append((domacin, gost))
            self.datumi[trenutno_kolo - 1].append(datum_obj.strftime("%d.%m.%Y"))
            odabrani_klubovi.add(domacin)
            odabrani_klubovi.add(gost)

            # Provjeri je li kolo popunjeno
            if len(self.kalendar[trenutno_kolo - 1]) == len(self.klubovi) // 2:
                trenutno_kolo += 1
                if trenutno_kolo > broj_kola:
                    messagebox.showinfo("Raspored kompletiran", "Sva kola su unesena. Liga će sada započeti.")
                    self.zapocni_ligu_iz_rasporeda(prozor)
                    return
                tablica.insert("", "end", values=("", f"--- Kolo {trenutno_kolo} ---", "", ""))  # Vizualni razdjelnik
                odabrani_klubovi.clear()

        # Gumb za dodavanje utakmice
        btn_dodaj_utakmicu = tk.Button(prozor, text="Dodaj utakmicu", command=otvori_prozor_domacina, bg="green", fg="white", width=20)
        btn_dodaj_utakmicu.pack(pady=10)

        # Gumb za spremanje rasporeda
        btn_spremi = tk.Button(prozor, text="Spremi raspored", command=lambda: self.zapocni_ligu_iz_rasporeda(prozor), bg="gray", fg="white", width=20)
        btn_spremi.pack(pady=10)





    def zapocni_ligu_iz_rasporeda(self, prozor):
        # Provjeri je li raspored popunjen
        if len(self.kalendar) < 1 or any(len(kolo) < len(self.klubovi) // 2 for kolo in self.kalendar):
            messagebox.showerror("Greška", "Raspored nije kompletan. Provjerite jeste li unijeli sve utakmice.")
            return

        # Zatvori prozor za unos rasporeda
        prozor.destroy()

        # Postavi trenutno kolo na 1 i prikaži utakmice
        self.trenutno_kolo = 1
        self.prikazi_utakmice()
        self.prikazi_rezultate_kola()

        # Onemogući unos klubova i gumb "Počni ligu"
        self.entry_klub.config(state="disabled")
        self.btn_dodaj_klub.config(state="disabled")
        self.btn_pocni_ligu.config(state="disabled")

        messagebox.showinfo("Liga započela", "Raspored je spremljen i liga je započela!")






        #funkcija za kreiranje scrollable framea, koristi canvas i scrollbar

    def create_scrollable_frame(self, parent):
        canvas = tk.Canvas(parent, width=parent["width"])  # Postavi širinu Canvas-a
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame
    

    




# ---------------- SAVE/LOAD ----------------
    def spremi_stanje(self, filename="liga_stanje.pkl"):
        try:
            stanje = {
                "klubovi": self.klubovi,
                "statistika": self.statistika,
                "kalendar": self.kalendar,
                "datumi": self.datumi,
                "trenutno_kolo": self.trenutno_kolo,
                "odigrano_u_kolu": self.odigrano_u_kolu,
                "praznici": self.praznici, 
                "rezultati_utakmica": self.rezultati_utakmica,  
            }
            with open(filename, "wb") as f:
                pickle.dump(stanje, f)
            messagebox.showinfo("Spremanje", "Stanje lige je uspješno spremljeno.")
        except Exception as e:
            messagebox.showerror("Greška", f"Došlo je do greške prilikom spremanja: {e}")


    def ucitaj_stanje(self, filename="liga_stanje.pkl"):
        try:
            with open(filename, "rb") as f:
                stanje = pickle.load(f)
            self.klubovi = stanje["klubovi"]
            self.statistika = stanje["statistika"]
            self.kalendar = stanje["kalendar"]
            self.datumi = stanje["datumi"]
            self.trenutno_kolo = stanje["trenutno_kolo"]
            self.odigrano_u_kolu = stanje["odigrano_u_kolu"]
            self.praznici = stanje.get("praznici", [])  # Dodano: učitavanje prazničnih datuma
            self.rezultati_utakmica = stanje.get("rezultati_utakmica", {})  # Dodano: učitavanje rezultata utakmica

            # Ažuriraj UI nakon učitavanja
            self.prikazi_utakmice()
            self.prikazi_tablicu()
            self.prikazi_klubove()
            self.prikazi_rezultate_kola()
            self.prikazi_pauze()
            self.entry_klub.config(state="disabled")
            self.btn_dodaj_klub.config(state="disabled")
            self.btn_pocni_ligu.config(state="disabled")
            messagebox.showinfo("Učitavanje", "Stanje lige je uspješno učitano.")
        except FileNotFoundError:
            messagebox.showerror("Greška", "Datoteka sa stanjem lige nije pronađena.")
        except Exception as e:
            messagebox.showerror("Greška", f"Došlo je do greške prilikom učitavanja: {e}")



#----------------- PDF ----------------


    def izvezi_raspored_u_pdf(self, filename="raspored_utakmica.pdf"):
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            y = height - 50  # Početna visina za ispis

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "Raspored utakmica za sezonu")
            y -= 30

            for broj_kola, (utakmice_kola, datumi_kola) in enumerate(zip(self.kalendar, self.datumi), start=1):
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, f"Kolo {broj_kola}")
                y -= 20

                for (domacin, gost), datum in zip(utakmice_kola, datumi_kola):
                    rezultat = "Nije još odigrano"
                    if (domacin, gost) in self.rezultati_utakmica:
                        gol1, gol2 = self.rezultati_utakmica[(domacin, gost)]
                        rezultat = f"{gol1}:{gol2}"

                    c.setFont("Helvetica", 12)
                    c.drawString(70, y, f"{datum}: {domacin} - {gost} ({rezultat})")
                    y -= 15

                    #Dodaj novu stranicu
                    if y < 50:
                        c.showPage()
                        y = height - 50

                y -= 10  #Razmak između kola

            c.save()
            messagebox.showinfo("PDF generiran", f"Raspored utakmica je uspješno izvezen u '{filename}'.")
        except Exception as e:
            messagebox.showerror("Greška", f"Došlo je do greške prilikom generiranja PDF-a: {e}")


    def izvezi_tablicu_u_pdf(self, filename="tablica_poretka.pdf"):
        try:
            # Kreiraj PDF dokument
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []

            # Naslov PDF-a
            naslov = [["Tablica poretka"]]
            naslov_tablica = Table(naslov, colWidths=[500])
            naslov_tablica.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]))
            elements.append(naslov_tablica)

            # Zaglavlje tablice
            data = [["Pozicija", "Klub", "Bodovi", "Zabijeni", "Primljeni", "Gol razlika", "Odigrane ut."]]

            # Podaci iz tablice poretka
            sortirano = sorted(self.statistika.items(), key=lambda x: (-x[1]["bodovi"], -x[1]["gol_razlika"]))
            for pozicija, (klub, stats) in enumerate(sortirano, start=1):
                data.append([
                    str(pozicija),
                    klub,
                    str(stats["bodovi"]),
                    str(stats["zabijeni"]),
                    str(stats["primljeni"]),
                    str(stats["gol_razlika"]),
                    str(stats["odigrane_utakmice"]),
                ])

            # Kreiraj tablicu
            tablica = Table(data, colWidths=[50, 150, 70, 70, 70, 70, 100])
            tablica.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Vidljive linije
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Siva pozadina za zaglavlje
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Bijela boja teksta za zaglavlje
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Poravnanje teksta
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold font za zaglavlje
                ("FONTSIZE", (0, 0), (-1, 0), 12),  # Veličina fonta za zaglavlje
                ("FONTSIZE", (0, 1), (-1, -1), 10),  # Veličina fonta za podatke
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),  # Bijela pozadina za podatke
            ]))

            elements.append(tablica)

            # Spremi PDF
            doc.build(elements)
            messagebox.showinfo("PDF generiran", f"Tablica poretka je uspješno izvezena u '{filename}'.")
        except Exception as e:
            messagebox.showerror("Greška", f"Došlo je do greške prilikom generiranja PDF-a: {e}")










# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LigaAplikacija(root)
    root.mainloop()