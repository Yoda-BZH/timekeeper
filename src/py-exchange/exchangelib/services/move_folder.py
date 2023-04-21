from ..errors import InvalidTypeError
from ..folders import BaseFolder
from ..properties import FolderId
from ..util import MNS, create_element
from .common import EWSAccountService, folder_ids_element


class MoveFolder(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/movefolder-operation"""

    SERVICE_NAME = "MoveFolder"
    element_container_name = f"{{{MNS}}}Folders"

    def call(self, folders, to_folder):
        if not isinstance(to_folder, (BaseFolder, FolderId)):
            raise InvalidTypeError("to_folder", to_folder, (BaseFolder, FolderId))
        return self._elems_to_objs(self._chunked_get_elements(self.get_payload, items=folders, to_folder=to_folder))

    def _elem_to_obj(self, elem):
        return FolderId.from_xml(elem=elem.find(FolderId.response_tag()), account=self.account)

    def get_payload(self, folders, to_folder):
        # Takes a list of folders and returns their new folder IDs
        payload = create_element(f"m:{self.SERVICE_NAME}")
        payload.append(folder_ids_element(folders=[to_folder], version=self.account.version, tag="m:ToFolderId"))
        payload.append(folder_ids_element(folders=folders, version=self.account.version))
        return payload
