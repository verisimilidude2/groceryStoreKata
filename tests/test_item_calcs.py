""" Test for the Receipt Total Generation Kata """
import os
import sys
from decimal import Decimal
from typing import Dict
import pytest
#sys.path.insert(0,
#                os.path.join(os.path.dirname(os.path.abspath("__file__")),
#                             "src"))
#from receipts import POS, StockType, SaleType, Receipt
from ..receipts import POS, StockType, SaleType, Receipt

@pytest.fixture(scope='module')
def shop_inventory() -> Dict[str, StockType]:
    "shared test info, the inventory carried in the store."
    return {
        "CAMP SOUP 10.75z": StockType(1.99, SaleType.EACH, StockType.standard)
    }

def test_standard_calc_single(shop_inventory) -> None:
    """ Test that a receipt with only a single standard
        (non-discount) item on it returns the right price.
    """
    # Create a cash register holding only a single standard item)
    pos = POS(shop_inventory)
    receipt = Receipt(pos)

    # Add an item to the receipt
    receipt += "CAMP SOUP 10.75z"

    # check the total
    assert receipt.total() == Decimal('1.99')

def test_standard_calc_multiple(shop_inventory) -> None:
    """ Test that a receipt with only three standard
        (non-discount) items on it returns the right total.
    """
    # Create a cash register holding a single standard item
    pos = POS(shop_inventory)
    receipt = Receipt(pos)

    # Add items to the receipt
    receipt += "CAMP SOUP 10.75z"
    receipt += "CAMP SOUP 10.75z"
    receipt += "CAMP SOUP 10.75z"

    # check the total
    assert receipt.total() == Decimal('1.99') * 3
