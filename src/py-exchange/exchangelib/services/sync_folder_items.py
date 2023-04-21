from ..errors import InvalidEnumValue, InvalidTypeError
from ..folders import BaseFolder
from ..properties import ItemId
from ..util import MNS, TNS, peek, xml_text_to_value
from .common import add_xml_child, item_ids_element
from .sync_folder_hierarchy import SyncFolder


class SyncFolderItems(SyncFolder):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/syncfolderitems-operation
    """

    SERVICE_NAME = "SyncFolderItems"
    SYNC_SCOPES = (
        "NormalItems",
        "NormalAndAssociatedItems",
    )
    # Extra change type
    READ_FLAG_CHANGE = "read_flag_change"
    CHANGE_TYPES = SyncFolder.CHANGE_TYPES + (READ_FLAG_CHANGE,)
    shape_tag = "m:ItemShape"
    last_in_range_name = f"{{{MNS}}}IncludesLastItemInRange"
    change_types_map = SyncFolder.change_types_map
    change_types_map[f"{{{TNS}}}ReadFlagChange"] = READ_FLAG_CHANGE

    def call(self, folder, shape, additional_fields, sync_state, ignore, max_changes_returned, sync_scope):
        self.sync_state = sync_state
        if max_changes_returned is None:
            max_changes_returned = self.page_size
        if not isinstance(max_changes_returned, int):
            raise InvalidTypeError("max_changes_returned", max_changes_returned, int)
        if max_changes_returned <= 0:
            raise ValueError(f"'max_changes_returned' {max_changes_returned} must be a positive integer")
        if sync_scope is not None and sync_scope not in self.SYNC_SCOPES:
            raise InvalidEnumValue("sync_scope", sync_scope, self.SYNC_SCOPES)
        return self._elems_to_objs(
            self._get_elements(
                payload=self.get_payload(
                    folder=folder,
                    shape=shape,
                    additional_fields=additional_fields,
                    sync_state=sync_state,
                    ignore=ignore,
                    max_changes_returned=max_changes_returned,
                    sync_scope=sync_scope,
                )
            )
        )

    def _elem_to_obj(self, elem):
        change_type = self.change_types_map[elem.tag]
        if change_type == self.READ_FLAG_CHANGE:
            item = (
                ItemId.from_xml(elem=elem.find(ItemId.response_tag()), account=self.account),
                xml_text_to_value(elem.find(f"{{{TNS}}}IsRead").text, bool),
            )
        elif change_type == self.DELETE:
            item = ItemId.from_xml(elem=elem.find(ItemId.response_tag()), account=self.account)
        else:
            # We can't find() the element because we don't know which tag to look for. The change element can
            # contain multiple item types, each with their own tag.
            item_elem = elem[0]
            item = BaseFolder.item_model_from_tag(item_elem.tag).from_xml(elem=item_elem, account=self.account)
        return change_type, item

    def get_payload(self, folder, shape, additional_fields, sync_state, ignore, max_changes_returned, sync_scope):
        sync_folder_items = self._partial_get_payload(
            folder=folder, shape=shape, additional_fields=additional_fields, sync_state=sync_state
        )
        is_empty, ignore = (True, None) if ignore is None else peek(ignore)
        if not is_empty:
            sync_folder_items.append(item_ids_element(items=ignore, version=self.account.version, tag="m:Ignore"))
        add_xml_child(sync_folder_items, "m:MaxChangesReturned", max_changes_returned)
        if sync_scope:
            add_xml_child(sync_folder_items, "m:SyncScope", sync_scope)
        return sync_folder_items
