from ..errors import ResponseMessageError
from ..util import MNS, create_element
from .common import EWSAccountService, item_ids_element


class ExportItems(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/exportitems-operation"""

    ERRORS_TO_CATCH_IN_RESPONSE = ResponseMessageError
    SERVICE_NAME = "ExportItems"
    element_container_name = f"{{{MNS}}}Data"

    def call(self, items):
        return self._elems_to_objs(self._chunked_get_elements(self.get_payload, items=items))

    def _elem_to_obj(self, elem):
        return elem.text  # All we want is the 64bit string in the 'Data' tag

    def get_payload(self, items):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        payload.append(item_ids_element(items=items, version=self.account.version))
        return payload

    # We need to override this since ExportItemsResponseMessage is formatted a
    # little bit differently. .
    @classmethod
    def _get_elements_in_container(cls, container):
        return [container]
