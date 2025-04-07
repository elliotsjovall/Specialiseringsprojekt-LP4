
class Produkt:
    def __init__(self, namn, lagerstatus, vikt):
        self.namn = namn
        self.lagerstatus = lagerstatus
        self.vikt = vikt

    
    def visa_info(self):
        return f"Produkt: {self.namn}, Lagerstatus: {self.lagerstatus}"
    
class Lager:
    def __init__(self):
        self.produkter = {
            "Paracetamol": Produkt("Paracetamol", 50, 10),  
            "Ibuprofen": Produkt("Ibuprofen", 40, 16),    
            "Acetylsalicylsyra": Produkt("Acetylsalicylsyra", 30, 10), 
            "Antihistaminer": Produkt("Antihistaminer", 20, 2),  
            "Laktosintoleransmedel": Produkt("Laktosintoleransmedel", 60, 4), 
            "Antacida": Produkt("Antacida", 48, 680),  
            "Sårsalvor och antiseptiska medel": Produkt("Sårsalvor och antiseptiska medel", 40, 50), 
            "Nässprej": Produkt("Nässprej", 20, 20), 
            "C-vitamin": Produkt("C-vitamin", 100, 500)  
        }
    
    def lägg_till_produkt(self, namn, antal):
        if namn in self.produkter:
         self.produkter[namn].lagerstatus += antal
        else:
            print(f"Produkten {namn} finns inte i lagret.")


    def köp(self, namn, antal):
        if namn in self.produkter:
            if self.produkter[namn] > antal:
                self.produkter[namn] -= antal
            elif self.produkter[namn] == antal:
                del self.produkter[namn]
            else:
                print(f"Det finns inte tillräckligt av {namn} i lager")
        else:
         print(f"Produkten {namn} finns inte i lager")

    def visa_lager(self):
        return f"Lagerstatus: {self.produkter}"

    def hämta_alla_produkter(self):
        return list(self.produkter.values())
    


