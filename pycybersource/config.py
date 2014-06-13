from os import path
import ConfigParser


TEST_URL = 'https://ics2wstest.ic3.com/commerce/1.x/transactionProcessor'
PRODUCTION_URL = 'https://ics2ws.ic3.com/commerce/1.x/transactionProcessor'
WSDL_URL = '{0}/CyberSourceTransaction_1.100.wsdl'


class CyberSourceConfig(object):
    """
    Configuration object for CyberSource
    """
    def __init__(self, merchant_id, api_key, test_mode=True, **kwargs):
        self.merchant_id = merchant_id.strip()
        self.api_key = api_key.strip()
        self.test_mode = test_mode

        self.service_url = kwargs.get('service_url')
        if self.service_url is None:
            if self.test_mode:
                self.service_url = TEST_URL
            else:
                self.service_url = PRODUCTION_URL

        self.wsdl_url = kwargs.get('wsdl_url',
                                   WSDL_URL.format(self.service_url))


def get_config_from_file(config_path=None, **kwargs):
    config = ConfigParser.RawConfigParser()
    if config_path is None:
        config.read(['.cybersource', path.expanduser('~/.cybersource')])
    else:
        config.read(config_path)

    if not config.has_section('cybersource'):
        return None

    options = dict(config.items('cybersource'))
    if 'merchant_id' not in options:
        raise RuntimeError("'merchant_id' not found in .cybersource")
    if 'api_key' not in options:
        raise RuntimeError("'api_key' not found in .cybersource")
    return CyberSourceConfig(**options)
