from ..errors import InvalidEnumValue
from ..items import DELETE_TYPE_CHOICES
from ..util import create_element
from .common import EWSAccountService, folder_ids_element


class EmptyFolder(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/emptyfolder-operation"""

    SERVICE_NAME = "EmptyFolder"
    returns_elements = False

    def call(self, folders, delete_type, delete_sub_folders):
        if delete_type not in DELETE_TYPE_CHOICES:
            raise InvalidEnumValue("delete_type", delete_type, DELETE_TYPE_CHOICES)
        return self._chunked_get_elements(
            self.get_payload, items=folders, delete_type=delete_type, delete_sub_folders=delete_sub_folders
        )

    def get_payload(self, folders, delete_type, delete_sub_folders):
        payload = create_element(
            f"m:{self.SERVICE_NAME}", attrs=dict(DeleteType=delete_type, DeleteSubFolders=delete_sub_folders)
        )
        payload.append(folder_ids_element(folders=folders, version=self.account.version))
        return payload
