import datetime

from .ewsdatetime import UTC
from .fields import Choice, ChoiceField, DateTimeField, MessageField
from .properties import EWSElement, OutOfOffice
from .util import create_element, set_xml_value


class OofSettings(EWSElement):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/oofsettings"""

    ELEMENT_NAME = "OofSettings"
    REQUEST_ELEMENT_NAME = "UserOofSettings"

    ENABLED = "Enabled"
    SCHEDULED = "Scheduled"
    DISABLED = "Disabled"
    STATE_CHOICES = (ENABLED, SCHEDULED, DISABLED)

    state = ChoiceField(field_uri="OofState", is_required=True, choices={Choice(c) for c in STATE_CHOICES})
    external_audience = ChoiceField(
        field_uri="ExternalAudience", choices={Choice("None"), Choice("Known"), Choice("All")}, default="All"
    )
    start = DateTimeField(field_uri="StartTime")
    end = DateTimeField(field_uri="EndTime")
    internal_reply = MessageField(field_uri="InternalReply")
    external_reply = MessageField(field_uri="ExternalReply")

    def clean(self, version=None):
        super().clean(version=version)
        if self.state == self.SCHEDULED:
            if not self.start or not self.end:
                raise ValueError(f"'start' and 'end' must be set when state is {self.SCHEDULED!r}")
            if self.start >= self.end:
                raise ValueError("'start' must be before 'end'")
            if self.end < datetime.datetime.now(tz=UTC):
                raise ValueError("'end' must be in the future")
        if self.state != self.DISABLED and (not self.internal_reply or not self.external_reply):
            raise ValueError(f"'internal_reply' and 'external_reply' must be set when state is not {self.DISABLED!r}")

    @classmethod
    def from_xml(cls, elem, account):
        kwargs = {}
        for attr in ("state", "external_audience", "internal_reply", "external_reply"):
            f = cls.get_field_by_fieldname(attr)
            kwargs[attr] = f.from_xml(elem=elem, account=account)
        kwargs.update(OutOfOffice.duration_to_start_end(elem=elem, account=account))
        cls._clear(elem)
        return cls(**kwargs)

    def to_xml(self, version):
        self.clean(version=version)
        elem = create_element(f"t:{self.REQUEST_ELEMENT_NAME}")
        for attr in ("state", "external_audience"):
            value = getattr(self, attr)
            f = self.get_field_by_fieldname(attr)
            set_xml_value(elem, f.to_xml(value, version=version))
        if self.start or self.end:
            duration = create_element("t:Duration")
            if self.start:
                f = self.get_field_by_fieldname("start")
                set_xml_value(duration, f.to_xml(self.start, version=version))
            if self.end:
                f = self.get_field_by_fieldname("end")
                set_xml_value(duration, f.to_xml(self.end, version=version))
            elem.append(duration)
        for attr in ("internal_reply", "external_reply"):
            value = getattr(self, attr)
            if value is None:
                value = ""  # The value can be empty, but the XML element must always be present
            f = self.get_field_by_fieldname(attr)
            set_xml_value(elem, f.to_xml(value, version=version))
        return elem

    def __hash__(self):
        # Customize comparison
        if self.state == self.DISABLED:
            # All values except state are ignored by the server
            relevant_attrs = ("state",)
        elif self.state != self.SCHEDULED:
            # 'start' and 'end' values are ignored by the server, and the server always returns today's date
            relevant_attrs = tuple(f.name for f in self.FIELDS if f.name not in ("start", "end"))
        else:
            relevant_attrs = tuple(f.name for f in self.FIELDS)
        return hash(tuple(getattr(self, attr) for attr in relevant_attrs))
