from ..util import create_element, set_xml_value
from .common import EWSAccountService


class CreateUserConfiguration(EWSAccountService):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/createuserconfiguration-operation
    """

    SERVICE_NAME = "CreateUserConfiguration"
    returns_elements = False

    def call(self, user_configuration):
        return self._get_elements(payload=self.get_payload(user_configuration=user_configuration))

    def get_payload(self, user_configuration):
        return set_xml_value(
            create_element(f"m:{self.SERVICE_NAME}"), user_configuration, version=self.protocol.version
        )
