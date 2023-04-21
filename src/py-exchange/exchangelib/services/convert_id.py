from ..errors import InvalidEnumValue, InvalidTypeError
from ..properties import ID_FORMATS, AlternateId, AlternatePublicFolderId, AlternatePublicFolderItemId
from ..util import create_element, set_xml_value
from ..version import EXCHANGE_2007_SP1
from .common import EWSService


class ConvertId(EWSService):
    """Take a list of IDs to convert. Returns a list of converted IDs or exception instances, in the same order as the
    input list.

    MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/convertid-operation
    """

    SERVICE_NAME = "ConvertId"
    supported_from = EXCHANGE_2007_SP1
    cls_map = {cls.response_tag(): cls for cls in (AlternateId, AlternatePublicFolderId, AlternatePublicFolderItemId)}

    def call(self, items, destination_format):
        if destination_format not in ID_FORMATS:
            raise InvalidEnumValue("destination_format", destination_format, ID_FORMATS)
        return self._elems_to_objs(
            self._chunked_get_elements(self.get_payload, items=items, destination_format=destination_format)
        )

    def _elem_to_obj(self, elem):
        return self.cls_map[elem.tag].from_xml(elem, account=None)

    def get_payload(self, items, destination_format):
        supported_item_classes = AlternateId, AlternatePublicFolderId, AlternatePublicFolderItemId
        payload = create_element(f"m:{self.SERVICE_NAME}", attrs=dict(DestinationFormat=destination_format))
        item_ids = create_element("m:SourceIds")
        for item in items:
            if not isinstance(item, supported_item_classes):
                raise InvalidTypeError("item", item, supported_item_classes)
            set_xml_value(item_ids, item, version=self.protocol.version)
        payload.append(item_ids)
        return payload

    @classmethod
    def _get_elements_in_container(cls, container):
        # We may have other elements in here, e.g. 'ResponseCode'. Filter away those.
        return (
            container.findall(AlternateId.response_tag())
            + container.findall(AlternatePublicFolderId.response_tag())
            + container.findall(AlternatePublicFolderItemId.response_tag())
        )
