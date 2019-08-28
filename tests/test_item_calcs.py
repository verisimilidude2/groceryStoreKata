""" Test for the Receipt Total Generation Kata """
import os
import sys
from decimal import Decimal
from typing import Dict
import pytest
from ..receipts import POS, StockType, SaleType, Receipt

@pytest.fixture(scope='module')
def shop_inventory() -> Dict[str, StockType]:
    "shared test info, the inventory carried in the store."
    return {
        "CAMP SOUP 10.75z": StockType(1.99, SaleType.EACH, StockType.standard),
        "15%FAT GRD CHUCK": StockType(1.99, SaleType.BY_WT, StockType.standard),
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
