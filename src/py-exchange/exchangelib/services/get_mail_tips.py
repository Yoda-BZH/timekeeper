from ..properties import MailTips
from ..util import MNS, create_element, set_xml_value
from .common import EWSService


class GetMailTips(EWSService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getmailtips-operation"""

    SERVICE_NAME = "GetMailTips"

    def call(self, sending_as, recipients, mail_tips_requested):
        return self._elems_to_objs(
            self._chunked_get_elements(
                self.get_payload,
                items=recipients,
                sending_as=sending_as,
                mail_tips_requested=mail_tips_requested,
            )
        )

    def _elem_to_obj(self, elem):
        return MailTips.from_xml(elem=elem, account=None)

    def get_payload(self, recipients, sending_as, mail_tips_requested):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        set_xml_value(payload, sending_as, version=self.protocol.version)

        recipients_elem = create_element("m:Recipients")
        for recipient in recipients:
            set_xml_value(recipients_elem, recipient, version=self.protocol.version)
        payload.append(recipients_elem)

        if mail_tips_requested:
            set_xml_value(payload, mail_tips_requested, version=self.protocol.version)
        return payload

    def _get_elements_in_response(self, response):
        for msg in response:
            yield self._get_element_container(message=msg, name=MailTips.response_tag())

    @classmethod
    def _response_message_tag(cls):
        return f"{{{MNS}}}MailTipsResponseMessageType"
