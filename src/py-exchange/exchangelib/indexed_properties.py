import logging

from .fields import Choice, EmailSubField, LabelField, NamedSubField, SubField
from .properties import EWSElement, EWSMeta

log = logging.getLogger(__name__)


class IndexedElement(EWSElement, metaclass=EWSMeta):
    """Base class for all classes that implement an indexed element."""

    LABEL_CHOICES = ()


class SingleFieldIndexedElement(IndexedElement, metaclass=EWSMeta):
    """Base class for all classes that implement an indexed element with a single field."""

    @classmethod
    def value_field(cls, version):
        fields = cls.supported_fields(version=version)
        if len(fields) != 1:
            raise ValueError(f"Class {cls} must have only one value field (found {tuple(f.name for f in fields)})")
        return fields[0]


class EmailAddress(SingleFieldIndexedElement):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/entry-emailaddress"""

    ELEMENT_NAME = "Entry"
    LABEL_CHOICES = ("EmailAddress1", "EmailAddress2", "EmailAddress3")

    label = LabelField(field_uri="Key", choices={Choice(c) for c in LABEL_CHOICES}, default=LABEL_CHOICES[0])
    email = EmailSubField(is_required=True)


class PhoneNumber(SingleFieldIndexedElement):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/entry-phonenumber"""

    ELEMENT_NAME = "Entry"
    LABEL_CHOICES = (
        "AssistantPhone",
        "BusinessFax",
        "BusinessPhone",
        "BusinessPhone2",
        "Callback",
        "CarPhone",
        "CompanyMainPhone",
        "HomeFax",
        "HomePhone",
        "HomePhone2",
        "Isdn",
        "MobilePhone",
        "OtherFax",
        "OtherTelephone",
        "Pager",
        "PrimaryPhone",
        "RadioPhone",
        "Telex",
        "TtyTddPhone",
    )

    label = LabelField(field_uri="Key", choices={Choice(c) for c in LABEL_CHOICES}, default="PrimaryPhone")
    phone_number = SubField(is_required=True)


class MultiFieldIndexedElement(IndexedElement, metaclass=EWSMeta):
    """Base class for all classes that implement an indexed element with multiple fields."""


class PhysicalAddress(MultiFieldIndexedElement):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/entry-physicaladdress"""

    ELEMENT_NAME = "Entry"
    LABEL_CHOICES = ("Business", "Home", "Other")

    label = LabelField(field_uri="Key", choices={Choice(c) for c in LABEL_CHOICES}, default=LABEL_CHOICES[0])
    street = NamedSubField(field_uri="Street")  # Street, house number, etc.
    city = NamedSubField(field_uri="City")
    state = NamedSubField(field_uri="State")
    country = NamedSubField(field_uri="CountryOrRegion")
    zipcode = NamedSubField(field_uri="PostalCode")

    def clean(self, version=None):
        if isinstance(self.zipcode, int):
            self.zipcode = str(self.zipcode)
        super().clean(version=version)
