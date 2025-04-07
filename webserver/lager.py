class Produkt:
    def __init__(self, namn, vikt):
        self.namn = namn
        self.vikt = vikt
    
    def getWeight(self):
        return self.vikt
    
class Order:
    def __init__(self, lists, adress, ordernumber):
        self.lists = lists
        self.adress = adress
        self.ordernumber = ordernumber

    def getOrderNmbr(self):
        return self.ordernummer

    def getTotWeight(self):
        tot = 0
        for p in self.lists:
            tot += p
        return tot
    
    def wievInfo(self):
        return f"Produkt: {self.list}, \n Adress: {self.adress}"

lista1 = [
    Produkt("Sårsalvor och antiseptiska medel", 50), 
    Produkt("Nässprej", 20), 
    Produkt("C-vitamin", 500), 
]
lista2 = [
    Produkt("Paracetamol", 10),  
    Produkt("Ibuprofen", 16),    
    Produkt("Acetylsalicylsyra", 10), 
]

lista3 = [
    Produkt("Acetylsalicylsyra", 10), 
    Produkt("Antihistaminer", 2),  
    Produkt("Laktosintoleransmedel", 4), 
    Produkt("Antacida", 48),  
]
lista4 = [
    Produkt("Aloe Vera-gel", 100) 
]

olist = [
    Order(lista1, "Magistratsvägen 1", "12345"),
    Order(lista2, "Agardsgatan 1", "654321"),
    Order(lista3, "Tunavägen 5", "109876"),
    Order(lista4, "Södra Esplanaden 10", "567453")
]

class Test:
    def __init__(self, orderlist):
        self.orderlist = orderlist
    
    def getOrder(self, ordernbr):
        for n in self.orderlist:
            if n.getOrderNmbr() == ordernbr:
                return n
            else:
                return None


def main():
    a = Test(olist)

main()
