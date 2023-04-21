from ..errors import InvalidTypeError
from ..properties import AvailabilityMailbox, Mailbox
from ..settings import OofSettings
from ..util import MNS, create_element, set_xml_value
from .common import EWSAccountService


class SetUserOofSettings(EWSAccountService):
    """Set automatic replies for the specified mailbox.
    MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/setuseroofsettings-operation
    """

    SERVICE_NAME = "SetUserOofSettings"
    returns_elements = False

    def call(self, oof_settings, mailbox):
        if not isinstance(oof_settings, OofSettings):
            raise InvalidTypeError("oof_settings", oof_settings, OofSettings)
        if not isinstance(mailbox, Mailbox):
            raise InvalidTypeError("mailbox", mailbox, Mailbox)
        return self._get_elements(payload=self.get_payload(oof_settings=oof_settings, mailbox=mailbox))

    def get_payload(self, oof_settings, mailbox):
        payload = create_element(f"m:{self.SERVICE_NAME}Request")
        set_xml_value(payload, AvailabilityMailbox.from_mailbox(mailbox), version=self.account.version)
        return set_xml_value(payload, oof_settings, version=self.account.version)

    def _get_element_container(self, message, name=None):
        message = message.find(self._response_message_tag())
        return super()._get_element_container(message=message, name=name)

    @classmethod
    def _response_message_tag(cls):
        return f"{{{MNS}}}ResponseMessage"
