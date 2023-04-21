from ..errors import ErrorNameResolutionMultipleResults
from ..properties import Mailbox
from ..util import MNS, create_element, set_xml_value
from .common import EWSService


class ExpandDL(EWSService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/expanddl-operation"""

    SERVICE_NAME = "ExpandDL"
    element_container_name = f"{{{MNS}}}DLExpansion"
    WARNINGS_TO_IGNORE_IN_RESPONSE = ErrorNameResolutionMultipleResults

    def call(self, distribution_list):
        return self._elems_to_objs(self._get_elements(payload=self.get_payload(distribution_list=distribution_list)))

    def _elem_to_obj(self, elem):
        return Mailbox.from_xml(elem, account=None)

    def get_payload(self, distribution_list):
        return set_xml_value(create_element(f"m:{self.SERVICE_NAME}"), distribution_list, version=self.protocol.version)
