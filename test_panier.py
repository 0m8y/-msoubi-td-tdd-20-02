from datetime import datetime, timedelta
from Panier import Panier
from Panier import Article
import pytest

@pytest.fixture
def panier():
    panier = Panier()
    panier.addArticle("milk", 1, 1, "2023-01-01")
    panier.addArticle("pasta", 2, 1, "2023-01-01")
    panier.addArticle("beef", 12, 1, "2023-01-01")
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
    panier.addArticle("chocolat", 1, 1, "2023-01-01")
    assert len(panier.getArticles()) == 4

def test_get_total(panier):
    assert panier.getTotal() == 15
    panier.addArticle("chocolat", 25, 1, "2023-01-01")
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
    article = Article("yogurt", 3, 10, "2023-01-01")
    assert article.isExpired("2023-01-02")
    assert not article.isExpired("2022-12-31")

def test_article_quantity_management():
    panier = Panier()
    panier.addArticle("bread", 1, 5, "2024-01-01")
    
    panier.removeArticle("bread", 3)
    assert panier.getArticles()[0].getQuantity() == 2
    
    with pytest.raises(ValueError) as e:
        panier.removeArticle("bread", 3)
    assert str(e.value) == "La quantité en stock ne peut pas être négative."
    
    panier.addArticle("bread", 1, 2, "2024-01-01")
    assert panier.getArticles()[0].getQuantity() == 4

@pytest.fixture
def stock_history():
    panier = Panier()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    panier.addArticle("milk", 1, 10, today)
    panier.addArticle("bread", 0.5, 5, yesterday)
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
    