import logging

from ..errors import InvalidEnumValue
from ..items import ID_ONLY, ITEM_TRAVERSAL_CHOICES, SHAPE_CHOICES, Persona
from ..util import MNS, create_element, set_xml_value
from ..version import EXCHANGE_2013
from .common import EWSPagingService, folder_ids_element, shape_element

log = logging.getLogger(__name__)


class FindPeople(EWSPagingService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/findpeople-operation"""

    SERVICE_NAME = "FindPeople"
    element_container_name = f"{{{MNS}}}People"
    supported_from = EXCHANGE_2013
    supports_paging = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A hack to communicate parsing args to _elems_to_objs()
        self.additional_fields = None
        self.shape = None

    def call(self, folder, additional_fields, restriction, order_fields, shape, query_string, depth, max_items, offset):
        """Find items in an account. This service can only be called on a single folder.

        :param folder: the Folder object to query
        :param additional_fields: the extra fields that should be returned with the item, as FieldPath objects
        :param restriction: a Restriction object for
        :param order_fields: the fields to sort the results by
        :param shape: The set of attributes to return
        :param query_string: a QueryString object
        :param depth: How deep in the folder structure to search for items
        :param max_items: the max number of items to return
        :param offset: the offset relative to the first item in the item collection. Usually 0.

        :return: XML elements for the matching items
        """
        if shape not in SHAPE_CHOICES:
            raise InvalidEnumValue("shape", shape, SHAPE_CHOICES)
        if depth not in ITEM_TRAVERSAL_CHOICES:
            raise InvalidEnumValue("depth", depth, ITEM_TRAVERSAL_CHOICES)
        self.additional_fields = additional_fields
        self.shape = shape
        return self._elems_to_objs(
            self._paged_call(
                payload_func=self.get_payload,
                max_items=max_items,
                folders=[folder],  # We just need the list to satisfy self._paged_call()
                **dict(
                    additional_fields=additional_fields,
                    restriction=restriction,
                    order_fields=order_fields,
                    query_string=query_string,
                    shape=shape,
                    depth=depth,
                    page_size=self.page_size,
                    offset=offset,
                ),
            )
        )

    def _elem_to_obj(self, elem):
        if self.shape == ID_ONLY and self.additional_fields is None:
            return Persona.id_from_xml(elem)
        return Persona.from_xml(elem, account=self.account)

    def get_payload(
        self, folders, additional_fields, restriction, order_fields, query_string, shape, depth, page_size, offset=0
    ):
        # We actually only support a single folder, but self._paged_call() sends us a list
        payload = create_element(f"m:{self.SERVICE_NAME}", attrs=dict(Traversal=depth))
        payload.append(
            shape_element(
                tag="m:PersonaShape", shape=shape, additional_fields=additional_fields, version=self.account.version
            )
        )
        payload.append(
            create_element(
                "m:IndexedPageItemView", attrs=dict(MaxEntriesReturned=page_size, Offset=offset, BasePoint="Beginning")
            )
        )
        if restriction:
            payload.append(restriction.to_xml(version=self.account.version))
        if order_fields:
            payload.append(set_xml_value(create_element("m:SortOrder"), order_fields, version=self.account.version))
        payload.append(folder_ids_element(folders=folders, version=self.account.version, tag="m:ParentFolderId"))
        if query_string:
            payload.append(query_string.to_xml(version=self.account.version))
        return payload

    @staticmethod
    def _get_paging_values(elem):
        """Find paging values. The paging element from FindPeople is different from other paging containers."""
        item_count = int(elem.find(f"{{{MNS}}}TotalNumberOfPeopleInView").text)
        first_matching = int(elem.find(f"{{{MNS}}}FirstMatchingRowIndex").text)
        first_loaded = int(elem.find(f"{{{MNS}}}FirstLoadedRowIndex").text)
        log.debug(
            "Got page with total items %s, first matching %s, first loaded %s ",
            item_count,
            first_matching,
            first_loaded,
        )
        next_offset = None  # GetPersona does not support fetching more pages
        return item_count, next_offset
