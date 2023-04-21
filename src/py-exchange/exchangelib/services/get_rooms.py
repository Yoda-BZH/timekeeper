from ..properties import Room
from ..util import MNS, create_element, set_xml_value
from ..version import EXCHANGE_2010
from .common import EWSService


class GetRooms(EWSService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getrooms-operation"""

    SERVICE_NAME = "GetRooms"
    element_container_name = f"{{{MNS}}}Rooms"
    supported_from = EXCHANGE_2010

    def call(self, room_list):
        return self._elems_to_objs(self._get_elements(payload=self.get_payload(room_list=room_list)))

    def _elem_to_obj(self, elem):
        return Room.from_xml(elem=elem, account=None)

    def get_payload(self, room_list):
        return set_xml_value(create_element(f"m:{self.SERVICE_NAME}"), room_list, version=self.protocol.version)
