from sharpy.client import Client
from sharpy.exceptions import NotFound
from sharpy.parsers import PlansParser, CustomersParser, PromotionsParser
from sharpy.product import *


# Get a product instance to work with
product = CheddarProduct(
    username = "tspelde@smartfile.com",
    password = "CELE3Ete",
    product_code = "SMARTFILEBETA",
)

# Get the customer from Cheddar Getter
customers = product.get_customers()


print(customers[0])

