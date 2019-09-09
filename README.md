# groceryStoreKata

An exercise to show coding for Pillar.

This is mostly a response to the requirements laid out in the [Checkout Order Kata(https://github.com/PillarTechnology/kata-checkout-order-total)] but I have 
added some assumptions that are in the spirit of the Kata.

# Assumptions

The intended final run environment of this code is an embedded processor
with a processor that is also running the scanner(s), keypad, display, printer,
cash drawer, etc.  The processor is fast enough that keeping up with the
peripherals is a small amount of its capability.  However the memory to be
used is constrained to be whatever is available in the chip's cache and it would
be expensive to add additional memory to every POS terminal to be manufactured.
Therefore in cases where data structures that save time would add to the memory
overhead the choice to be made is to eschew those structures and instead take
additional processor cycles.  For instance I use sequential scanning of a list
in place of additional dictionaries.

Because the processor is believed to be I/O bound I have written the system
to re-calculate the receipt total on every call retrieving the total rather
than holding the total and modifying it.

Security is best designed in rather than added on.  This Kata, as written, has
no security requirements for the API.  I have assumed that this is because the
system has security at another level and the API that I am writing is not to
be publicly available.  The tests I am providing are not part of what is to be
delivered on the embedded processor.  The provided tests may be part of what
will be used to create a test sub-system at a later iteration but the
specification of that sub-system is not within the scope of this exercise.
Therefore the tests may use memory structures and additional libraries that
are not appropriate for the delivered code.

Since this code is not responsible for the receipt there is no requirement that
the it supports keeping the items in scanned, or any other, order.  I assume
some other part of the system will need to call an API to get the final
price of each SKU, in addition to the total price for the receipt.

Access to the stores prices is not done through an API.  I assume that in the
embedded system this data would be downloaded on startup to a data structure
that, for purposes of this API, is read-only.  There is no requirement for
prices to be updated while receipt creation is occurring.  I make the assumption
that the data structure being read-only means that there will not be threading
issues that need to be addressed.

The prices are held in a data structure that could be transmitted in JSON or
YAML but in this code is a dictionary provided when the receipt is begun.  In a
real system putting code into a data structure that is updated with an editor
is nonsense and some system that will allow the user to define prices, maintain
specials, define dates when the specials will be used, and catch problems will
be needed.

# Running The Solution

Code is in the main directory in the `receipts.py` file.  Tests are in the
tests directory in the `test_item_calcs.py` file.

The code requires the latest version of the python programming language,
Python 3.7.  To run the tests requires the pytest module which must be
added after Python is installed.

The appropriate version of Python 3.7 must be installed for your operating
system.  Downloading and installation 
[instructions](https://www.python.org/downloads/) are on the python.org
website.

A probably easier way to get the latest Python version is to install
[Miniconda](https://docs.conda.io/en/latest/miniconda.html).

Once you have cloned the repository and have installed python so it can be
accessed from your command line, change directory into the base of the
repository and create, and then activate, a virtual environment.

    cd groceryStoreKata # your path will probably be different
    python -m venv venv
    source ./venv/bin/activate  # Windows does not require the 'source' word

Now you are set up to install pytest

    pip install pytest

To run the tests:

    pytest tests/

Here is the expected output:

    $ pytest tests/
    ========================== test session starts ===========================
    platform linux -- Python 3.7.0, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
    rootdir: /home/phil/groceryStoreKata, inifile:
    plugins: remotedata-0.3.0, openfiles-0.3.0, doctestplus-0.1.3, arraydiff-0.2
    collected 14 items                                                             

    tests/test_item_calcs.py ..............                             [100%]

    ======================= 14 passed in 0.09 seconds ========================

If there are any errors a stack trace will be dumped along with
information as to what problem was found.


# Use Case Problems

Things that are not in the Use Cases would be brought up to the user
if this was a real project.  In most of these cases I have coded a new
requirement into the system and an exception is raised when the system
is initialized.  In a real system this exception would be caught at a
higher level and a fixup would be applied to the inventory before re-trying
system initialization.

- There is no requirement for cents-off deals on products sold by weight.
    It would be extra code to implement this so I have allowed it.  It
    would be easy to add a check if this were a requirement.
- There is no requirement for checking that any discount does not exceed
    the base price of the item. In my code I have given the item free to
    the purchaser when such a deal is specified.  
- There is no requirement that constrains the range of a percent off value.
    I have chosen to not implement a percent off that is zero or below or that
    is greater than 100%.
- There is no requirement, that constrains the minimum number of items that
    need to be purchased to access a special, to be greater than zero. I have
    chosen to implement this as a requirement for the system.
- There is no requirement that constrains the number of discounted items to
    be less than one.  This has been implemented as a requirement.
- In the case of a special like 'Buy `tot` items, get `disc` items discounted'
    there is no requirement that the `tot` be at least one greater than the
    `disc` number. This has been implemented as a requirement.
- The definition of some of the specials does not follow the practice in
    my neighborhood stores.  For instance "buy 2, get 1 free, limit 6" means
    you are limited to six free items no matter how many you buy while the
    Use Case makes it clear that the offer is on the group of six, two of
    which are free.  A special like "2 for $5" at Jewel means you can get
    one for $2.50 while at Walgreens it means full price if you only buy one.
    At both the third one would be (the discounted) 2.50 each while the Use
    Case indicates that the third should be full price since it is not part
    of the next group of two needed to access the special price.
- In the discussion of 'limit' specials it is unclear what is to happen
    after the limit is reached.  Is the limit to prevent too much discount
    being claimed by a single customer, or is it to prevent too much product
    being bought by a single customer.  I have coded this kata assuming that the
    reason is the first, but if the reason is to prevent too much product going
    to a single customer the code could be extended by changing the `scan`
    method of the POS to raise an exception once the limit is reached.
- The use cases are not clear as to how the method to remove items
    from the receipt is to work.  I have implemented two functions,
    `remove` (remove a specific quantity of an item from the receipt) 
    and `remove_last` (remove the prior scan of an item) to cover two
    possibilities.  A third possibility, removing items in reverse scan
    order, was not implemented since nowhere else is there a
    requirement to keep a record of the order in which items were
    scanned.



# The API

Python allows higher level code to call into any function at a lower level or
to create any class that the code can import.  Calling restrictions are
implemented by convention or merely documented and developers are expected
to follow the directives of the original developer.  This is somewhat similar
to the situation in the Java world with `sun.*` classes that codersi, by
convention, should not use.  

Python also explicitly puts the object `self` parameter in the method definition
although when the method is called the language fills in that value with the
identity of the calling object.  In the documentation below I have left off
the self parameter since it is not seen in the calls.

## Classes

### SaleType

A class that wraps an enumeration of the way to measure how much product is
sold.  There are just two options, `EACH` which is an attribute of products
sold as an integral number of items, and `BY_WT` which is an attribute of
products sold by weight as measured by a scale.

### StockType
This type inherits from the standard class `NamedTuple` which allows named
fields to be predefined for the class and the class's data to be stored in an
immutible data structure (a tuple). That the data structure is immutable allows
it to be used as a dictionary key and to be compared for equality with other
`StockType`s.  The things that the store carries are each defined as an
instance of this type.

#### Stock Type API
- `price: SaleQuantity` The standard, non-special price per unit for the item.

- `how_sold: SaleType` This variable defines whether the price is for a single
   item or whether it if for a standard weight.

- `pricing: Callable[[SaleQuantity], Money]` This variable is a reference to
   a function that takes a quantity and returns the cost for that quantity
   of the product.  If the product is on special the function is a 'curried'
   function that has the details of the special baked into the call and only
   the quantity sold is needed.  For specials this class has function,
   documented below, that return the needed function.

- `check_qty(qty: SaleQuantity) -> None`
   It is expected that the quantity of a weighed item for the standard price
   is expressed as a real number and the quantity per price of a counted item
   is an integer.  This API is used when ingesting the stock data in order
   to enforce this.  This method raises an error if the numeric type of the
   quantity is not consistent with the way the item is sold.

- `handle_limit(disc_limit: int, # max number of products to be discounted
                cur_disc: int,  # number currently discounted
                cur_full: int  # number currently full price
               ) -> Tuple[int,int]:`
   This method checks the current number of full price and discounted items
   against a limit for the number eligible for a discount and returns (possibly)
   adjusted discount and full price counts.

   For example the special is "buy 2, get 1 free, limit 6" and 10 have been
   scanned.  The discount limit would be 2 (== 6//(2+1) ). `cur_disc` before
   adjustment would be three and `cur_full` would be 7.  Since 3 > 2 we are
   past the limit and all items scanned past the limit should be full price.
   This method will return a discounted count of 2 and a full price count of 8.

- `standard(qty: SaleQuantity) -> Money:`
   This is the function for calculation of the amount owed for a specific
   quantity of an item.  It merely returns the price of the object times the
   quantity rounded to the nearest penny.

- `cents_off(amount_off: float, limit:int=None) -> \
             Callable[[Any, SaleQuantity], Money]:`
   This function returns a function.  The function that it returns calculates
   the special price of an item that is being sold on an "X amount off" or
   "X amount off, Limit Y" basis with the amount off and (optionally) the
   limit specified at the time this creation function is called.  If no limit
   is provided in the call the special value None is passed and no limit
   is enforced by the resulting function.

- `conditional_percent_off(min_items: int,
                           disc_items: int, pct_off: float,
                           limit: int=None) -> \
                           Callable[[Any, SaleQuantity], Money]`
    This function returns a function.  The function that it returns takes a
    quantity and returns the price with a per-item percentage price-off
    reduction. A limit on the total number of products to be sold as part
    of this special can optionally be specified. The values passed into this
    function are curried into the returned function so that the returned
    function has the same calling signature as all the other cost calculation
    functions.


### Scan

This dataclass implements no functions outside of the one provided by Python
when the class is marked as a `@dataclass` (e.g. `hash`, equality, data
accessors). The class represents all the scans of a particular item added to
a particular receipt.  It has two data fields, the name of the item that was
scanned and a list of quantities of the item that were added by the scans.  
If the item is sold by weight the quantities are `float`s, if sold by individual
container the quantities are `int`s.


### POS

This class representing the outside environment that the receipt calculation
runs within. It creates the universe of items upon initialization. Once the
inventory is created there is no API to allow it to be modified.  The `Receipt`
object then can safely hold references to the inventory without the possibility
of race conditions.

#### POS API

- `scan(item: str) -> StockType`
    The POS class's only implemented method, other than the object
    initializer, is this one which takes in the item's code name and returns
    the full information about that item.

As a class with only one implemented method this class should be a candidate for
turning into a stand alone function.  I haven't done that since in a real system
the class would be needed to handle the cash drawer, the scale, networking,
and a myriad of other things beyond handling the inventory data. There would
also be more to starting and ending a receipt in a real system and so this
class would probably be responsible for starting and stopping a receipt. Since
in this kata there is no additional responsibility I have chosen not to
implement management of the reciept lifespan here.  All such a function would
do is call the `Receipt` class's initializer.

### Receipt
    """ This object manages items that are on the receipt. It adds items
        (purchases list) to the receipt and calculates the total spent.  The
        items are held in a dictionary indexed by the item with the value being
        a list of item quantities.

Upon initialization the `Receipt` is passed the POS object which allows an
object of the `Receipt` class to retrieve information from inventory. The
`Receipt` also sets up a dictionary that maps inventory items to list of scans
for that item type.

#### Reciept API
- `add_scan(item_desc: str, qty: SaleQuantity) -> None`
    Add a quantity of an item to the receipt. Will raise a `KeyError` if the
    `item_desc` is not in the inventory or `NotImplementedError` if the
    quantity does not match how the item is sold (e.g. a weight for a
    product sold by item count).  The actions to be taken when these happen
    are not specified the the use cases.

- `__iadd__(item_desc: str) -> Receipt`
    A convenience funtion for adding a single counted item to the
    `Receipt`.  It calls `add_scan` with the quantity of 1.  Being a
    Python double-underscore function Python will call this function when
    a `Receipt` is on the left side of the `+=` operator and a string is
    on the right side.

- `total(self) -> Money`
   Returns the total currently owed on this Receipt object.  When this
   method is called the method iterates over the dictionary that holds all the
   items purchased, sums the list of amounts purchased on each scan,
   and calls the that item's `price` function which calculates the
   amount owed for that item.  The sum of amounts owed for each of the
   items scanned is returned as the receipt's total.

- `remove(item_desc: str, num2remove: SaleQuantity) -> None`
   Removes sales of the item `item_desc` of up to `num2remove` from the
   receipt.  If the item is sold by weight the `SaleQuantity` must be
   a `float`, if sold by item count the `SaleQuantity` must be an
   `int`.  If the item is not on the receipt nothing is removed.  If
   a larger quantity is specified than has been sold the amount on the
   receipt is reduced to zero.

- `remove_last(item_desc: str) -> None`
    This is a convenience function that removes whatever quantity made
    up the last sale of the specified item.  If this method is called
    repeatedly it steps back in history removing prior sales until there
    are no remaining sales of the item. 

# Notes on the development

The first thing I did after selecting the Kata to implement was figure
out what data was going to be needed.  The data elements identified
were then grouped into classes that would own the data elements and
would need similar data items to be owned by the same object.

I then identified the actions that were specified and did an informal
(pen and paper) logic analysis of the actions at a set and set
operations level to identify any missing functions.  This is when I
discovered that there were multiple ways to implement removing
something from the receipt that I discussed above in the Use Case
Problems section.  Other implications of the Use Cases also became
clearer.

The first iteration created a store with a single item at full price,
added it to the receipt and checked that the total was correct.  I
also tested that adding the item several times also generated the
correct total.

Later iterations involved selecting a new Use Case, creating an empty
method, writing a test that called the empty method, and then
implementing the functionality for the method(s) needed for the test
to pass.

Implementation was rather easy and straight forward, and the Use Cases
provided are in the correct order for implementation.  This of course
is not to be expected in the real world.

The final task was a final code quality check and writing this guide to
the API.
