from ..properties import RoomList
from ..util import MNS, create_element
from ..version import EXCHANGE_2010
from .common import EWSService


class GetRoomLists(EWSService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getroomlists-operation"""

    SERVICE_NAME = "GetRoomLists"
    element_container_name = f"{{{MNS}}}RoomLists"
    supported_from = EXCHANGE_2010

    def call(self):
        return self._elems_to_objs(self._get_elements(payload=self.get_payload()))

    def _elem_to_obj(self, elem):
        return RoomList.from_xml(elem=elem, account=None)

    def get_payload(self):
        return create_element(f"m:{self.SERVICE_NAME}")
