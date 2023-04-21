from ..items import Persona
from ..properties import PersonaId
from ..util import MNS, create_element, set_xml_value
from .common import EWSAccountService, to_item_id


class GetPersona(EWSAccountService):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getpersona-operation"""

    SERVICE_NAME = "GetPersona"

    def call(self, personas):
        # GetPersona only accepts one persona ID per request. Crazy.
        for persona in personas:
            yield from self._elems_to_objs(self._get_elements(payload=self.get_payload(persona=persona)))

    def _elem_to_obj(self, elem):
        return Persona.from_xml(elem=elem, account=None)

    def get_payload(self, persona):
        return set_xml_value(
            create_element(f"m:{self.SERVICE_NAME}"), to_item_id(persona, PersonaId), version=self.protocol.version
        )

    @classmethod
    def _get_elements_in_container(cls, container):
        return container.findall(f"{{{MNS}}}{Persona.ELEMENT_NAME}")

    @classmethod
    def _response_tag(cls):
        return f"{{{MNS}}}{cls.SERVICE_NAME}ResponseMessage"
