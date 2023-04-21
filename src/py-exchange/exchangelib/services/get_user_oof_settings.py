from ..properties import AvailabilityMailbox
from ..settings import OofSettings
from ..util import MNS, TNS, create_element, set_xml_value
from .common import EWSAccountService


class GetUserOofSettings(EWSAccountService):
    """Get automatic reply settings for the specified mailbox.
    MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getuseroofsettings-operation
    """

    SERVICE_NAME = "GetUserOofSettings"
    element_container_name = f"{{{TNS}}}OofSettings"

    def call(self, mailbox):
        return self._elems_to_objs(self._get_elements(payload=self.get_payload(mailbox=mailbox)))

    def _elem_to_obj(self, elem):
        return OofSettings.from_xml(elem=elem, account=self.account)

    def get_payload(self, mailbox):
        return set_xml_value(
            create_element(f"m:{self.SERVICE_NAME}Request"),
            AvailabilityMailbox.from_mailbox(mailbox),
            version=self.account.version,
        )

    @classmethod
    def _get_elements_in_container(cls, container):
        # This service only returns one result, directly in 'container'
        return [container]

    def _get_element_container(self, message, name=None):
        # This service returns the result container outside the response message
        super()._get_element_container(message=message.find(self._response_message_tag()), name=None)
        return message.find(name)

    @classmethod
    def _response_message_tag(cls):
        return f"{{{MNS}}}ResponseMessage"
