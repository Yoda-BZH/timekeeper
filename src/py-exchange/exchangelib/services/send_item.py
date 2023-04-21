from ..errors import InvalidTypeError
from ..folders import BaseFolder
from ..properties import FolderId
from ..util import create_element
from .common import EWSAccountService, folder_ids_element, item_ids_element


class SendItem(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/senditem-operation"""

    SERVICE_NAME = "SendItem"
    returns_elements = False

    def call(self, items, saved_item_folder):
        if saved_item_folder and not isinstance(saved_item_folder, (BaseFolder, FolderId)):
            raise InvalidTypeError("saved_item_folder", saved_item_folder, (BaseFolder, FolderId))
        return self._chunked_get_elements(self.get_payload, items=items, saved_item_folder=saved_item_folder)

    def get_payload(self, items, saved_item_folder):
        payload = create_element(f"m:{self.SERVICE_NAME}", attrs=dict(SaveItemToFolder=bool(saved_item_folder)))
        payload.append(item_ids_element(items=items, version=self.account.version))
        if saved_item_folder:
            payload.append(
                folder_ids_element(folders=[saved_item_folder], version=self.account.version, tag="m:SavedItemFolderId")
            )
        return payload
