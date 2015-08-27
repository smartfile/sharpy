import random
import string

from copy import copy
from datetime import datetime, timedelta
from decimal import Decimal
import unittest

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from nose.tools import raises
from testconfig import config

from sharpy.product import CheddarProduct
from sharpy.exceptions import NotFound

from testing_tools.decorators import clear_users


class ProductTests(unittest.TestCase):

    client_defaults = {
        'username': config['cheddar']['username'],
        'password': config['cheddar']['password'],
        'product_code': config['cheddar']['product_code'],
        'endpoint': config['cheddar']['endpoint'],
    }

    customer_defaults = {
        'code': 'test',
        'email': 'garbage@saaspire.com',
        'first_name': 'Test',
        'last_name': 'User',
        'plan_code': 'FREE_MONTHLY',
    }

    paypal_defaults = {
        'code': 'test',
        'email': 'garbage@saaspire.com',
        'first_name': 'Test',
        'last_name': 'User',
        'plan_code': 'PAID_MONTHLY',
        'method': 'paypal',
        'cc_first_name': 'Test',
        'cc_last_name': 'User',
        'cc_email': 'garbage@saaspire.com',
        'return_url': 'http://example.com/return',
        'cancel_url': 'http://example.com/cancel',
    }

    exipration = datetime.now() + timedelta(days=180)

    paid_defaults = {
        'cc_number': '4111111111111111',
        'cc_expiration': exipration.strftime('%m/%Y'),
        'cc_card_code': '123',
        'cc_first_name': 'Test',
        'cc_last_name': 'User',
        'cc_company': 'Some Co LLC',
        'cc_country': 'United States',
        'cc_address': '123 Something St',
        'cc_city': 'Someplace',
        'cc_state': 'NY',
        'cc_zip': '12345',
        'plan_code': 'PAID_MONTHLY',
    }

    def get_product(self):
        ''' Helper method for getting product. '''
        product = CheddarProduct(**self.client_defaults)

        return product

    def test_repr(self):
        ''' Test Product __repr__ method. '''
        product = self.get_product()
        expected = u'CheddarProduct: %s' % product.product_code
        result = product.__repr__()

        self.assertEquals(expected, result)

    def test_instantiate_product(self):
        ''' Test product key. '''
        product = self.get_product()

        for key, value in self.client_defaults.items():
            self.assertEquals(value, getattr(product.client, key))

    def test_get_all_plans(self):
        ''' Test product get_all_plans method. '''
        product = self.get_product()

        plans = product.get_all_plans()

        for plan in plans:
            if plan.code == 'FREE_MONTHLY':
                free_plan = plan
            elif plan.code == 'PAID_MONTHLY':
                paid_plan = plan
            elif plan.code == 'TRACKED_MONTHLY':
                tracked_plan = plan

        self.assertEquals('FREE_MONTHLY', free_plan.code)
        self.assertEquals('PAID_MONTHLY', paid_plan.code)
        self.assertEquals('TRACKED_MONTHLY', tracked_plan.code)

    def test_get_plan(self):
        ''' Test product get_plan method with plan code. '''
        product = self.get_product()
        code = 'PAID_MONTHLY'
        plan = product.get_plan(code)

        self.assertEquals(code, plan.code)

    def test_plan_initial_bill_date(self):
        ''' Test plan with initial bill date. '''
        product = self.get_product()
        code = 'PAID_MONTHLY'
        plan = product.get_plan(code)

        expected = datetime.utcnow().date() + relativedelta(months=1)
        result = plan.initial_bill_date

        self.assertEquals(expected, result)

    def get_customer(self, **kwargs):
        ''' Test Product get_customer method with filtering. '''
        customer_data = copy(self.customer_defaults)
        # We need to make unique customers with the same data.
        # Cheddar recomends we pass a garbage field.
        # http://support.cheddargetter.com/discussions/problems/8342-duplicate-post
        # http://support.cheddargetter.com/kb/api-8/error-handling#duplicate
        random_string = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(5))
        customer_data.update({'notes': random_string})
        customer_data.update(kwargs)
        product = self.get_product()

        customer = product.create_customer(**customer_data)

        return customer

    def get_customer_with_items(self, **kwargs):
        ''' Test Product get_customer method with items. '''
        data = copy(self.paid_defaults)
        if 'items' in kwargs.keys():
            items = kwargs['items']
        else:
            items = []
            items.append({'code': 'MONTHLY_ITEM', 'quantity': 3})
            items.append({'code': 'ONCE_ITEM'})

        data['items'] = items
        data['plan_code'] = 'TRACKED_MONTHLY'
        customer = self.get_customer(**data)

        return customer

    @clear_users
    def test_simple_create_customer(self):
        ''' Test Create Customer with only the get_customer helper. '''
        self.get_customer()

    @clear_users
    def test_create_customer_with_company(self):
        ''' Test Create Customer with company name. '''
        self.get_customer(company='Test Co')

    @clear_users
    def test_create_customer_with_meta_data(self):
        ''' Test Create Customer with meta data. '''
        self.get_customer(meta_data={'key_1': 'value_1', 'key2': 'value_2'})

    @clear_users
    def test_create_customer_with_true_vat_exempt(self):
        ''' Test Create Customer with vat exempt true. '''
        self.get_customer(is_vat_exempt=True)

    @clear_users
    def test_create_customer_with_false_vat_exempt(self):
        ''' Test Create Customer with vat exempt false. '''
        self.get_customer(is_vat_exempt=False)

    @clear_users
    def test_create_customer_with_vat_number(self):
        ''' Test Create Customer with vat number. '''
        self.get_customer(vat_number=12345)

    @clear_users
    def test_create_customer_with_notes(self):
        ''' Test Create Customer with notes. '''
        self.get_customer(notes='This is a test note!')

    @clear_users
    def test_create_customer_with_first_contact_datetime(self):
        ''' Test Create Customer with first contact datetime. '''
        self.get_customer(first_contact_datetime=datetime.now())

    @clear_users
    def test_create_customer_with_referer(self):
        ''' Test Create Customer with referer. '''
        self.get_customer(referer='http://saaspire.com/test.html')

    @clear_users
    def test_create_customer_with_campaign_term(self):
        ''' Test Create Customer with campaign term. '''
        self.get_customer(campaign_term='testing')

    @clear_users
    def test_create_customer_with_campaign_name(self):
        ''' Test Create Customer with campaign name. '''
        self.get_customer(campaign_name='testing')

    @clear_users
    def test_create_customer_with_campaign_source(self):
        ''' Test Create Customer with campaign source. '''
        self.get_customer(campaign_source='testing')

    @clear_users
    def test_create_customer_with_campaign_content(self):
        ''' Test Create Customer with campaign content. '''
        self.get_customer(campaign_content='testing')

    @clear_users
    def test_create_customer_with_initial_bill_date(self):
        ''' Test Create Customer with initial bill date. '''
        initial_bill_date = datetime.utcnow() + timedelta(days=60)
        customer = self.get_customer(initial_bill_date=initial_bill_date)
        invoice = customer.subscription.invoices[0]
        real_bill_date = invoice['billing_datetime']

        # Sometimes cheddar getter will push the bill date to the next day
        # if the request is made around UTC midnight
        diff = initial_bill_date.date() - real_bill_date.date()
        self.assertLessEqual(diff.days, 1)

    @clear_users
    def test_create_paid_customer(self):
        ''' Test Create Customer with payment. '''
        self.get_customer(**self.paid_defaults)

    @clear_users
    def test_create_paid_customer_with_charges(self):
        ''' Test Create Customer with payment and additional charges. '''
        data = copy(self.paid_defaults)
        charges = []
        charges.append({'code': 'test_charge_1', 'each_amount': 2})
        charges.append({'code': 'charge2', 'quantity': 3, 'each_amount': 4})
        data['charges'] = charges
        self.get_customer(**data)

    @clear_users
    def test_create_paid_customer_with_decimal_charges(self):
        '''
        Test Create Customer with payment and additional decimal charges.
        '''
        data = copy(self.paid_defaults)
        charges = []
        charges.append({'code': 'test_charge_1',
                        'each_amount': Decimal('2.30')})
        charges.append({'code': 'charge2', 'each_amount': Decimal('-4.5')})
        data['charges'] = charges
        self.get_customer(**data)

    @clear_users
    def test_create_paid_customer_with_items(self):
        ''' Test Create Customer with payment and additional items. '''
        data = copy(self.paid_defaults)
        items = []
        items.append({'code': 'MONTHLY_ITEM', 'quantity': 3})
        items.append({'code': 'ONCE_ITEM'})
        data['items'] = items
        data['plan_code'] = 'TRACKED_MONTHLY'
        self.get_customer(**data)

    @clear_users
    def test_create_paid_customer_with_decimal_quantity_items(self):
        '''
        Test Create Customer with payment and additional decimal quantity
        items.
        '''
        data = copy(self.paid_defaults)
        items = []
        items.append({'code': 'MONTHLY_ITEM', 'quantity': Decimal('1.23456')})
        items.append({'code': 'ONCE_ITEM'})
        data['items'] = items
        data['plan_code'] = 'TRACKED_MONTHLY'
        self.get_customer(**data)

    @clear_users
    def test_create_paypal_customer(self):
        ''' Test Create Customer with paypal. '''
        data = copy(self.paypal_defaults)
        self.get_customer(**data)

    @clear_users
    def test_update_paypal_customer(self):
        ''' Test Update Customer with paypal. '''
        data = copy(self.paypal_defaults)
        customer = self.get_customer(**data)
        customer.update(
            method='paypal',
            return_url='http://example.com/update-success/',
            cancel_url='http://example.com/update-cancel/',
        )

    @clear_users
    def test_customer_repr(self):
        ''' Test Customer __repr__ method. '''
        customer = self.get_customer()

        expected = 'Customer: Test User (test)'
        result = repr(customer)

        self.assertEquals(expected, result)

    @clear_users
    def test_subscription_repr(self):
        ''' Test Subscription __repr__ method. '''
        customer = self.get_customer()
        subscription = customer.subscription

        expected = 'Subscription:'
        result = repr(subscription)

        self.assertIn(expected, result)

    @clear_users
    def test_pricing_plan_repr(self):
        ''' Test PricingPlan __repr__ method. '''
        customer = self.get_customer()
        subscription = customer.subscription
        plan = subscription.plan

        expected = 'PricingPlan: Free Monthly (FREE_MONTHLY)'
        result = repr(plan)

        self.assertEquals(expected, result)

    @clear_users
    def test_item_repr(self):
        ''' Test Item __repr__ method. '''
        customer = self.get_customer_with_items()
        subscription = customer.subscription
        item = subscription.items['MONTHLY_ITEM']

        expected = 'Item: MONTHLY_ITEM for test'
        result = repr(item)

        self.assertEquals(expected, result)

    @clear_users
    def test_get_customers(self):
        ''' Create two customers, verify 2 returned. '''
        self.get_customer()
        customer2_data = copy(self.paid_defaults)
        customer2_data.update({
            'code': 'test2',
            'email': 'garbage+2@saaspire.com',
            'first_name': 'Test2',
            'last_name': 'User2',
        })
        self.get_customer(**customer2_data)
        product = self.get_product()

        fetched_customers = product.get_customers()
        self.assertEquals(2, len(fetched_customers))

    @clear_users
    def test_get_customer(self):
        ''' Test getting a customer by code.. '''
        created_customer = self.get_customer()
        product = self.get_product()

        fetched_customer = product.get_customer(code=created_customer.code)

        self.assertEquals(created_customer.code, fetched_customer.code)
        self.assertEquals(created_customer.first_name,
                          fetched_customer.first_name)
        self.assertEquals(created_customer.last_name,
                          fetched_customer.last_name)
        self.assertEquals(created_customer.email, fetched_customer.email)

    @clear_users
    def test_simple_customer_update(self):
        ''' Test Update Customer. '''
        new_name = 'Different'
        customer = self.get_customer()
        product = self.get_product()

        customer.update(first_name=new_name)
        self.assertEquals(new_name, customer.first_name)

        fetched_customer = product.get_customer(code=customer.code)
        self.assertEquals(customer.first_name, fetched_customer.first_name)

    @clear_users
    @raises(NotFound)
    def test_delete_customer(self):
        ''' Create a Customer and delete that customer. '''
        customer = self.get_customer()
        product = self.get_product()

        fetched_customer = product.get_customer(code=customer.code)
        self.assertEquals(customer.first_name, fetched_customer.first_name)

        customer.delete()
        fetched_customer = product.get_customer(code=customer.code)

    @clear_users
    def test_delete_all_customers(self):
        '''
        Create two customers, verify 2 returned,
        delete and verify 0 customers.
        '''
        self.get_customer()
        self.get_customer(code='test2')
        product = self.get_product()

        # This test fails intermitently. I'm assuming network race condition
        # due to creating customers and fetching all customers so quickly.
        import time
        time.sleep(0.5)
        fetched_customers = product.get_customers()
        self.assertEquals(2, len(fetched_customers))

        product.delete_all_customers()

        fetched_customers = product.get_customers()
        self.assertEquals(0, len(fetched_customers))

    @clear_users
    def test_cancel_subscription(self):
        ''' Test cancel subscription. '''
        customer = self.get_customer()
        customer.subscription.cancel()

        now = datetime.now(tzutc())
        canceled_on = customer.subscription.canceled
        diff = now - canceled_on
        limit = timedelta(seconds=10)

        self.assertLess(diff, limit)

    def assert_increment(self, quantity=None):
        ''' Helper method for asserting increment in other tests. '''
        customer = self.get_customer_with_items()
        product = self.get_product()
        item = customer.subscription.items['MONTHLY_ITEM']

        old_quantity = item.quantity_used
        item.increment(quantity)
        new_quantity = item.quantity_used
        diff = new_quantity - old_quantity
        expected = Decimal(quantity or 1)
        self.assertAlmostEqual(expected, diff, places=2)

        fetched_customer = product.get_customer(code=customer.code)
        fetched_item = fetched_customer.subscription.items[item.code]
        self.assertEquals(item.quantity_used, fetched_item.quantity_used)

    @clear_users
    def test_simple_increment(self):
        ''' Test item increment. '''
        self.assert_increment()

    @clear_users
    def test_int_increment(self):
        ''' Test item increment with integer. '''
        self.assert_increment(1)

    @clear_users
    def test_float_increment(self):
        ''' Test item increment with float. '''
        self.assert_increment(1.234)

    @clear_users
    def test_decimal_increment(self):
        ''' Test item increment with decimal. '''
        self.assert_increment(Decimal('1.234'))

    def assert_decrement(self, quantity=None):
        ''' Helper method for asserting decrement in other tests. '''
        customer = self.get_customer_with_items()
        product = self.get_product()
        item = customer.subscription.items['MONTHLY_ITEM']

        old_quantity = item.quantity_used
        item.decrement(quantity)
        new_quantity = item.quantity_used
        diff = old_quantity - new_quantity
        expected = Decimal(quantity or 1)
        self.assertAlmostEqual(expected, diff, places=2)

        fetched_customer = product.get_customer(code=customer.code)
        fetched_item = fetched_customer.subscription.items[item.code]
        self.assertEquals(item.quantity_used, fetched_item.quantity_used)

    @clear_users
    def test_simple_decrement(self):
        ''' Test item decrement. '''
        self.assert_decrement()

    @clear_users
    def test_int_decrement(self):
        ''' Test item decrement with integer. '''
        self.assert_decrement(1)

    @clear_users
    def test_float_decrement(self):
        ''' Test item decrement with float. '''
        self.assert_decrement(1.234)

    @clear_users
    def test_decimal_decrement(self):
        ''' Test item decrement with decimal. '''
        self.assert_decrement(Decimal('1.234'))

    def assert_set(self, quantity):
        '''
        Helper method for asserting item quantity has been set as expected.
        '''
        customer = self.get_customer_with_items()
        product = self.get_product()
        item = customer.subscription.items['MONTHLY_ITEM']

        item.set(quantity)
        new_quantity = item.quantity_used
        expected = Decimal(quantity)
        self.assertAlmostEqual(expected, new_quantity, places=2)

        fetched_customer = product.get_customer(code=customer.code)
        fetched_item = fetched_customer.subscription.items[item.code]
        self.assertEquals(item.quantity_used, fetched_item.quantity_used)

    @clear_users
    def test_int_set(self):
        ''' Test item set with integer. '''
        self.assert_set(1)

    @clear_users
    def test_float_set(self):
        ''' Test item set with float. '''
        self.assert_set(1.234)

    @clear_users
    def test_decimal_set(self):
        ''' Test item set with decimal. '''
        self.assert_set(Decimal('1.234'))

    def assert_charged(self, code, each_amount, quantity=None,
                       description=None):
        ''' Helper method for asserting custom charges as expected. '''
        customer = self.get_customer(**self.paid_defaults)
        product = self.get_product()

        customer.charge(
            code=code,
            each_amount=each_amount,
            quantity=quantity,
            description=description,
        )

        if description is None:
            description = ''

        found_charge = None
        for invoice in customer.subscription.invoices:
            for charge in invoice['charges']:
                if charge['code'] == code:
                    found_charge = charge

        self.assertAlmostEqual(Decimal(each_amount),
                               found_charge['each_amount'], places=2)
        self.assertEqual(quantity, found_charge['quantity'])
        self.assertEqual(description, found_charge['description'])

        fetched_customer = product.get_customer(code=customer.code)
        fetched_charge = None
        for invoice in fetched_customer.subscription.invoices:
            for charge in invoice['charges']:
                if charge['code'] == code:
                    fetched_charge = charge

        self.assertAlmostEqual(Decimal(each_amount),
                               fetched_charge['each_amount'], places=2)
        self.assertEqual(quantity, fetched_charge['quantity'])
        self.assertEqual(description, fetched_charge['description'])

    @clear_users
    def test_add_charge(self):
        ''' Test adding a custom charge to an invoice. '''
        self.assert_charged(code='TEST-CHARGE', each_amount=1, quantity=1)

    @clear_users
    def test_add_float_charge(self):
        ''' Test adding a custom charge to an invoice with float. '''
        self.assert_charged(code='TEST-CHARGE', each_amount=2.3, quantity=2)

    @clear_users
    def test_add_decimal_charge(self):
        ''' Test adding a custom charge to an invoice with decimal. '''
        self.assert_charged(code='TEST-CHARGE', each_amount=Decimal('2.3'),
                            quantity=3)

    @clear_users
    def test_add_charge_with_descriptions(self):
        ''' Test adding a custom charge to an invoice with descriptions. '''
        self.assert_charged(code='TEST-CHARGE', each_amount=1, quantity=1,
                            description="A test charge")

    @clear_users
    def test_add_credit(self):
        ''' Test adding a custom charge to an invoice as credit. '''
        self.assert_charged(code='TEST-CHARGE', each_amount=-1, quantity=1)

    def assertCharge(self, customer, code, each_amount, quantity,
                     description='', invoice_type=None):
        ''' Helper method for asserting custom charge as expected. '''
        found_charge = None
        for invoice in customer.subscription.invoices:
            if invoice_type is None or invoice['type'] == invoice_type:
                for charge in invoice['charges']:
                    if charge['code'] == code:
                        found_charge = charge

        self.assertAlmostEqual(Decimal(each_amount),
                               found_charge['each_amount'], places=2)
        self.assertEqual(quantity, found_charge['quantity'])
        self.assertEqual(description, found_charge['description'])

    def assertOneTimeInvoice(self, charges):
        ''' Helper method for asserting one time invoice as expected. '''
        customer = self.get_customer(**self.paid_defaults)
        product = self.get_product()

        customer.create_one_time_invoice(charges)

        for charge in charges:
            self.assertCharge(
                customer,
                code=charge['code'],
                quantity=charge['quantity'],
                each_amount=charge['each_amount'],
                description=charge.get('description', ''),
                invoice_type='one-time',
            )

        fetched_customer = product.get_customer(code=customer.code)
        for charge in charges:
            self.assertCharge(
                fetched_customer,
                code=charge['code'],
                quantity=charge['quantity'],
                each_amount=charge['each_amount'],
                description=charge.get('description', ''),
                invoice_type='one-time',
            )

    @clear_users
    def test_add_simple_one_time_invoice(self):
        ''' Test adding a one time invoice. '''
        charges = [
            {
                'code': 'immediate-test',
                'quantity': 1,
                'each_amount': Decimal(5.23)
            }]

        self.assertOneTimeInvoice(charges)

    @clear_users
    def test_add_one_time_invoice_with_description(self):
        ''' Test adding a one time invoice with description. '''
        charges = [
            {
                'code': 'immediate-test',
                'quantity': 1,
                'each_amount': Decimal(5.23),
                'description': 'This is a test charge'
            }]

        self.assertOneTimeInvoice(charges)

    @clear_users
    def test_add_one_time_invoice_with_multiple_charges(self):
        ''' Test adding a one time invoice with multiple charges. '''
        charges = [
            {
                'code': 'immediate-test',
                'quantity': 1,
                'each_amount': Decimal(5.23),
                'description': 'This is a test charge'
            },
            {
                'code': 'immediate-test-2',
                'quantity': 3,
                'each_amount': 15,
                'description': 'This is another test charge'
            }]

        self.assertOneTimeInvoice(charges)

    def test_get_all_promotions(self):
        ''' Test get all promotions. '''
        product = self.get_product()
        promotions = product.get_all_promotions()

        self.assertEquals(2, len(promotions))
        for promotion in promotions:
            assert promotion.coupons[0].get('code') in ('COUPON', 'COUPON2')

    def test_get_promotion(self):
        ''' Test get a single promotion. '''
        product = self.get_product()
        promotion = product.get_promotion('COUPON')

        self.assertEqual(unicode(promotion), 'Coupon (COUPON)')
        self.assertEqual(promotion.name, 'Coupon')
        self.assertEqual(promotion.coupons[0].get('code'), 'COUPON')
        self.assertEqual(promotion.incentives[0].get('percentage'), '10')
        self.assertEqual(promotion.incentives[0].get('expiration_datetime'),
                         None)

    def test_promotion_repr(self):
        ''' Test the internal __repr___ method of Promotion. '''
        product = self.get_product()
        promotion = product.get_promotion('COUPON')

        expected = 'Promotion: Coupon (COUPON)'
        result = repr(promotion)

        self.assertEquals(expected, result)

    def test_promotion_unicode(self):
        ''' Test the internal __unicode___ method of Promotion. '''
        product = self.get_product()
        promotion = product.get_promotion('COUPON')

        expected = 'Coupon (COUPON)'
        result = unicode(promotion)

        self.assertEquals(expected, result)
