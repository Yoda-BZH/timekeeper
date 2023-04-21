from ..errors import InvalidEnumValue
from ..items import AFFECTED_TASK_OCCURRENCES_CHOICES, DELETE_TYPE_CHOICES, SEND_MEETING_CANCELLATIONS_CHOICES
from ..util import create_element
from ..version import EXCHANGE_2013_SP1
from .common import EWSAccountService, item_ids_element


class DeleteItem(EWSAccountService):
    """Take a folder and a list of (id, changekey) tuples. Return result of deletion as a list of tuples
    (success[True|False], errormessage), in the same order as the input list.

    MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/deleteitem-operation
    """

    SERVICE_NAME = "DeleteItem"
    returns_elements = False

    def call(self, items, delete_type, send_meeting_cancellations, affected_task_occurrences, suppress_read_receipts):
        if delete_type not in DELETE_TYPE_CHOICES:
            raise InvalidEnumValue("delete_type", delete_type, DELETE_TYPE_CHOICES)
        if send_meeting_cancellations not in SEND_MEETING_CANCELLATIONS_CHOICES:
            raise InvalidEnumValue(
                "send_meeting_cancellations", send_meeting_cancellations, SEND_MEETING_CANCELLATIONS_CHOICES
            )
        if affected_task_occurrences not in AFFECTED_TASK_OCCURRENCES_CHOICES:
            raise InvalidEnumValue(
                "affected_task_occurrences", affected_task_occurrences, AFFECTED_TASK_OCCURRENCES_CHOICES
            )
        return self._chunked_get_elements(
            self.get_payload,
            items=items,
            delete_type=delete_type,
            send_meeting_cancellations=send_meeting_cancellations,
            affected_task_occurrences=affected_task_occurrences,
            suppress_read_receipts=suppress_read_receipts,
        )

    def get_payload(
        self, items, delete_type, send_meeting_cancellations, affected_task_occurrences, suppress_read_receipts
    ):
        # Takes a list of (id, changekey) tuples or Item objects and returns the XML for a DeleteItem request.
        attrs = dict(
            DeleteType=delete_type,
            SendMeetingCancellations=send_meeting_cancellations,
            AffectedTaskOccurrences=affected_task_occurrences,
        )
        if self.account.version.build >= EXCHANGE_2013_SP1:
            attrs["SuppressReadReceipts"] = suppress_read_receipts
        payload = create_element(f"m:{self.SERVICE_NAME}", attrs=attrs)
        payload.append(item_ids_element(items=items, version=self.account.version))
        return payload
