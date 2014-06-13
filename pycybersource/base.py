import collections
from decimal import Decimal as D
from suds.client import Client
from suds.wsse import Security, UsernameToken

from pycybersource.config import CyberSourceConfig
from pycybersource.response import CyberSourceResponse


class CyberSource(object):
    """
    Light suds wrapper around the with the Cybersource SOAP API
    """

    def __init__(self, config):
        self.config = self.init_config(config)
        self.client = self.init_client()

    def init_config(self, config):
        if isinstance(config, CyberSourceConfig):
            return config
        elif isinstance(config, collections.Mapping):
            return CyberSourceConfig(**config)
        else:
            raise ValueError(
                    "config must be a CyberSourceConfig instance or a dict")

    def init_client(self):
        client = Client(self.config.wsdl_url)

        # Add wsse security
        security = Security()
        token = UsernameToken(username=self.config.merchant_id,
                              password=self.config.api_key)
        security.tokens.append(token)
        client.set_options(wsse=security)
        return client

    def _build_service_data(self, serviceType, **kwargs):
        """
        Because each service can have differnt options, we delegate building
        the options to methods for each service type.
        """
        try:
            method = getattr(self, '_build_{0}'.format(serviceType))
            return method(**kwargs)
        except AttributeError:
            raise ValueError("{0} is not a valid service".format(serviceType))

    def _build_ccAuthService(self, **kwargs):
        # service
        ccAuthService = self.client.factory.create(
                                    'ns0:ccAuthService')
        ccAuthService._run = 'true'

        # payment info
        payment = self._build_payment(**kwargs['payment'])

        # card info
        card = self._build_card(**kwargs['card'])

        # billing
        billTo = self._build_bill_to(**kwargs['billTo'])

        return {
            'ccAuthService': ccAuthService,
            'purchaseTotals': payment,
            'card': card,
            'billTo': billTo,
        }
        return ccAuthService

    def _build_ccCaptureService(self, **kwargs):
        # service
        ccCaptureService = self.client.factory.create(
                                    'ns0:ccCaptureService')
        ccCaptureService.authRequestID = kwargs['authRequestID']
        ccCaptureService._run = 'true'

        # payment info
        payment = self._build_payment(**kwargs['payment'])

        return {
            'ccCaptureService': ccCaptureService,
            'purchaseTotals': payment,
        }

    def _build_ccSale(self, **kwargs):
        # auth
        ccAuthServiceOptions = self._build_ccAuthService(**kwargs)
        ccCaptureService = self.client.factory.create(
                                    'ns0:ccCaptureService')
        # capture
        ccCaptureService = self.client.factory.create(
                                    'ns0:ccCaptureService')
        ccCaptureService._run = 'true'

        options = {}
        options.update(ccAuthServiceOptions)
        options.update({
            'ccCaptureService': ccCaptureService
        })
        return options

    def _build_payment(self, total, currency):
        """
        kwargs:
        total: the total payment amount
        currency: the payment currency (e.g. USD)
        """
        payment = self.client.factory.create('ns0:PurchaseTotals')
        payment.currency = currency
        payment.grandTotalAmount = D(total)
        return payment

    def _build_card(self,
                    accountNumber,
                    expirationMonth,
                    expirationYear,
                    cvNumber=None):

        card = self.client.factory.create('ns0:Card')
        card.accountNumber = accountNumber
        card.expirationMonth = expirationMonth
        card.expirationYear = expirationYear

        if cvNumber:
            card.cvIndicator = 1
            card.cvNumber = cvNumber

        return card

    def _build_bill_to(self,
                       firstName,
                       lastName,
                       email,
                       country,
                       state,
                       city,
                       postalCode,
                       street1,
                       street2=None):
        billTo = self.client.factory.create('ns0:BillTo')
        billTo.firstName = firstName
        billTo.lastName = lastName
        billTo.email = email
        billTo.country = country
        billTo.city = city
        billTo.state = state
        billTo.postalCode = postalCode
        billTo.street1 = street1
        billTo.street2 = street2

        return billTo

    def run_transaction(self, serviceType, **kwargs):
        """
        Builds the SOAP transaction and returns a response.
        """
        # build request options
        options = {
            'merchantID': self.config.merchant_id,
            'merchantReferenceCode': kwargs['referenceCode'],
        }

        # Each service may have different options
        service_options = self._build_service_data(serviceType, **kwargs)
        options.update(service_options)

        response = self.client.service.runTransaction(**options)

        return CyberSourceResponse(response)

    # SOAP API calls below
    def ccAuth(self, referenceCode, payment, card, billTo, **kwargs):
        """
        Do a credit card auth transaction. Use this to crate a card auth, which
        can later be captured to charge the card.
        """
        kwargs.update(dict(
            referenceCode=referenceCode,
            payment=payment,
            card=card,
            billTo=billTo))
        return self.run_transaction('ccAuthService', **kwargs)

    def ccCapture(self, referenceCode, authRequestID, payment, **kwargs):
        """
        Do a credit card capture, based on a previous auth.
        """
        kwargs.update(dict(
            referenceCode=referenceCode,
            authRequestID=authRequestID,
            payment=payment))
        return self.run_transaction('ccCaptureService', **kwargs)

    def ccSale(self, referenceCode, payment, card, billTo, **kwargs):
        """
        Do an auth and an immediate capture. Use this for an immediate charge.
        """
        kwargs.update(dict(
            referenceCode=referenceCode,
            payment=payment,
            card=card,
            billTo=billTo))
        return self.run_transaction('ccSale', **kwargs)
