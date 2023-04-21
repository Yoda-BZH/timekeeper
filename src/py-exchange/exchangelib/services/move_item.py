from ..errors import InvalidTypeError
from ..folders import BaseFolder
from ..items import Item
from ..properties import FolderId
from ..util import MNS, create_element
from .common import EWSAccountService, folder_ids_element, item_ids_element


class MoveItem(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/moveitem-operation"""

    SERVICE_NAME = "MoveItem"
    element_container_name = f"{{{MNS}}}Items"

    def call(self, items, to_folder):
        if not isinstance(to_folder, (BaseFolder, FolderId)):
            raise InvalidTypeError("to_folder", to_folder, (BaseFolder, FolderId))
        return self._elems_to_objs(self._chunked_get_elements(self.get_payload, items=items, to_folder=to_folder))

    def _elem_to_obj(self, elem):
        return Item.id_from_xml(elem)

    def get_payload(self, items, to_folder):
        # Takes a list of items and returns their new item IDs
        payload = create_element(f"m:{self.SERVICE_NAME}")
        payload.append(folder_ids_element(folders=[to_folder], version=self.account.version, tag="m:ToFolderId"))
        payload.append(item_ids_element(items=items, version=self.account.version))
        return payload
