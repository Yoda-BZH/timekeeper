from ..properties import TimeZoneDefinition
from ..util import MNS, create_element, peek, set_xml_value
from ..version import EXCHANGE_2010
from .common import EWSService


class GetServerTimeZones(EWSService):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getservertimezones-operation
    """

    SERVICE_NAME = "GetServerTimeZones"
    element_container_name = f"{{{MNS}}}TimeZoneDefinitions"
    supported_from = EXCHANGE_2010

    def call(self, timezones=None, return_full_timezone_data=False):
        return self._elems_to_objs(
            self._get_elements(
                payload=self.get_payload(timezones=timezones, return_full_timezone_data=return_full_timezone_data)
            )
        )

    def get_payload(self, timezones, return_full_timezone_data):
        payload = create_element(
            f"m:{self.SERVICE_NAME}",
            attrs=dict(ReturnFullTimeZoneData=return_full_timezone_data),
        )
        if timezones is not None:
            is_empty, timezones = peek(timezones)
            if not is_empty:
                tz_ids = create_element("m:Ids")
                for timezone in timezones:
                    tz_id = set_xml_value(create_element("t:Id"), timezone.ms_id)
                    tz_ids.append(tz_id)
                payload.append(tz_ids)
        return payload

    def _elem_to_obj(self, elem):
        return TimeZoneDefinition.from_xml(elem=elem, account=None)
