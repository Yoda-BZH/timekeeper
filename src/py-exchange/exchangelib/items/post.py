import logging

from ..fields import BodyField, DateTimeField, MailboxField, TextField
from .item import Item
from .message import Message

log = logging.getLogger(__name__)


class PostItem(Item):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/postitem"""

    ELEMENT_NAME = "PostItem"

    conversation_index = Message.FIELDS["conversation_index"]
    conversation_topic = Message.FIELDS["conversation_topic"]

    author = Message.FIELDS["author"]
    message_id = Message.FIELDS["message_id"]
    is_read = Message.FIELDS["is_read"]

    posted_time = DateTimeField(field_uri="postitem:PostedTime", is_read_only=True)
    references = TextField(field_uri="message:References")
    sender = MailboxField(field_uri="message:Sender", is_read_only=True, is_read_only_after_send=True)


class PostReplyItem(Item):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/postreplyitem"""

    ELEMENT_NAME = "PostReplyItem"

    # This element only has Item fields up to, and including, 'culture'
    # TDO: Plus all message fields
    new_body = BodyField(field_uri="NewBodyContent")  # Accepts and returns Body or HTMLBody instances

    culture_idx = Item.FIELDS.index_by_name("culture")
    sender_idx = Message.FIELDS.index_by_name("sender")
    FIELDS = Item.FIELDS[: culture_idx + 1] + Message.FIELDS[sender_idx:]
