from ..util import create_element
from .common import EWSAccountService, add_xml_child


class Unsubscribe(EWSAccountService):
    """Unsubscribing is only valid for pull and streaming notifications.

    MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/unsubscribe-operation
    """

    SERVICE_NAME = "Unsubscribe"
    returns_elements = False
    prefer_affinity = True

    def call(self, subscription_id):
        return self._get_elements(payload=self.get_payload(subscription_id=subscription_id))

    def get_payload(self, subscription_id):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        add_xml_child(payload, "m:SubscriptionId", subscription_id)
        return payload
