from ..folders.base import BaseFolder
from ..util import MNS, create_element
from .common import EWSAccountService, item_ids_element, shape_element


class GetItem(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getitem-operation"""

    SERVICE_NAME = "GetItem"
    element_container_name = f"{{{MNS}}}Items"

    def call(self, items, additional_fields, shape):
        """Return all items in an account that correspond to a list of ID's, in stable order.

        :param items: a list of (id, changekey) tuples or Item objects
        :param additional_fields: the extra fields that should be returned with the item, as FieldPath objects
        :param shape: The shape of returned objects

        :return: XML elements for the items, in stable order
        """
        return self._elems_to_objs(
            self._chunked_get_elements(
                self.get_payload,
                items=items,
                additional_fields=additional_fields,
                shape=shape,
            )
        )

    def _elem_to_obj(self, elem):
        return BaseFolder.item_model_from_tag(elem.tag).from_xml(elem=elem, account=self.account)

    def get_payload(self, items, additional_fields, shape):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        payload.append(
            shape_element(
                tag="m:ItemShape", shape=shape, additional_fields=additional_fields, version=self.account.version
            )
        )
        payload.append(item_ids_element(items=items, version=self.account.version))
        return payload
