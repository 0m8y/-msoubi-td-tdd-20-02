from datetime import datetime, timedelta
from Panier import Panier
from Panier import Article
import pytest

@pytest.fixture
def panier():
    panier = Panier()
    panier.addArticle("milk", 1, 1, "2035-01-01")
    panier.addArticle("pasta", 2, 1, "2035-01-01")
    panier.addArticle("beef", 12, 1, "2035-01-01")
    return panier

def test_constructor(panier):
    ctr_panier = Panier()
    assert ctr_panier.getTotal() == 0

def test_remove_article(panier):
    with pytest.raises(ValueError) as e:
        panier.removeArticle("adzasdqsd")
    assert str(e.value) == "L'article n'est pas en stock."

    panier.removeArticle("milk")

    with pytest.raises(ValueError) as e:
        panier.removeArticle("milk") 
    assert str(e.value) == "L'article n'est pas en stock."

def test_add_article(panier):
    assert len(panier.getArticles()) == 3
    panier.addArticle("chocolat", 1, 1, "2035-01-01")
    assert len(panier.getArticles()) == 4

def test_get_total(panier):
    assert panier.getTotal() == 15
    panier.addArticle("chocolat", 25, 1, "2035-01-01")
    assert panier.getTotal() == 40

def test_reduction(panier):
    assert panier.getTotal() == 15

    with pytest.raises(ValueError) as e:
        panier.setReduction(-1)
    assert str(e.value) == "La réduction doit être supérieure à 0."
    
    with pytest.raises(ValueError) as e:
        panier.setReduction(0)
    assert str(e.value) == "La réduction doit être supérieure à 0."
    
    panier.setReduction(50)
    
    with pytest.raises(ValueError) as e:
        panier.setReduction(20)
    assert str(e.value) == "Une réduction a déjà été appliquée."

    assert panier.getTotal() == 7.5

def test_article_expiration():
    article = Article("yogurt", 3, 10, "2035-01-01")
    assert article.isExpired("2035-01-02")
    assert not article.isExpired("2020-12-31")

def test_article_quantity_management():
    panier = Panier()
    panier.addArticle("bread", 1, 5, "2035-01-01")
    
    panier.removeArticle("bread", 3)
    assert panier.getArticles()[0].getQuantity() == 2
    
    with pytest.raises(ValueError) as e:
        panier.removeArticle("bread", 3)
    assert str(e.value) == "La quantité en stock ne peut pas être négative."
    
    panier.addArticle("bread", 1, 2, "2035-01-01")
    assert panier.getArticles()[0].getQuantity() == 4

@pytest.fixture
def stock_history():
    panier = Panier()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    panier.addArticle("milk", 1, 10, today)
    panier.addArticle("bread", 1, 5, yesterday)
    return panier

def test_update_stock_history(stock_history):
    assert len(stock_history.stockHistory.changes) == 2

def test_display_stock_on_date(stock_history, capsys):
    today = datetime.now().strftime("%Y-%m-%d")
    stock_history.displayStockOnDate(today)
    captured = capsys.readouterr()
    assert "milk" in captured.out
    assert "bread" in captured.out

def test_display_stock_evolution(stock_history, capsys):
    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    stock_history.displayStockEvolution(start_date, end_date)
    captured = capsys.readouterr()
    assert "milk" in captured.out
    assert "bread" in captured.out
    
def test_add_product_updates_stock_history(stock_history):
    stock_history.addArticle("cheese", 2.5, 20, "2035-01-01")
    assert any(change for change in stock_history.getStockHistory().changes if change["name"] == "cheese" and change["type"] == "add" and change["quantity"] == 20)
    assert any(article for article in stock_history.getArticles() if article.getName() == "cheese" and article.getQuantity() == 20)

def test_remove_product_updates_stock_history(stock_history):
    stock_history.addArticle("water", 2, 10, "2035-01-01")
    stock_history.removeArticle("water", 5)
    assert any(change for change in stock_history.getStockHistory().changes if change["name"] == "water" and change["type"] == "remove" and change["quantity"] == 5)
    assert any(article for article in stock_history.getArticles() if article.getName() == "water" and article.getQuantity() == 5)

def test_cannot_reduce_stock_into_negative(stock_history):
    stock_history.addArticle("juice", 1.0, 5, "2035-01-01")
    with pytest.raises(ValueError) as e:
        stock_history.removeArticle("juice", 10)
    assert str(e.value) == "La quantité en stock ne peut pas être négative."
    assert any(article for article in stock_history.getArticles() if article.getName() == "juice" and article.getQuantity() == 5)

def test_isExpired_checks_for_expired_products():
    article = Article("expiredMilk", 1.0, 1, "2020-01-01")
    assert article.isExpired(datetime.now().strftime("%Y-%m-%d")) == True

def test_add_coupon(stock_history, capsys):
    with pytest.raises(ValueError) as e:
        stock_history.addCoupon("ZERO", 0, "milk")
    assert str(e.value) == "La réduction doit être supérieure à 0."
    
    with pytest.raises(ValueError) as e:
        stock_history.addCoupon("CODE NEGATIVE", -5, "milk")
    assert str(e.value) == "La réduction doit être supérieure à 0."

    stock_history.addCoupon("CODE10", 10, "milk")

    with pytest.raises(ValueError) as e:
        stock_history.addCoupon("CODE10", 10, "bread")
    assert str(e.value) == "Ce coupon a déjà été appliqué a un article."

    with pytest.raises(ValueError) as e:
        stock_history.addCoupon("NEWCODE20", 10, "milk")
    assert str(e.value) == "L'article possède déjà un coupon."

def test_display_discounts(stock_history, capsys):
    stock_history.addCoupon("CODE10", 10, "milk")
    assert stock_history.getTotal() == 9
    captured = capsys.readouterr()
    assert "Milk - 1€ => 0.90€ - x10" in captured.out

