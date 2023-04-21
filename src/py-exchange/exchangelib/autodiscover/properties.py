from ..errors import AutoDiscoverFailed, ErrorNonExistentMailbox
from ..fields import (
    BooleanField,
    BuildField,
    Choice,
    ChoiceField,
    EmailAddressField,
    EWSElementField,
    IntegerField,
    OnOffField,
    ProtocolListField,
    TextField,
)
from ..properties import EWSElement
from ..transport import BASIC, CBA, DEFAULT_ENCODING, GSSAPI, NOAUTH, NTLM, SSPI
from ..util import AUTODISCOVER_BASE_NS, AUTODISCOVER_REQUEST_NS
from ..util import AUTODISCOVER_RESPONSE_NS as RNS
from ..util import ParseError, add_xml_child, create_element, is_xml, to_xml, xml_to_str
from ..version import Version


class AutodiscoverBase(EWSElement):
    NAMESPACE = RNS


class User(AutodiscoverBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/user-pox"""

    ELEMENT_NAME = "User"

    display_name = TextField(field_uri="DisplayName", namespace=RNS)
    legacy_dn = TextField(field_uri="LegacyDN", namespace=RNS)
    deployment_id = TextField(field_uri="DeploymentId", namespace=RNS)  # GUID format
    autodiscover_smtp_address = EmailAddressField(field_uri="AutoDiscoverSMTPAddress", namespace=RNS)


class IntExtUrlBase(AutodiscoverBase):
    external_url = TextField(field_uri="ExternalUrl", namespace=RNS)
    internal_url = TextField(field_uri="InternalUrl", namespace=RNS)


class AddressBook(IntExtUrlBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/addressbook-pox"""

    ELEMENT_NAME = "AddressBook"


class MailStore(IntExtUrlBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/mailstore-pox"""

    ELEMENT_NAME = "MailStore"


class NetworkRequirements(AutodiscoverBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/networkrequirements-pox"""

    ELEMENT_NAME = "NetworkRequirements"

    ipv4_start = TextField(field_uri="IPv4Start", namespace=RNS)
    ipv4_end = TextField(field_uri="IPv4End", namespace=RNS)
    ipv6_start = TextField(field_uri="IPv6Start", namespace=RNS)
    ipv6_end = TextField(field_uri="IPv6End", namespace=RNS)


class SimpleProtocol(AutodiscoverBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/protocol-pox

    Used for the 'Internal' and 'External' elements that may contain a stripped-down version of the Protocol element.
    """

    ELEMENT_NAME = "Protocol"
    WEB = "WEB"
    EXCH = "EXCH"
    EXPR = "EXPR"
    EXHTTP = "EXHTTP"
    TYPES = (WEB, EXCH, EXPR, EXHTTP)

    type = ChoiceField(field_uri="Type", choices={Choice(c) for c in TYPES}, namespace=RNS)
    as_url = TextField(field_uri="ASUrl", namespace=RNS)


class IntExtBase(AutodiscoverBase):
    # TODO: 'OWAUrl' also has an AuthenticationMethod enum-style XML attribute with values:
    #  WindowsIntegrated, FBA, NTLM, Digest, Basic
    owa_url = TextField(field_uri="OWAUrl", namespace=RNS)
    protocol = EWSElementField(value_cls=SimpleProtocol)


class Internal(IntExtBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/internal-pox"""

    ELEMENT_NAME = "Internal"


class External(IntExtBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/external-pox"""

    ELEMENT_NAME = "External"


class Protocol(SimpleProtocol):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/protocol-pox"""

    # Attribute 'Type' is ignored here. Has a name conflict with the child element and does not seem useful.
    version = TextField(field_uri="Version", is_attribute=True, namespace=RNS)
    internal = EWSElementField(value_cls=Internal)
    external = EWSElementField(value_cls=External)
    ttl = IntegerField(field_uri="TTL", namespace=RNS, default=1)  # TTL for this autodiscover response, in hours
    server = TextField(field_uri="Server", namespace=RNS)
    server_dn = TextField(field_uri="ServerDN", namespace=RNS)
    server_version = BuildField(field_uri="ServerVersion", namespace=RNS)
    mdb_dn = TextField(field_uri="MdbDN", namespace=RNS)
    public_folder_server = TextField(field_uri="PublicFolderServer", namespace=RNS)
    port = IntegerField(field_uri="Port", namespace=RNS, min=1, max=65535)
    directory_port = IntegerField(field_uri="DirectoryPort", namespace=RNS, min=1, max=65535)
    referral_port = IntegerField(field_uri="ReferralPort", namespace=RNS, min=1, max=65535)
    ews_url = TextField(field_uri="EwsUrl", namespace=RNS)
    emws_url = TextField(field_uri="EmwsUrl", namespace=RNS)
    sharing_url = TextField(field_uri="SharingUrl", namespace=RNS)
    ecp_url = TextField(field_uri="EcpUrl", namespace=RNS)
    ecp_url_um = TextField(field_uri="EcpUrl-um", namespace=RNS)
    ecp_url_aggr = TextField(field_uri="EcpUrl-aggr", namespace=RNS)
    ecp_url_mt = TextField(field_uri="EcpUrl-mt", namespace=RNS)
    ecp_url_ret = TextField(field_uri="EcpUrl-ret", namespace=RNS)
    ecp_url_sms = TextField(field_uri="EcpUrl-sms", namespace=RNS)
    ecp_url_publish = TextField(field_uri="EcpUrl-publish", namespace=RNS)
    ecp_url_photo = TextField(field_uri="EcpUrl-photo", namespace=RNS)
    ecp_url_tm = TextField(field_uri="EcpUrl-tm", namespace=RNS)
    ecp_url_tm_creating = TextField(field_uri="EcpUrl-tmCreating", namespace=RNS)
    ecp_url_tm_hiding = TextField(field_uri="EcpUrl-tmHiding", namespace=RNS)
    ecp_url_tm_editing = TextField(field_uri="EcpUrl-tmEditing", namespace=RNS)
    ecp_url_extinstall = TextField(field_uri="EcpUrl-extinstall", namespace=RNS)
    oof_url = TextField(field_uri="OOFUrl", namespace=RNS)
    oab_url = TextField(field_uri="OABUrl", namespace=RNS)
    um_url = TextField(field_uri="UMUrl", namespace=RNS)
    ews_partner_url = TextField(field_uri="EwsPartnerUrl", namespace=RNS)
    login_name = TextField(field_uri="LoginName", namespace=RNS)
    domain_required = OnOffField(field_uri="DomainRequired", namespace=RNS)
    domain_name = TextField(field_uri="DomainName", namespace=RNS)
    spa = OnOffField(field_uri="SPA", namespace=RNS, default=True)
    auth_package = ChoiceField(
        field_uri="AuthPackage",
        namespace=RNS,
        choices={Choice(c) for c in ("basic", "kerb", "kerbntlm", "ntlm", "certificate", "negotiate", "nego2")},
    )
    cert_principal_name = TextField(field_uri="CertPrincipalName", namespace=RNS)
    ssl = OnOffField(field_uri="SSL", namespace=RNS, default=True)
    auth_required = OnOffField(field_uri="AuthRequired", namespace=RNS, default=True)
    use_pop_path = OnOffField(field_uri="UsePOPAuth", namespace=RNS)
    smtp_last = OnOffField(field_uri="SMTPLast", namespace=RNS, default=False)
    network_requirements = EWSElementField(value_cls=NetworkRequirements)
    address_book = EWSElementField(value_cls=AddressBook)
    mail_store = EWSElementField(value_cls=MailStore)

    @property
    def auth_type(self):
        # Translates 'auth_package' value to our own 'auth_type' enum vals
        if not self.auth_required:
            return NOAUTH
        if not self.auth_package:
            return None
        return {
            # Missing in list are DIGEST and OAUTH2
            "basic": BASIC,
            "kerb": GSSAPI,
            "kerbntlm": NTLM,  # Means client can chose between NTLM and GSSAPI
            "ntlm": NTLM,
            "certificate": CBA,
            "negotiate": SSPI,  # Unsure about this one
            "nego2": GSSAPI,
            "anonymous": NOAUTH,  # Seen in some docs even though it's not mentioned in MSDN
        }.get(self.auth_package.lower())


class Error(EWSElement):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/error-pox"""

    ELEMENT_NAME = "Error"
    NAMESPACE = AUTODISCOVER_BASE_NS

    id = TextField(field_uri="Id", namespace=AUTODISCOVER_BASE_NS, is_attribute=True)
    time = TextField(field_uri="Time", namespace=AUTODISCOVER_BASE_NS, is_attribute=True)
    code = TextField(field_uri="ErrorCode", namespace=AUTODISCOVER_BASE_NS)
    message = TextField(field_uri="Message", namespace=AUTODISCOVER_BASE_NS)
    debug_data = TextField(field_uri="DebugData", namespace=AUTODISCOVER_BASE_NS)


class Account(AutodiscoverBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/account-pox"""

    ELEMENT_NAME = "Account"
    REDIRECT_URL = "redirectUrl"
    REDIRECT_ADDR = "redirectAddr"
    SETTINGS = "settings"
    ACTIONS = (REDIRECT_URL, REDIRECT_ADDR, SETTINGS)

    type = ChoiceField(field_uri="AccountType", namespace=RNS, choices={Choice("email")})
    action = ChoiceField(field_uri="Action", namespace=RNS, choices={Choice(p) for p in ACTIONS})
    microsoft_online = BooleanField(field_uri="MicrosoftOnline", namespace=RNS)
    redirect_url = TextField(field_uri="RedirectURL", namespace=RNS)
    redirect_address = EmailAddressField(field_uri="RedirectAddr", namespace=RNS)
    image = TextField(field_uri="Image", namespace=RNS)  # Path to image used for branding
    service_home = TextField(field_uri="ServiceHome", namespace=RNS)  # URL to website of ISP
    protocols = ProtocolListField()
    # 'SmtpAddress' is inside the 'PublicFolderInformation' element
    public_folder_smtp_address = TextField(field_uri="SmtpAddress", namespace=RNS)

    @classmethod
    def from_xml(cls, elem, account):
        kwargs = {}
        public_folder_information = elem.find(f"{{{cls.NAMESPACE}}}PublicFolderInformation")
        for f in cls.FIELDS:
            if f.name == "public_folder_smtp_address":
                if public_folder_information is None:
                    continue
                kwargs[f.name] = f.from_xml(elem=public_folder_information, account=account)
                continue
            kwargs[f.name] = f.from_xml(elem=elem, account=account)
        cls._clear(elem)
        return cls(**kwargs)


class Response(AutodiscoverBase):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/response-pox"""

    ELEMENT_NAME = "Response"

    user = EWSElementField(value_cls=User)
    account = EWSElementField(value_cls=Account)

    @property
    def redirect_address(self):
        try:
            if self.account.action != Account.REDIRECT_ADDR:
                return None
            return self.account.redirect_address
        except AttributeError:
            return None

    @property
    def redirect_url(self):
        try:
            if self.account.action != Account.REDIRECT_URL:
                return None
            return self.account.redirect_url
        except AttributeError:
            return None

    @property
    def autodiscover_smtp_address(self):
        # AutoDiscoverSMTPAddress might not be present in the XML. In this case, use the original email address.
        try:
            if self.account.action != Account.SETTINGS:
                return None
            return self.user.autodiscover_smtp_address
        except AttributeError:
            return None

    @property
    def version(self):
        # Get the server version. Not all protocol entries have a server version so we cheat a bit and also look at the
        # other ones that point to the same endpoint.
        ews_url = self.protocol.ews_url
        for protocol in self.account.protocols:
            if not protocol.ews_url or not protocol.server_version:
                continue
            if protocol.ews_url.lower() == ews_url.lower():
                return Version(build=protocol.server_version)
        return None

    @property
    def protocol(self):
        """Return the protocol containing an EWS URL.

        A response may contain a number of possible protocol types. EXPR is meant for EWS. See
        https://techcommunity.microsoft.com/t5/blogs/blogarticleprintpage/blog-id/Exchange/article-id/16

        We allow fallback to EXCH if EXPR is not available, to support installations where EXPR is not available.

        Additionally, some responses may contain an EXPR with no EWS URL. In that case, return EXCH, if available.
        """
        protocols = {p.type: p for p in self.account.protocols if p.ews_url}
        if Protocol.EXPR in protocols:
            return protocols[Protocol.EXPR]
        if Protocol.EXCH in protocols:
            return protocols[Protocol.EXCH]
        raise ValueError(
            f"No EWS URL found in any of the available protocols: {[str(p) for p in self.account.protocols]}"
        )


class ErrorResponse(EWSElement):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/response-pox

    Like 'Response', but with a different namespace.
    """

    ELEMENT_NAME = "Response"
    NAMESPACE = AUTODISCOVER_BASE_NS

    error = EWSElementField(value_cls=Error)


class Autodiscover(EWSElement):
    ELEMENT_NAME = "Autodiscover"
    NAMESPACE = AUTODISCOVER_BASE_NS

    response = EWSElementField(value_cls=Response)
    error_response = EWSElementField(value_cls=ErrorResponse)

    @staticmethod
    def _clear(elem):
        # Parent implementation also clears the parent, but this element doesn't have one.
        elem.clear()

    @classmethod
    def from_bytes(cls, bytes_content):
        """Create an instance from response bytes. An Autodiscover request and response example is available at:
        https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/pox-autodiscover-response-for-exchange

        :param bytes_content:
        :return:
        """
        if not is_xml(bytes_content):
            raise ParseError(f"Response is not XML: {bytes_content}", "<not from file>", -1, 0)
        root = to_xml(bytes_content).getroot()  # May raise ParseError
        if root.tag != cls.response_tag():
            raise ParseError(f"Unknown root element in XML: {bytes_content}", "<not from file>", -1, 0)
        return cls.from_xml(elem=root, account=None)

    def raise_errors(self):
        # Find an error message in the response and raise the relevant exception
        try:
            errorcode = self.error_response.error.code
            message = self.error_response.error.message
            if message in ("The e-mail address cannot be found.", "The email address can't be found."):
                raise ErrorNonExistentMailbox("The SMTP address has no mailbox associated with it")
            raise AutoDiscoverFailed(f"Unknown error {errorcode}: {message}")
        except AttributeError:
            raise AutoDiscoverFailed(f"Unknown autodiscover error response: {self.error_response}")

    @staticmethod
    def payload(email):
        # Builds a full Autodiscover XML request
        payload = create_element("Autodiscover", attrs=dict(xmlns=AUTODISCOVER_REQUEST_NS))
        request = create_element("Request")
        add_xml_child(request, "EMailAddress", email)
        add_xml_child(request, "AcceptableResponseSchema", RNS)
        payload.append(request)
        return xml_to_str(payload, encoding=DEFAULT_ENCODING, xml_declaration=True)
