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

# The solution

Code is in the src directory.
