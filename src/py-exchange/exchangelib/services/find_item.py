from ..errors import InvalidEnumValue
from ..folders.base import BaseFolder
from ..items import ID_ONLY, ITEM_TRAVERSAL_CHOICES, SHAPE_CHOICES, Item
from ..util import MNS, TNS, create_element, set_xml_value
from .common import EWSPagingService, folder_ids_element, shape_element


class FindItem(EWSPagingService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/finditem-operation"""

    SERVICE_NAME = "FindItem"
    element_container_name = f"{{{TNS}}}Items"
    paging_container_name = f"{{{MNS}}}RootFolder"
    supports_paging = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A hack to communicate parsing args to _elems_to_objs()
        self.additional_fields = None
        self.shape = None

    def call(
        self,
        folders,
        additional_fields,
        restriction,
        order_fields,
        shape,
        query_string,
        depth,
        calendar_view,
        max_items,
        offset,
    ):
        """Find items in an account.

        :param folders: the folders to act on
        :param additional_fields: the extra fields that should be returned with the item, as FieldPath objects
        :param restriction: a Restriction object for
        :param order_fields: the fields to sort the results by
        :param shape: The set of attributes to return
        :param query_string: a QueryString object
        :param depth: How deep in the folder structure to search for items
        :param calendar_view: If set, returns recurring calendar items unfolded
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
                folders=folders,
                **dict(
                    additional_fields=additional_fields,
                    restriction=restriction,
                    order_fields=order_fields,
                    query_string=query_string,
                    shape=shape,
                    depth=depth,
                    calendar_view=calendar_view,
                    page_size=self.page_size,
                    offset=offset,
                ),
            )
        )

    def _elem_to_obj(self, elem):
        if self.shape == ID_ONLY and self.additional_fields is None:
            return Item.id_from_xml(elem)
        return BaseFolder.item_model_from_tag(elem.tag).from_xml(elem=elem, account=self.account)

    def get_payload(
        self,
        folders,
        additional_fields,
        restriction,
        order_fields,
        query_string,
        shape,
        depth,
        calendar_view,
        page_size,
        offset=0,
    ):
        payload = create_element(f"m:{self.SERVICE_NAME}", attrs=dict(Traversal=depth))
        payload.append(
            shape_element(
                tag="m:ItemShape", shape=shape, additional_fields=additional_fields, version=self.account.version
            )
        )
        if calendar_view is None:
            view_type = create_element(
                "m:IndexedPageItemView", attrs=dict(MaxEntriesReturned=page_size, Offset=offset, BasePoint="Beginning")
            )
        else:
            view_type = calendar_view.to_xml(version=self.account.version)
        payload.append(view_type)
        if restriction:
            payload.append(restriction.to_xml(version=self.account.version))
        if order_fields:
            payload.append(set_xml_value(create_element("m:SortOrder"), order_fields, version=self.account.version))
        payload.append(folder_ids_element(folders=folders, version=self.protocol.version, tag="m:ParentFolderIds"))
        if query_string:
            payload.append(query_string.to_xml(version=self.account.version))
        return payload
