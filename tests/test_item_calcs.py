""" Test for the Receipt Total Generation Kata """
import os
import sys
from decimal import Decimal
from typing import Dict
import pytest
from ..receipts import POS, StockType, SaleType, Receipt

def test_bad_stock_types():
    """ Test the various ways creation of a StockType may fail """
    #  pct_off <= 0
    with pytest.raises(NotImplementedError):
        badStock = StockType(0.28, SaleType.BY_WT,
                             StockType.conditional_percent_off(
                                 min_items=2, disc_items=1, pct_off=-100))
    #  pct_off > 100:
    with pytest.raises(NotImplementedError):
        badStock = StockType(0.28, SaleType.BY_WT,
                             StockType.conditional_percent_off(
                                 min_items=2, disc_items=1, pct_off=110))
    # min_items < 1:
    with pytest.raises(NotImplementedError):
        badStock = StockType(0.28, SaleType.BY_WT,
                             StockType.conditional_percent_off(
                                 min_items=0, disc_items=1,
                                 pct_off=100))
    # disc_items < 1:
    with pytest.raises(NotImplementedError):
        badStock = StockType(0.28, SaleType.BY_WT,
                             StockType.conditional_percent_off(
                                 min_items=1, disc_items=0,
                                 pct_off=100))
    # limit < (min_items + disc_items):
    with pytest.raises(NotImplementedError):
        badStock = StockType(0.28, SaleType.BY_WT,
                             StockType.conditional_percent_off(
                                 min_items=1, disc_items=0,
                                 pct_off=100, limit=1))


@pytest.fixture(scope='module')
def shop_inventory() -> Dict[str, StockType]:
    "shared test info, the inventory carried by the store."
    return {
        "CAMP SOUP 10.75z": StockType(1.99, SaleType.EACH, StockType.standard),
        "15%FAT GRD CHUCK": StockType(1.99, SaleType.BY_WT, StockType.standard),
        "DOZ JNSTN SAUSAG": StockType(4.99, SaleType.EACH,
                                      StockType.cents_off(.45)),
        "2.0L CANFLD SELZ": StockType(1.99, SaleType.EACH,
                                      StockType.cents_off(.25)),
        "BANANAS DELMONTE": StockType(0.28, SaleType.BY_WT,
                                      StockType.cents_off(.08)),
        # Buy one, get on free on hydroponic bib lettuce
        "BIB LETTUCE HDRP": StockType(1.99, SaleType.EACH,
                                      StockType.conditional_percent_off(
                                          min_items=1, disc_items=1,
                                          pct_off=100)),
        # Buy two get one half off on 1 liter coke
        "COKE CLASIC 1.Ol": StockType(1.29, SaleType.EACH,
                                      StockType.conditional_percent_off(
                                          min_items=2, disc_items=1,
                                          pct_off=50)),
        # 25 cents off, limit 6
        "FNCYFST CATFD 3z": StockType(1.25, SaleType.EACH,
                                      StockType.cents_off(.25, limit=6)),
        #"TWO BRTS WBL 6PK": StockType(1.25, SaleType.EACH,
        #"2 QTY DSPSBL BAG": StockType(1.25, SaleType.EACH,

        # buy one get one free, limit six
        "ETERNAL WTR 600M": StockType(1.00, SaleType.EACH,
                                      StockType.conditional_percent_off(
                                          min_items=1, disc_items=1,
                                          pct_off=100, limit=6)),

        # probably bad, discount greater than base price.
        "PROGRESSO TRADI": StockType(1.25, SaleType.EACH,
                                     StockType.cents_off(1.45)),
    }


@pytest.fixture
def receipt(shop_inventory):
    """ Provide a new receipt for each test """
    pos = POS(shop_inventory)
    return Receipt(pos)


def test_standard_calc_single(receipt) -> None:
    """ Test that a receipt with only a single standard
        (non-discount) item on it returns the right price.
    """
    # Add an item to the receipt
    receipt += "CAMP SOUP 10.75z"

    # check the total
    assert receipt.total() == Decimal('1.99')


def test_standard_calc_multiple(receipt) -> None:
    """ Test that a receipt with only three standard
        (non-discount) items on it returns the right total.
    """

    # Add items to the receipt
    receipt += "CAMP SOUP 10.75z"
    receipt += "CAMP SOUP 10.75z"
    receipt += "CAMP SOUP 10.75z"

    # check the total
    assert receipt.total() == Decimal('1.99') * 3


def test_standard_weighed_single(receipt) -> None:
    """ Test that a receipt with only a single standard
        (non-discount) weighed item on it returns the right price.
    """
    # Add an item to the receipt
    receipt.add_scan("15%FAT GRD CHUCK", 3.0)

    # check the total
    assert receipt.total() == Decimal('1.99') * Decimal('3.0')


def test_bad_qty_on_standard(receipt) -> None:
    """ Test that adding a weight for a counted item or a
        count for a weighed item throws the proper exception.
    """
    with pytest.raises(NotImplementedError):
        # weighed item with a count
        receipt.add_scan("15%FAT GRD CHUCK", 1)
    with pytest.raises(NotImplementedError):
        # counted item with a weight
        receipt.add_scan("CAMP SOUP 10.75z", 1.5)


def test_price_off_special_items(receipt) -> None:
    """ Calculate the proper price for special items. """
    # add a discounted item to the receipt
    receipt += "2.0L CANFLD SELZ"
    # add another discounted item to the receipt
    receipt += "DOZ JNSTN SAUSAG"

    # check the total
    assert receipt.total() == (Decimal('1.99') - Decimal('.25') +
                               Decimal('4.99') - Decimal('.45'))


def test_price_off_special_weighed(receipt) -> None:
    """ Calculate the proper price for special items. """
    # add a discounted item to the receipt
    receipt.add_scan("BANANAS DELMONTE", 3.5)

    # check the total
    assert receipt.total() == Decimal('0.70')


def test_price_buy1get1(receipt) -> None:
    receipt += "BIB LETTUCE HDRP"
    # check the total
    assert receipt.total() == Decimal('1.99')
    # buy another
    receipt += "BIB LETTUCE HDRP"
    # check the total, should be the same
    assert receipt.total() == Decimal('1.99')
    # buy a third
    receipt += "BIB LETTUCE HDRP"
    # check that the total has increased
    assert receipt.total() == Decimal('3.98')


def test_price_buy2get1half_off(receipt) -> None:
    # buy four on a buy two get one half off
    receipt.add_scan("COKE CLASIC 1.Ol", 4)
    # results in three full price and one half price
    assert receipt.total() == Decimal(1.29 * 3.5). quantize(Decimal('.01'))


def test_discount_with_limit(receipt) -> None:
    receipt.add_scan("FNCYFST CATFD 3z", 7)
    # six discounted and one full price
    assert receipt.total() == Decimal('7.25')


def test_buy1get1_with_limit(receipt) -> None:
    receipt.add_scan("ETERNAL WTR 600M", 12)
    # three full price, three free, then six more full price
    assert receipt.total() == Decimal('9.00')


def test_discount_greater_than_price(receipt) -> None:
    """ Test that a product with a discount greater than the price is free """
    receipt.add_scan("PROGRESSO TRADI", 1)
    assert receipt.total() == Decimal('0.00')
