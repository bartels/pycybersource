
CC_RESPONSE_CODES = {
        100: "Successful transaction",
        101: "Declined - The request is missing one or more fields",
        102: "Declined - One or more fields in the request contains invalid data",
        104: "Declined - The merchantReferenceCode sent with this authorization request matches the merchantReferenceCode of another authorization request that you sent in the last 15 minutes.",
        110: "Partial amount was approved",
        150: "Error - General system failure.",
        151: "Error - The request was received but there was a server timeout. This error does not include timeouts between the client and the server.",
        152: "Error: The request was received, but a service did not finish running in time.",
        200: "Soft Decline - The authorization request was approved by the issuing bank but declined by CyberSource because it did not pass the Address Verification Service (AVS) check.",
        201: "Decline - The issuing bank has questions about the request. You do not receive an authorization code programmatically, but you might receive one verbally by calling the processor.",
        202: "Decline - Expired card. You might also receive this if the expiration date you provided does not match the date the issuing bank has on file.",
        203: "Decline - General decline of the card. No other information provided by the issuing bank.",
        204: "Decline - Insufficient funds in the account.",
        205: "Decline - Stolen or lost card.",
        207: "Decline - Issuing bank unavailable.",
        208: "Decline - Inactive card or card not authorized for card-not-present transactions.",
        209: "Decline - American Express Card Identification Digits (CID) did not match.",
        210: "Decline - The card has reached the credit limit.",
        211: "Decline - Invalid Card Verification Number (CVN).",
        220: "Decline - Generic Decline.",
        221: "Decline - The customer matched an entry on the processor's negative file.",
        222: "Decline - customer's account is frozen",
        230: "Soft Decline - The authorization request was approved by the issuing bank but declined by CyberSource because it did not pass the card verification number (CVN) check.",
        231: "Decline - Invalid account number",
        232: "Decline - The card type is not accepted by the payment processor.",
        233: "Decline - General decline by the processor.",
        234: "Decline - There is a problem with your CyberSource merchant configuration.",
        235: "Decline - The requested amount exceeds the originally authorized amount. Occurs, for example, if you try to capture an amount larger than the original authorization amount.",
        236: "Decline - Processor failure.",
        237: "Decline - The authorization has already been reversed.",
        238: "Decline - The transaction has already been settled.",
        239: "Decline - The requested transaction amount must match the previous transaction amount.",
        240: "Decline - The card type sent is invalid or does not correlate with the credit card number.",
        241: "Decline - The referenced request id is invalid for all follow-on transactions.",
        242: "Decline - The request ID is invalid. You requested a capture, but there is no corresponding, unused authorization record.",
        243: "Decline - The transaction has already been settled or reversed.",
        246: "Decline - The capture or credit is not voidable because the capture or credit information has already been submitted to your processor. Or, you requested a void for a type of transaction that cannot be voided.",
        247: "Decline - You requested a credit for a capture that was previously voided.",
        248: "Decline - The boleto request was declined by your processor.",
        250: "Error - The request was received, but there was a timeout at the payment processor.",
        251: "Decline - The Pinless Debit card's use frequency or maximum amount per use has been exceeded.",
        254: "Decline - Account is prohibited from processing stand-alone refunds.",
        400: "Soft Decline - Fraud score exceeds threshold.",
        450: "Apartment number missing or not found.",
        451: "Insufficient address information.",
        452: "House/Box number not found on street.",
        453: "Multiple address matches were found.",
        454: "P.O. Box identifier not found or out of range.",
        455: "Route service identifier not found or out of range.",
        456: "Street name not found in Postal code.",
        457: "Postal code not found in database.",
        458: "Unable to verify or correct address.",
        459: "Multiple addres matches were found (international)",
        460: "Address match not found (no reason given)",
        461: "Unsupported character set",
        475: "The cardholder is enrolled in Payer Authentication. Please authenticate the cardholder before continuing with the transaction.",
        476: "Encountered a Payer Authentication problem. Payer could not be authenticated.",
        480: "The order is marked for review by Decision Manager",
        481: "The order has been rejected by Decision Manager",
        520: "Soft Decline - The authorization request was approved by the issuing bank but declined by CyberSource based on your Smart Authorization settings.",
        700: "The customer matched the Denied Parties List",
        701: "Export bill_country/ship_country match",
        702: "Export email_country match",
        703: "Export hostname_country/ip_country match",
}


class CyberSourceResponse(object):
    def __init__(self, raw_response):
        self.raw_response = raw_response

    @property
    def reasonCode(self):
        return self.raw_response.reasonCode

    @property
    def decision(self):
        return unicode(self.raw_response.decision)

    @property
    def success(self):
        return self.reasonCode == 100

    @property
    def requestID(self):
        return unicode(self.raw_response.requestID)

    @property
    def message(self):
        message = unicode(CC_RESPONSE_CODES.get(self.reasonCode, ''))
        if self.reasonCode in (101, 102):
            if hasattr(self.raw_response, 'invalidField'):
                fields = u'Invalid fields: {0}'.format(
                        u', '.join(list(self.raw_response.invalidField)))
                message = u'. '.join([message, fields])
        return message

    def __str__(self):
        return '{0}\n{1}'.format(self.message, self.raw_response)

    def __getattr__(self, name):
        return getattr(self.raw_response, name)
