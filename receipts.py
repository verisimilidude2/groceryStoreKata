""" Receipt Total Generation Kata
    (https://github.com/PillarTechnology/kata-checkout-order-total)

    Requires Python 3.7 to run
"""
from collections import defaultdict
from typing import Callable, Union, List, Dict, Any, NamedTuple, Type, Tuple
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

    def handle_limit(self,
                     disc_limit: int, # max number of products to be discounted
                     cur_disc: int,  # number currently discounted
                     cur_full: int  # number currently full price
                    ) -> Tuple[int,int]:
        """ This method checks the current number of full price and
            discounted items against a limit for the number eligible
            for a discount and returns (possibly) adjusted discount
            and full price counts.

            For example:
                "buy 2, get 1 free, limit 6" and 10 have been scanned.
                The discount limit would be 2 (== 6//(2+1) )
                cur_disc would be 3 and cur_full would be 7.
                Since 3 > 2 we are past the limit and all later
                items should be full price.
                This routine will return a discounted count of 2 and
                a full price count of 8.
        """
        # short circuit if there is no limit
        if not disc_limit:
            return(cur_disc, cur_full)
        disc = cur_disc # number to sell at discout
        full = cur_full # number to sell at full price
        if cur_disc > disc_limit:
            disc = disc_limit
            full = (cur_disc + cur_full) - disc
        return (disc, full)


    ###############################
    # ways of calculating a price #
    ###############################
    def standard(self, qty: SaleQuantity) -> Money:
        """ Calculate a standard, non-special price """
        return (Money(self.price * qty).quantize(Decimal('.01'),
                                                 rounding=ROUND_UP))

    @classmethod
    def cents_off(cls: Type['StockType'], amount_off: float,
                  limit:int=None) -> \
                  Callable[[Any, SaleQuantity], Money]:
        """ Returns a function that takes a quantity and returns the
            price with a per-item price-off reduction.
        """
        def cents_off_calc(self, qty: int, discount: Money, limit:int):
            "inline function that actually does the calculation"
            (disc, full) = self.handle_limit(limit, qty, 0)
            return ((Money((self.price - amount_off) * disc)) +
                    (Money(self.price * full)).
                          quantize(Decimal('.01')))

        # return function with items set in store's stock definition bound
        return partial(cents_off_calc, discount=amount_off, limit=limit)


    @classmethod
    def conditional_percent_off(cls: Type['StockType'], min_items: int,
                                disc_items: int, pct_off: float,
                                limit: int=None) -> \
                                Callable[[Any, SaleQuantity], Money]:
        """ Returns a function that implements 'Buy N items get M at %X off'
            pricing specials.
            TODO: ask customer if this type of discount ever applies to
            weighed items
        """
        def conditional_percent_off_calc(self, qty: int, min_items: int,
                                         disc_items: int, pct_off: int,
                                         limit: int):
            "inline function that actually does the calculation"
            grp = min_items + disc_items # max number of items in a dsct group
            disc_qty = (((qty//grp) * disc_items) +
                        max((qty % grp) - min_items, 0))
            full_qty = qty - disc_qty
            # calculate max number of discounted items (pythonic ternary)
            disc_limit = limit and limit // grp
            # adjust discounted count when there is a limit
            disc_qty, full_qty = self.handle_limit(disc_limit,
                                                   disc_qty, full_qty)

            return (Money(self.price * full_qty).  # items with no discount
                          quantize(Decimal('.01')) +
                    # plus items that are discounted
                    Money((self.price * (1.0 - pct_off/100.0)) * disc_qty).
                          quantize(Decimal('.01')))

        # ask customer if they want these common sense constraints. Not in the
        # Use Cases but calculations may not be valid outside these ranges.
        if pct_off <= 0 or pct_off > 100:
            raise NotImplementedError(f"Cannot have a discount percentage "
                "that is 0% or less or more than 100%, got {pct_off}")
        if min_items < 1:
            raise NotImplementedError(f"Cannot have a discount where one "
                "must buy less than one item, got {min_items}")
        if disc_items < 1:
            raise NotImplementedError(f"Cannot have a discount where the "
                "number of items discounted is less than one, got {min_items}")
        if limit and limit < (min_items + disc_items):
            raise NotImplementedError(f"Cannot have a purchase limit where the "
                "number of items needed to be purchased is less than the "
                "purchase limit.  (e.g. 'buy 3 get 1 half off, limit 1' is "
                "wrong, it should be limit 4 to limit to one discounted item. "
                "Got limit={limit}, full price count={min_items}, discounted "
                "count={disc_items}")

        # return function with items set in store's stock definition bound
        return partial(conditional_percent_off_calc, min_items=min_items,
                       disc_items=disc_items, pct_off=pct_off, limit=limit)


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
            KeyError if the item_desc is not in the inventory or
            NotImplementedError if the quantity does not match how the
            item is sold (e.g. a weight for a product sold by item count).
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
        return rcp_total.quantize(Decimal('.01'))
