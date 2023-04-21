import abc
import logging

from ..properties import FolderId
from ..util import MNS, TNS, create_element, xml_text_to_value
from .common import EWSPagingService, add_xml_child, folder_ids_element, parse_folder_elem, shape_element

log = logging.getLogger(__name__)


class SyncFolder(EWSPagingService, metaclass=abc.ABCMeta):
    """Base class for SyncFolderHierarchy and SyncFolderItems."""

    element_container_name = f"{{{MNS}}}Changes"
    # Change types
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    CHANGE_TYPES = (CREATE, UPDATE, DELETE)
    shape_tag = None
    last_in_range_name = None
    change_types_map = {
        f"{{{TNS}}}Create": CREATE,
        f"{{{TNS}}}Update": UPDATE,
        f"{{{TNS}}}Delete": DELETE,
    }

    def __init__(self, *args, **kwargs):
        # These values are reset and set each time call() is consumed
        self.sync_state = None
        self.includes_last_item_in_range = None
        super().__init__(*args, **kwargs)

    def _get_element_container(self, message, name=None):
        self.sync_state = message.find(f"{{{MNS}}}SyncState").text
        log.debug("Sync state is: %s", self.sync_state)
        self.includes_last_item_in_range = xml_text_to_value(message.find(self.last_in_range_name).text, bool)
        log.debug("Includes last item in range: %s", self.includes_last_item_in_range)
        return super()._get_element_container(message=message, name=name)

    def _partial_get_payload(self, folder, shape, additional_fields, sync_state):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        payload.append(
            shape_element(
                tag=self.shape_tag, shape=shape, additional_fields=additional_fields, version=self.account.version
            )
        )
        payload.append(folder_ids_element(folders=[folder], version=self.account.version, tag="m:SyncFolderId"))
        if sync_state:
            add_xml_child(payload, "m:SyncState", sync_state)
        return payload


class SyncFolderHierarchy(SyncFolder):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/syncfolderhierarchy-operation
    """

    SERVICE_NAME = "SyncFolderHierarchy"
    shape_tag = "m:FolderShape"
    last_in_range_name = f"{{{MNS}}}IncludesLastFolderInRange"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = None  # A hack to communicate parsing args to _elems_to_objs()

    def call(self, folder, shape, additional_fields, sync_state):
        self.sync_state = sync_state
        self.folder = folder
        return self._elems_to_objs(
            self._get_elements(
                payload=self.get_payload(
                    folder=folder,
                    shape=shape,
                    additional_fields=additional_fields,
                    sync_state=sync_state,
                )
            )
        )

    def _elem_to_obj(self, elem):
        change_type = self.change_types_map[elem.tag]
        if change_type == self.DELETE:
            folder = FolderId.from_xml(elem=elem.find(FolderId.response_tag()), account=self.account)
        else:
            # We can't find() the element because we don't know which tag to look for. The change element can
            # contain multiple folder types, each with their own tag.
            folder_elem = elem[0]
            folder = parse_folder_elem(elem=folder_elem, folder=self.folder, account=self.account)
        return change_type, folder

    def get_payload(self, folder, shape, additional_fields, sync_state):
        return self._partial_get_payload(
            folder=folder, shape=shape, additional_fields=additional_fields, sync_state=sync_state
        )
