from ..properties import DelegateUser, DLMailbox, UserId  # The service expects a Mailbox element in the MNS namespace
from ..util import MNS, create_element, set_xml_value
from ..version import EXCHANGE_2007_SP1
from .common import EWSAccountService


class GetDelegate(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getdelegate-operation"""

    SERVICE_NAME = "GetDelegate"
    ERRORS_TO_CATCH_IN_RESPONSE = ()
    supported_from = EXCHANGE_2007_SP1

    def call(self, user_ids, include_permissions):
        return self._elems_to_objs(
            self._chunked_get_elements(
                self.get_payload,
                items=user_ids or [None],
                mailbox=DLMailbox(email_address=self.account.primary_smtp_address),
                include_permissions=include_permissions,
            )
        )

    def _elem_to_obj(self, elem):
        return DelegateUser.from_xml(elem=elem, account=self.account)

    def get_payload(self, user_ids, mailbox, include_permissions):
        payload = create_element(f"m:{self.SERVICE_NAME}", attrs=dict(IncludePermissions=include_permissions))
        set_xml_value(payload, mailbox, version=self.protocol.version)
        if user_ids != [None]:
            user_ids_elem = create_element("m:UserIds")
            for user_id in user_ids:
                if isinstance(user_id, str):
                    user_id = UserId(primary_smtp_address=user_id)
                set_xml_value(user_ids_elem, user_id, version=self.protocol.version)
            set_xml_value(payload, user_ids_elem, version=self.protocol.version)
        return payload

    @classmethod
    def _get_elements_in_container(cls, container):
        return container.findall(DelegateUser.response_tag())

    @classmethod
    def _response_message_tag(cls):
        return f"{{{MNS}}}DelegateUserResponseMessageType"
