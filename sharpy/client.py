import base64
import logging
from urllib.parse import urlencode
from dateutil.tz import tzutc
import httplib2

from sharpy.exceptions import AccessDenied
from sharpy.exceptions import BadRequest
from sharpy.exceptions import CheddarError
from sharpy.exceptions import CheddarFailure
from sharpy.exceptions import NaughtyGateway
from sharpy.exceptions import NotFound
from sharpy.exceptions import PreconditionFailed
from sharpy.exceptions import UnprocessableEntity

client_log = logging.getLogger('SharpyClient')


class Client(object):
    default_endpoint = 'https://cheddargetter.com/xml'

    def __init__(self, username, password, product_code, cache=None,
                 timeout=None, endpoint=None):
        '''
        username - Your cheddargetter username (probably an email address)
        password - Your cheddargetter password
        product_code - The product code for the product you want to work with
        cache - A file system path or an object which implements the 117
                cache API (optional)
        timeout - Socket level timout in seconds (optional)
        endpoint - An alternate API endpoint (optional)
        '''
        self.username = username
        self.password = password
        self.product_code = product_code
        self.endpoint = endpoint or self.default_endpoint
        self.cache = cache
        self.timeout = timeout

        super(Client, self).__init__()

    def build_url(self, path, params=None):
        '''
        Constructs the url for a cheddar API resource
        '''
        url = '%s/%s/productCode/%s' % (
            self.endpoint,
            path,
            self.product_code,
        )
        if params:
            for key, value in list(params.items()):
                url = '%s/%s/%s' % (url, key, value)

        return url

    def format_datetime(self, to_format):
        if to_format == 'now':
            str_dt = to_format
        else:
            if getattr(to_format, 'tzinfo', None) is not None:
                utc_value = to_format.astimezone(tzutc())
            else:
                utc_value = to_format
            str_dt = utc_value.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        return str_dt

    def format_date(self, to_format):
        if to_format == 'now':
            str_dt = to_format
        else:
            if getattr(to_format, 'tzinfo', None) is not None:
                utc_value = to_format.astimezone(tzutc())
            else:
                utc_value = to_format
            str_dt = utc_value.strftime('%Y-%m-%d')
        return str_dt

    def get_client(self):
        return httplib2.Http(cache=self.cache, timeout=self.timeout)

    def get_auth_headers(self):
        headers = {}
        headers['Authorization'] = "Basic %s" % base64.standard_b64encode(
            (self.username + ':' + self.password).encode('utf-8')
        ).strip().decode("utf-8")
        return headers

    def make_request(self, path, params=None, data=None, method=None):
        '''
        Makes a request to the cheddar api using the authentication and
        configuration settings available.
        '''
        # Setup values
        url = self.build_url(path, params)
        client_log.debug('Requesting:  %s' % url)
        method = method or 'GET'
        body = None
        headers = {}
        cleaned_data = None

        if data:
            method = 'POST'
            body = urlencode(data)
            headers = {
                'content-type':
                    'application/x-www-form-urlencoded; charset=UTF-8',
            }

            # Clean credit card info from when the request gets logged
            # (remove ccv and only show last four of card num)
            cleaned_data = data.copy()
            if 'subscription[ccCardCode]' in cleaned_data:
                del cleaned_data['subscription[ccCardCode]']
            if 'subscription[ccNumber]' in cleaned_data:
                ccNum = cleaned_data['subscription[ccNumber]']
                cleaned_data['subscription[ccNumber]'] = ccNum[-4:]

        client_log.debug('Request Method:  %s' % method)
        client_log.debug('Request Body (Cleaned Data):  %s' % cleaned_data)

        # Setup http client
        h = httplib2.Http(cache=self.cache, timeout=self.timeout)
        # Skip the normal http client behavior and send auth headers
        # immediately to save an http request.

        headers['Authorization'] = "Basic %s" % base64.standard_b64encode(
            (self.username + ':' + self.password).encode('utf-8')
        ).strip().decode("utf-8")
        # Make request
        response, content = h.request(url, method, body=body, headers=headers)
        status = response.status
        client_log.debug('Response Status:  %d' % status)
        client_log.debug('Response Content:  %s' % content)

        if status != 200 and status != 302:
            exception_class = CheddarError
            if status == 401:
                exception_class = AccessDenied
            elif status == 400:
                exception_class = BadRequest
            elif status == 404:
                exception_class = NotFound
            elif status == 412:
                exception_class = PreconditionFailed
            elif status == 500:
                exception_class = CheddarFailure
            elif status == 502:
                exception_class = NaughtyGateway
            elif status == 422:
                exception_class = UnprocessableEntity

            raise exception_class(response, content)

        response.content = content
        return response
