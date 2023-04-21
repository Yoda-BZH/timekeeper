import logging

from ..properties import Notification
from ..util import create_element
from .common import EWSAccountService, add_xml_child

log = logging.getLogger(__name__)


class GetEvents(EWSAccountService):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getevents-operation
    """

    SERVICE_NAME = "GetEvents"
    prefer_affinity = True

    def call(self, subscription_id, watermark):
        return self._elems_to_objs(
            self._get_elements(
                payload=self.get_payload(
                    subscription_id=subscription_id,
                    watermark=watermark,
                )
            )
        )

    def _elem_to_obj(self, elem):
        return Notification.from_xml(elem=elem, account=None)

    @classmethod
    def _get_elements_in_container(cls, container):
        return container.findall(Notification.response_tag())

    def get_payload(self, subscription_id, watermark):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        add_xml_child(payload, "m:SubscriptionId", subscription_id)
        add_xml_child(payload, "m:Watermark", watermark)
        return payload
