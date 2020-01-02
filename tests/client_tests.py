from copy import copy
from datetime import date, timedelta, datetime
import unittest

from dateutil.tz import tzoffset

from nose.tools import raises, assert_raises
from testconfig import config

from sharpy.client import Client
from sharpy.exceptions import AccessDenied
from sharpy.exceptions import BadRequest
from sharpy.exceptions import CheddarFailure
from sharpy.exceptions import NaughtyGateway
from sharpy.exceptions import NotFound
from sharpy.exceptions import PreconditionFailed
from sharpy.exceptions import UnprocessableEntity

from .testing_tools.decorators import clear_users


class ClientTests(unittest.TestCase):
    client_defaults = {
        'username': config['cheddar']['username'],
        'password': config['cheddar']['password'],
        'product_code': config['cheddar']['product_code'],
        'endpoint': config['cheddar']['endpoint'],
    }

    def get_client(self, **kwargs):
        ''' Helper mthod for instantiating client. '''
        client_kwargs = copy(self.client_defaults)
        client_kwargs.update(kwargs)

        c = Client(**client_kwargs)

        return c

    def try_client(self, **kwargs):
        ''' Helper method for getting client.'''
        args = copy(self.client_defaults)
        args.update(kwargs)
        client = self.get_client(**kwargs)

        self.assertEquals(args['username'], client.username)
        self.assertEquals(self.client_defaults['password'], client.password)
        self.assertEquals(self.client_defaults['product_code'],
                          client.product_code)
        if 'endpoint' in args.keys():
            self.assertEquals(args['endpoint'], client.endpoint)
        else:
            self.assertEquals(client.default_endpoint, client.endpoint)

    def test_basic_init(self):
        ''' Test basic initialization. '''
        self.try_client()

    def test_custom_endpoint_init(self):
        ''' Test initialization with custom endpoint. '''
        self.try_client(endpoint='http://cheddar-test.saaspire.com')

    def try_url_build(self, path, params=None):
        ''' Helper method for client build_url method. '''
        c = self.get_client()
        expected = u'%s/%s/productCode/%s' % (
            c.endpoint,
            path,
            c.product_code,
        )
        if params:
            for key, value in params.items():
                expected = u'%s/%s/%s' % (expected, key, value)

        result = c.build_url(path=path, params=params)

        self.assertEquals(expected, result)

    def test_basic_build_url(self):
        ''' Test basic client build_url. '''
        path = 'users'
        self.try_url_build(path)

    def test_single_param_build_url(self):
        ''' Test client build_url with single parameter. '''
        path = 'users'
        params = {'key': 'value'}
        self.try_url_build(path, params)

    def test_multi_param_build_url(self):
        ''' Test client build_url with multiple parameters. '''
        path = 'users'
        params = {'key1': 'value1', 'key2': 'value2'}
        self.try_url_build(path, params)

    def test_make_request(self):
        ''' Test client make_request method. '''
        path = 'plans/get'
        client = self.get_client()
        response = client.make_request(path)

        self.assertEquals(response.status, 200)

    @raises(AccessDenied)
    def test_make_request_access_denied(self):
        ''' Test client make_request method with bad username. '''
        path = 'plans/get'
        bad_username = self.client_defaults['username'] + '_bad'
        client = self.get_client(username=bad_username)
        client.make_request(path)

    @raises(BadRequest)
    def test_make_request_bad_request(self):
        ''' Attempt to add customer without data. '''
        path = 'customers/new'
        data = {}
        client = self.get_client()
        client.make_request(path, data=data)

    @raises(NotFound)
    def test_make_request_not_found(self):
        ''' Test client make_request method with bad path. '''
        path = 'things-which-dont-exist'
        client = self.get_client()
        client.make_request(path)

    @clear_users
    def test_post_request(self):
        ''' Test client make_request method as HTTP POST. '''
        path = 'customers/new'
        data = {
            'code': 'post_test',
            'firstName': 'post',
            'lastName': 'test',
            'email': 'garbage@saaspire.com',
            'subscription[planCode]': 'FREE_MONTHLY',
        }
        client = self.get_client()
        client.make_request(path, data=data)

    def generate_error_response(self, auxcode=None, path=None, params=None,
                                **overrides):
        '''
        Creates a request to cheddar which should return an error
        with the provided aux code.  See the urls below for details
        on simulating errors and aux codes:
        http://support.cheddargetter.com/kb/api-8/error-simulation
        http://support.cheddargetter.com/kb/api-8/error-handling
        '''
        expiration = date.today() + timedelta(days=180)

        path = path or 'customers/new'

        if auxcode is not None:
            zip_code = '0%d' % auxcode
        else:
            zip_code = '12345'

        data = {
            'code': 'post_test',
            'firstName': 'post',
            'lastName': 'test',
            'email': 'garbage@saaspire.com',
            'subscription[planCode]': 'PAID_MONTHLY',
            'subscription[ccNumber]': '4111111111111111',
            'subscription[ccExpiration]': expiration.strftime('%m/%Y'),
            'subscription[ccCardCode]': '123',
            'subscription[ccFirstName]': 'post',
            'subscription[ccLastName]': 'test',
            'subscription[ccZip]': zip_code,
        }
        data.update(overrides)

        client = self.get_client()
        client.make_request(path, params=params, data=data)

    def assertCheddarError(self, auxcode, expected_exception, path=None,
                           params=None):
        ''' Helper method for verifing a Cheddar Error is raised. '''
        assert_raises(
            expected_exception,
            self.generate_error_response,
            auxcode=auxcode,
            path=path,
            params=params,
        )

    def assertCheddarErrorForAuxCodes(self, auxcodes, expected_exception):
        ''' Helper method for verifing a Cheddar Aux Code Error is raised. '''
        for auxcode in auxcodes:
            self.assertCheddarError(auxcode, expected_exception)

    @clear_users
    def test_cheddar_500s(self):
        ''' Test a 500 HTTP status code on CheddarGetter. '''
        auxcodes = (1000, 1002, 1003)
        expected_exception = CheddarFailure
        self.assertCheddarErrorForAuxCodes(auxcodes, expected_exception)

    @clear_users
    def test_cheddar_400(self):
        '''
        The cheddar docs at
        http://support.cheddargetter.com/kb/api-8/error-handling
        say that this aux code should return a 502 but in practice
        the API returns a 400.  Not sure if this is a bug or typo in the
        docs but for now we're assuming the API is correct.
        '''
        self.assertCheddarError(auxcode=1001, expected_exception=BadRequest)

    @clear_users
    def test_cheddar_401s(self):
        ''' Test a 401 HTTP status code on CheddarGetter. '''
        auxcodes = (2000, 2001, 2002, 2003)
        expected_exception = AccessDenied
        self.assertCheddarErrorForAuxCodes(auxcodes, expected_exception)

    @clear_users
    def test_cheddar_502s(self):
        ''' Test a 502 HTTP status code on CheddarGetter. '''
        auxcodes = (3000, 4000)
        expected_exception = NaughtyGateway
        self.assertCheddarErrorForAuxCodes(auxcodes, expected_exception)

    @clear_users
    def test_cheddar_422s(self):
        ''' Test a 422 HTTP status code on CheddarGetter. '''
        auxcodes = (5000, 5001, 5002, 5003, 6000, 6001, 6002, 7000)
        expected_exception = UnprocessableEntity
        self.assertCheddarErrorForAuxCodes(auxcodes, expected_exception)

    @clear_users
    @raises(PreconditionFailed)
    def test_cheddar_412s(self):
        ''' Test a 412 HTTP status code on CheddarGetter. '''
        self.generate_error_response(auxcode=2345, firstName='')

    def test_format_datetime_with_datetime(self):
        ''' Test client format_datetime method. '''
        client = self.get_client()
        result = client.format_datetime(datetime(
            year=2010, month=9, day=19, hour=20, minute=10, second=39))
        expected = '2010-09-19T20:10:39+00:00'

        self.assertEquals(expected, result)

    def test_format_datetime_with_datetime_with_tz(self):
        ''' Test client format_datetime method with timezone info. '''
        client = self.get_client()
        result = client.format_datetime(datetime(
            year=2010, month=9, day=19, hour=20, minute=10, second=39,
            tzinfo=tzoffset("BRST", -10800)))
        expected = '2010-09-19T23:10:39+00:00'

        self.assertEquals(expected, result)

    def test_format_datetime_with_date(self):
        ''' Test client format_datetime method with date. '''
        client = self.get_client()
        result = client.format_datetime(date(year=2010, month=9, day=19))
        expected = '2010-09-19T00:00:00+00:00'

        self.assertEquals(expected, result)

    def test_format_date_with_now(self):
        ''' Test client format_date method with now. '''
        client = self.get_client()
        result = client.format_date('now')
        expected = 'now'

        self.assertEquals(expected, result)

    def test_format_datetime_with_now(self):
        ''' Test client format_datetime method with now. '''
        client = self.get_client()
        result = client.format_datetime('now')
        expected = 'now'

        self.assertEquals(expected, result)

    @clear_users
    def test_chedder_update_customer_error(self):
        '''
        Test overriding the zipcode so a customer actually gets updated.
        '''
        overrides = {
            'subscription[ccZip]': 12345
        }
        self.generate_error_response(**overrides)

        self.assertCheddarError(
            auxcode=6000,
            expected_exception=UnprocessableEntity,
            path='customers/edit',
            params={'code': 'post_test'}
        )
