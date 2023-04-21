from ..attachments import FileAttachment, ItemAttachment
from ..items import BaseItem
from ..properties import ParentItemId
from ..util import MNS, create_element, set_xml_value
from .common import EWSAccountService, to_item_id


class CreateAttachment(EWSAccountService):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/createattachment-operation
    """

    SERVICE_NAME = "CreateAttachment"
    element_container_name = f"{{{MNS}}}Attachments"
    cls_map = {cls.response_tag(): cls for cls in (FileAttachment, ItemAttachment)}

    def call(self, parent_item, items):
        return self._elems_to_objs(self._chunked_get_elements(self.get_payload, items=items, parent_item=parent_item))

    def _elem_to_obj(self, elem):
        return self.cls_map[elem.tag].from_xml(elem=elem, account=self.account)

    def get_payload(self, items, parent_item):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        version = self.account.version
        if isinstance(parent_item, BaseItem):
            # to_item_id() would convert this to a normal ItemId, but the service wants a ParentItemId
            parent_item = ParentItemId(parent_item.id, parent_item.changekey)
        set_xml_value(payload, to_item_id(parent_item, ParentItemId), version=self.account.version)
        attachments = create_element("m:Attachments")
        for item in items:
            set_xml_value(attachments, item, version=version)
        payload.append(attachments)
        return payload
