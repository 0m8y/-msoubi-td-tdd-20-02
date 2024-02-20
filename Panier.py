from datetime import datetime

class StockHistory:
    def __init__(self):
        self.changes = []

    def update(self, name, quantity, date, typeModification):
        self.changes.append({"name": name, "quantity": quantity, "date": datetime.strptime(date, "%Y-%m-%d"), "type": typeModification})

    def displayStock(self, date):
        stateStock = {}
        for change in self.changes:
            if change["date"] <= datetime.strptime(date, "%Y-%m-%d"):
                if change["name"] in stateStock:
                    stateStock[change["name"]] += change["quantity"] if change["type"] == "ajout" else -change["quantity"]
                else:
                    stateStock[change["name"]] = change["quantity"]
        print(f"État du stock au {date} :", stateStock)

    def displayStockEvolution(self, date_debut, date_fin):
        date_debut_dt = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_dt = datetime.strptime(date_fin, "%Y-%m-%d")
        
        print(f"Évolution du stock du {date_debut} au {date_fin}:")
        for change in self.changes:
            if date_debut_dt <= change["date"] <= date_fin_dt:
                print(change)

class Article:
    def __init__(self, name, price, quantity, expirationDate):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.expirationDate = datetime.strptime(expirationDate, "%Y-%m-%d")

    def getName(self):
        return self.name
    
    def getPrice(self):
        return self.price
    
    def getQuantity(self):
        return self.quantity

    def getExpirationDate(self):
        return self.expirationDate
    
    def isExpired(self, currentDate):
        return datetime.strptime(currentDate, "%Y-%m-%d") > self.expirationDate
    
    def reduceStock(self, quantity):
        if self.quantity - quantity < 0:
            raise ValueError("La quantité en stock ne peut pas être négative.")
        self.quantity -= quantity

    def increaseStock(self, quantity):
        self.quantity += quantity

class Coupon:
    def __init__(self, name, reduction, article=None):
        self.name = name
        self.reduction = reduction
        self.article = article

class Panier:
    def __init__(self):
        self.articles = []
        self.reduction = None
        self.stockHistory = StockHistory()
        self.coupons = []

    def getTotal(self):
        total = 0
        for article in self.articles:
            if not article.isExpired(datetime.now().strftime("%Y-%m-%d")):
                total += article.getPrice() * article.getQuantity()
        if self.reduction is not None:
            total -= total * (self.reduction / 100)
        return total
    
    def removeArticle(self, articleName, quantity=None):
        for article in self.articles:
            if article.getName() == articleName:
                initialQuantity = article.getQuantity()
                if quantity is None or quantity == initialQuantity:
                    self.articles.remove(article)
                    self.stockHistory.update(articleName, initialQuantity, datetime.now().strftime("%Y-%m-%d"), "remove")
                else:
                    article.reduceStock(quantity)
                    self.stockHistory.update(articleName, quantity, datetime.now().strftime("%Y-%m-%d"), "remove")
                return
        raise ValueError("L'article n'est pas en stock.")
        
    def addArticle(self, name, price, quantity, expirationDate):
        found = False
        for article in self.articles:
            if article.getName() == name and article.getExpirationDate() == datetime.strptime(expirationDate, "%Y-%m-%d"):
                article.increaseStock(quantity)
                found = True
                break
        if not found:
            newArticle = Article(name, price, quantity, expirationDate)
            self.articles.append(newArticle)
        self.stockHistory.update(name, quantity, datetime.now().strftime("%Y-%m-%d"), "add")

    def getArticles(self):
        return self.articles
    
    def setReduction(self, reduction):
        if reduction <= 0:
            raise ValueError("La réduction doit être supérieure à 0.")
        if self.reduction is not None:
            raise ValueError("Une réduction a déjà été appliquée.")
        else:
            self.reduction = reduction

    def addCoupon(self, name, reduction, article=None):
        if reduction <= 0:
            raise ValueError("La réduction doit être supérieure à 0.")
        if article is None:
            if self.reduction is not None:
                raise ValueError("Une réduction a déjà été appliquée.")
            self.reduction = Coupon(name, reduction)
        if any(coupon for coupon in self.coupons if coupon.name == name):
            raise ValueError("Ce coupon a déjà été appliqué a un article.")
        if any(coupon for coupon in self.coupons if coupon.article == article):
            raise ValueError("L'article possède déjà un coupon.")
        self.coupons.append(Coupon(name, reduction, article))

    def getStockHistory(self):
        return self.stockHistory

    def displayStockOnDate(self, date):
        self.stockHistory.displayStock(date)

    def displayStockEvolution(self, startDate, endDate):
        self.stockHistory.displayStockEvolution(startDate, endDate)
    