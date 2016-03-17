import httplib2
from time import time

from tests.testconfig import config


def clear_users():
    username = config['cheddar']['username']
    password = config['cheddar']['password']
    product = config['cheddar']['product_code']
    endpoint = config['cheddar']['endpoint']

    h = httplib2.Http()
    h.add_credentials(username, password)

    url = '%s/customers/delete-all/confirm/%d/productCode/%s' % (endpoint,
                                                                 int(time()),
                                                                 product)

    response, content = h.request(url, 'POST')

    if response.status != 200 or 'success' not in content:
        raise Exception(
            'Could not clear users. Recieved a response of %s %s \n %s' % (
                response.status, response.reason, content))
