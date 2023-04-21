from ..errors import MalformedResponseError
from ..properties import FailedMailbox, SearchableMailbox
from ..util import MNS, add_xml_child, create_element
from ..version import EXCHANGE_2013
from .common import EWSService


class GetSearchableMailboxes(EWSService):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getsearchablemailboxes-operation
    """

    SERVICE_NAME = "GetSearchableMailboxes"
    element_container_name = f"{{{MNS}}}SearchableMailboxes"
    failed_mailboxes_container_name = f"{{{MNS}}}FailedMailboxes"
    supported_from = EXCHANGE_2013
    cls_map = {cls.response_tag(): cls for cls in (SearchableMailbox, FailedMailbox)}

    def call(self, search_filter, expand_group_membership):
        return self._elems_to_objs(
            self._get_elements(
                payload=self.get_payload(
                    search_filter=search_filter,
                    expand_group_membership=expand_group_membership,
                )
            )
        )

    def _elem_to_obj(self, elem):
        return self.cls_map[elem.tag].from_xml(elem=elem, account=None)

    def get_payload(self, search_filter, expand_group_membership):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        if search_filter:
            add_xml_child(payload, "m:SearchFilter", search_filter)
        if expand_group_membership is not None:
            add_xml_child(payload, "m:ExpandGroupMembership", "true" if expand_group_membership else "false")
        return payload

    def _get_elements_in_response(self, response):
        for msg in response:
            for container_name in (self.element_container_name, self.failed_mailboxes_container_name):
                try:
                    container = self._get_element_container(message=msg, name=container_name)
                except MalformedResponseError:
                    # Responses may contain no mailboxes of either kind. _get_element_container() does not accept this.
                    continue
                yield from self._get_elements_in_container(container=container)
