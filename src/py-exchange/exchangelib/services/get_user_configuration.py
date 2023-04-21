from ..errors import InvalidEnumValue
from ..properties import UserConfiguration
from ..util import create_element, set_xml_value
from .common import EWSAccountService

ID = "Id"
DICTIONARY = "Dictionary"
XML_DATA = "XmlData"
BINARY_DATA = "BinaryData"
ALL = "All"
PROPERTIES_CHOICES = (ID, DICTIONARY, XML_DATA, BINARY_DATA, ALL)


class GetUserConfiguration(EWSAccountService):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getuserconfiguration-operation
    """

    SERVICE_NAME = "GetUserConfiguration"

    def call(self, user_configuration_name, properties):
        if properties not in PROPERTIES_CHOICES:
            raise InvalidEnumValue("properties", properties, PROPERTIES_CHOICES)
        return self._elems_to_objs(
            self._get_elements(
                payload=self.get_payload(user_configuration_name=user_configuration_name, properties=properties)
            )
        )

    def _elem_to_obj(self, elem):
        return UserConfiguration.from_xml(elem=elem, account=self.account)

    @classmethod
    def _get_elements_in_container(cls, container):
        return container.findall(UserConfiguration.response_tag())

    def get_payload(self, user_configuration_name, properties):
        payload = create_element(f"m:{self.SERVICE_NAME}")
        set_xml_value(payload, user_configuration_name, version=self.account.version)
        payload.append(
            set_xml_value(create_element("m:UserConfigurationProperties"), properties, version=self.account.version)
        )
        return payload
