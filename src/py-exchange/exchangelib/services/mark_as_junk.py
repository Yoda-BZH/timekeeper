from ..properties import MovedItemId
from ..util import create_element
from .common import EWSAccountService, item_ids_element


class MarkAsJunk(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/markasjunk-operation"""

    SERVICE_NAME = "MarkAsJunk"

    def call(self, items, is_junk, move_item):
        return self._elems_to_objs(
            self._chunked_get_elements(self.get_payload, items=items, is_junk=is_junk, move_item=move_item)
        )

    def _elem_to_obj(self, elem):
        return MovedItemId.id_from_xml(elem)

    @classmethod
    def _get_elements_in_container(cls, container):
        return container.findall(MovedItemId.response_tag())

    def get_payload(self, items, is_junk, move_item):
        # Takes a list of items and returns either success or raises an error message
        payload = create_element(f"m:{self.SERVICE_NAME}", attrs=dict(IsJunk=is_junk, MoveItem=move_item))
        payload.append(item_ids_element(items=items, version=self.account.version))
        return payload
