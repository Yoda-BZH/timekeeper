from ..util import create_element, set_xml_value, MNS
from .common import EWSAccountService, to_item_id


class CreateAttachment(EWSAccountService):
    """
    MSDN: https://msdn.microsoft.com/en-us/library/office/aa565877(v=exchg.150).aspx
    """
    SERVICE_NAME = 'CreateAttachment'
    element_container_name = '{%s}Attachments' % MNS

    def call(self, parent_item, items):
        return self._get_elements(payload=self.get_payload(
            parent_item=parent_item,
            items=items,
        ))

    def get_payload(self, parent_item, items):
        from ..properties import ParentItemId
        payload = create_element('m:%s' % self.SERVICE_NAME)
        parent_id = to_item_id(parent_item, ParentItemId)
        payload.append(parent_id.to_xml(version=self.account.version))
        attachments = create_element('m:Attachments')
        for item in items:
            set_xml_value(attachments, item, version=self.account.version)
        if not len(attachments):
            raise ValueError('"items" must not be empty')
        payload.append(attachments)
        return payload
