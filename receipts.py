""" Receipt Total Generation Kata
    (https://github.com/PillarTechnology/kata-checkout-order-total)

    Requires Python 3.7 to run
"""
from collections import defaultdict
from typing import Callable, Union, List, Dict, Any, NamedTuple, Type
from enum import Enum
from dataclasses import dataclass, field
from functools import partial
from decimal import Decimal, ROUND_UP

class SaleType(Enum):
    """ Ways to measure how much product is sold """
    EACH = 0  # Sold as an integral number of items
    BY_WT = 1 # Sold by weight as measured by a scale

# type aliases
SaleQuantity = Union[int, float]
Sales = List[SaleQuantity]
Money = Decimal

class StockType(NamedTuple):
    "Information about a stocked item"
    price: SaleQuantity # "price per unit for the item"
    how_sold: SaleType # enum, EACH or BY_WT
    pricing: Callable[[Any, SaleQuantity], Money] # function that takes a
        # quantity and returns the price for that quantity of the item.

    def check_qty(self, qty: SaleQuantity) -> None:
        """ raise an error if the numeric type of the quantity is not 
            consistent with the way the item is sold.
        """
        if isinstance(qty, float) and self.how_sold == SaleType.EACH:
            raise NotImplementedError("Quantity sold must be an int "
                "when the item is sold by count.")
        if isinstance(qty, int) and self.how_sold == SaleType.BY_WT:
            raise NotImplementedError("Quantity sold must be a real "
                "when the item is sold by weight.")

    ###############################
    # ways of calculating a price #
    ###############################
    def standard(self, qty: SaleQuantity) -> Money:
        """ Calculate a standard, non-special price """
        return (Money(self.price * qty).quantize(Decimal('.01'),
                                                 rounding=ROUND_UP))

    @classmethod
    def cents_off(cls: Type['StockType'], amount_off: float) -> \
                  Callable[[Any, SaleQuantity], Money]:
        """ Returns a function that takes a quantity and returns the
            price with a per-item price-off reduction.
        """
        def cents_off_calc(self, qty: int, discount: Money):
            "inline function that actually does the calculation"
            return (Money((self.price - amount_off) * qty).
                          quantize(Decimal('.01')))
        return partial(cents_off_calc, discount=amount_off)
            

@dataclass
class Scan:
    "Information about an item on the receipt"
    item_desc: str  # Name given to the item, send from a scanner
    qty: Sales = field(default_factory=list) # List of Number of items
                    # or weight of item on a line of the receipt. qty will
                    # be an int if item is sold by count, a float if
                    # sold by weight


class POS:
    """ A class representing the outside environment that the receipt
        calculation runs within.  Creates the universe of items upon
        initialization.  Scans items and returns information about the
        item.
    """

    def __init__(self,
                 stock_items: Dict[str, StockType]) -> None:
        """ Initializes the database of items that are stocked. """
        self.stock_items = stock_items

    def scan(self, item: str) -> StockType:
        """ Look up the item and return its StockType data.
            May throw a dictionary look-up exception if item
            is not in the stock_items dictionary.
        """
        return self.stock_items[item]

class Receipt:
    """ This object manages items that are on the receipt. It adds items
        (purchases list) to the receipt and calculates the total spent.  The
        items are held in a dictionary indexed by the item with the value being
        a list of item quantities.
    """
    def __init__(self, pos: POS) -> None:
        # what can be purchased
        self.pos = pos
        # what has been purchased
        self.purchases: Dict[StockType, Sales] = defaultdict(list)

    def __iadd__(self, item_desc: str):
        """ Define the += operator to add a scan of an item
            to the receipt.
        """
        self.add_scan(item_desc, 1)
        return self

    def add_scan(self, item_desc: str, qty: SaleQuantity) -> None:
        """ Add a quantity of an item to the receipt. Will raise a
            KeyError if the item_desc is not in the inventory.
        """
        stock_type: StockType = self.pos.scan(item_desc)
        stock_type.check_qty(qty)
        self.purchases[stock_type].append(qty)

    def total(self) -> Money:
        "total up the order, returning the price"
        rcp_total = Money(0.00)
        for purchased_item in self.purchases:
            rcp_total += purchased_item.pricing(
                purchased_item,
                sum(self.purchases[purchased_item]))
        return rcp_total
