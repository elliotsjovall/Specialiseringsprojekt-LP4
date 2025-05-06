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
        return self.ordernumber

    def getTotWeight(self):
        tot = 0
        for p in self.lists:
            tot += p.getWeight()
        return tot
    def getAdress(self):
        return self.adress

    def wievInfo(self):
        return f"Produkt: {self.lists}, \n Adress: {self.adress}"

class Test:
    def __init__(self, orderlist):
        self.orderlist = orderlist

    def getOrder(self, ordernbr):
        for n in self.orderlist:
            if isinstance(n, Order) and n.getOrderNmbr() == ordernbr:
                return n
        return None
