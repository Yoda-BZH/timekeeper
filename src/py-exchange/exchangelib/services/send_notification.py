from ..errors import InvalidEnumValue
from ..properties import Notification
from ..transport import wrap
from ..util import MNS, create_element
from .common import EWSService, add_xml_child


class SendNotification(EWSService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/sendnotification

    This service is implemented backwards compared to other services. We use it to parse the XML body of push
    notifications we receive on the callback URL defined in a push subscription, and to create responses to these
    push notifications.
    """

    SERVICE_NAME = "SendNotification"
    OK = "OK"
    UNSUBSCRIBE = "Unsubscribe"
    STATUS_CHOICES = (OK, UNSUBSCRIBE)

    def ok_payload(self):
        return wrap(content=self.get_payload(status=self.OK))

    def unsubscribe_payload(self):
        return wrap(content=self.get_payload(status=self.UNSUBSCRIBE))

    def _elem_to_obj(self, elem):
        return Notification.from_xml(elem=elem, account=None)

    @classmethod
    def _response_tag(cls):
        """Return the name of the element containing the service response."""
        return f"{{{MNS}}}{cls.SERVICE_NAME}"

    @classmethod
    def _get_elements_in_container(cls, container):
        return container.findall(Notification.response_tag())

    def get_payload(self, status):
        if status not in self.STATUS_CHOICES:
            raise InvalidEnumValue("status", status, self.STATUS_CHOICES)
        payload = create_element(f"m:{self.SERVICE_NAME}Result")
        add_xml_child(payload, "m:SubscriptionStatus", status)
        return payload
