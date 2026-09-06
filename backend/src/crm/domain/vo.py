from typing import ClassVar

import re
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from src.shared.domain.vo import ValueObject

_RU_FULL_LENGTH = 11
_RU_LOCAL_LENGTH = 10


def _normalize_ru_phone(raw: str) -> str:
    """Очищает строку и приводит российский номер к формату '7XXXXXXXXXX'."""

    digits = "".join(char for char in raw if char.isdigit())

    if not digits:
        raise ValueError("Phone number cannot be empty and must contain digits.")

    if digits.startswith("8") and len(digits) == _RU_FULL_LENGTH:
        digits = "7" + digits[1:]

    elif digits.startswith("9") and len(digits) == _RU_LOCAL_LENGTH:
        digits = "7" + digits

    return digits


class AddressType(StrEnum):
    LEGAL = "legal"
    ACTUAL = "actual"
    POSTAL = "postal"


@dataclass(frozen=True, slots=True)
class Address(ValueObject):
    """"""

    type: AddressType

    country: str
    postal_code: str | None = None
    region: str | None = None
    city: str | None = None
    street: str | None = None
    building: str | None = None
    apartment: str | None = None


@dataclass(frozen=True, slots=True)
class Inn(ValueObject):
    """ИНН - Идентификационный номер налогоплательщика (10 или 12 цифр)."""

    LEGAL_ENTITY_LEN: ClassVar[int] = 10
    INDIVIDUAL_LEN: ClassVar[int] = 12

    value: str = field(compare=True, hash=True)

    def __post_init__(self) -> None:
        cleaned = self.value.strip().replace(" ", "").replace("-", "")

        if not cleaned.isdigit():
            raise ValueError("INN can contains only digits")

        if len(cleaned) not in (self.LEGAL_ENTITY_LEN, self.INDIVIDUAL_LEN):
            raise ValueError(f"INN must contain 10 or 12 digits (received {len(cleaned)})")

        object.__setattr__(self, "value", cleaned)

    @property
    def is_legal_entity(self) -> bool:
        """Является ли юридическим лицом (10 цифр)."""

        return len(self.value) == self.LEGAL_ENTITY_LEN

    @property
    def is_individual(self) -> bool:
        """Является ли физическим лицом / ИП (12 цифр)."""

        return len(self.value) == self.INDIVIDUAL_LEN


@dataclass(frozen=True, slots=True)
class Kpp(ValueObject):
    """КПП - Код причины постановки на учёт (9 символов: цифры и заглавные буквы)."""

    LENGTH: ClassVar[int] = 9
    VALID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\d{4}[0-9A-ZА-Я]{2}\d{3}$")

    value: str = field(compare=True, hash=True)

    def __post_init__(self) -> None:
        cleaned = self.value.strip().replace(" ", "").replace("-", "").upper()

        if not self.VALID_PATTERN.match(cleaned):
            raise ValueError(
                "KPP must be 9 alphanumeric characters "
                f"matching FNS format (received: {self.value})",
            )

        object.__setattr__(self, "value", cleaned)


@dataclass(frozen=True, slots=True)
class Okpo(ValueObject):
    """ОКПО - Общероссийский классификатор предприятий и организаций
    (8 цифр - юридического лица, 10 цифр — ИП и обособленные подразделения).
    """

    LEGAL_ENTITY_LEN: ClassVar[int] = 8
    INDIVIDUAL_OR_BRANCH_LEN: ClassVar[int] = 10

    value: str = field(compare=True, hash=True, repr=False)

    def __post_init__(self) -> None:
        cleaned = self.value.strip().replace(" ", "").replace("-", "")

        if not cleaned.isdigit():
            raise ValueError("OKPO must contain only digits")

        if len(cleaned) not in (self.LEGAL_ENTITY_LEN, self.INDIVIDUAL_OR_BRANCH_LEN):
            raise ValueError(f"OKPO must contain 8 or 10 digits (received {len(cleaned)})")

        object.__setattr__(self, "value", cleaned)

    @property
    def is_legal_entity(self) -> bool:
        """Принадлежит ли юридическому лицу."""

        return len(self.value) == self.LEGAL_ENTITY_LEN

    @property
    def is_individual_or_branch(self) -> bool:
        """Является ИП или обособленным подразделением."""

        return len(self.value) == self.INDIVIDUAL_OR_BRANCH_LEN


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """Номер телефона (российский формат, хранится как 11 цифр начиная с 7)."""

    VALID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^7\d{10}$")

    value: str = field(compare=True, hash=True)

    def __post_init__(self) -> None:
        normalized = _normalize_ru_phone(self.value)

        if not self.VALID_PATTERN.match(normalized):
            raise ValueError(
                f"Invalid Russian phone number format (received: {self.value}). "
                "Expected formats: +7XXXXXXXXXX, 8XXXXXXXXXX or 9XXXXXXXXXX",
            )

        object.__setattr__(self, "value", normalized)


class BusinessSubjectType(StrEnum):
    INDIVIDUAL = "individual"
    INDIVIDUAL_ENTREPRENEUR = "individual_entrepreneur"
    LEGAL_ENTITY = "legal_entity"
    FOREIGN_LEGAL_ENTITY = "foreign_legal_entity"


@dataclass(frozen=True, slots=True)
class BusinessProfile(ValueObject):
    """"""

    subject_type: BusinessSubjectType

    legal_name: str
    short_name: str | None = None

    inn: Inn | None = None
    kpp: Kpp | None = None

    ogrn: str | None = None
    ogrnip: str | None = None

    okpo: Okpo | None = None

    registered_at: date | None = None

    def __post_init__(self) -> None:
        _validate_business_profile(self)


def _validate_business_profile(profile: BusinessProfile) -> None:
    """"""

    if not profile.legal_name.strip():
        raise ValueError("Legal name cannot be empty.")

    match profile.subject_type:
        case BusinessSubjectType.INDIVIDUAL:
            _validate_individual(profile)

        case BusinessSubjectType.INDIVIDUAL_ENTREPRENEUR:
            _validate_individual_entrepreneur(profile)

        case BusinessSubjectType.LEGAL_ENTITY:
            _validate_legal_entity(profile)

        case BusinessSubjectType.FOREIGN_LEGAL_ENTITY:
            _validate_foreign_legal_entity(profile)


def _validate_individual(profile: BusinessProfile) -> None:
    """"""

    if profile.inn is not None and not profile.inn.is_individual:
        raise ValueError("Individual must have a 12-digit INN.")

    if profile.kpp is not None:
        raise ValueError("Individual cannot have KPP.")

    if profile.ogrn is not None:
        raise ValueError("Individual cannot have OGRN.")

    if profile.ogrnip is not None:
        raise ValueError("Individual cannot have OGRNIP.")


def _validate_individual_entrepreneur(profile: BusinessProfile) -> None:
    if profile.inn is not None and not profile.inn.is_individual:
        raise ValueError("Individual entrepreneur must have a 12-digit INN.")

    if profile.kpp is not None:
        raise ValueError("Individual entrepreneur cannot have KPP.")

    if profile.ogrn is not None:
        raise ValueError("Individual entrepreneur cannot have OGRN.")

    if profile.ogrnip is None:
        raise ValueError("Individual entrepreneur must have OGRNIP.")


def _validate_legal_entity(profile: BusinessProfile) -> None:
    if profile.inn is not None and not profile.inn.is_legal_entity:
        raise ValueError("Legal entity must have a 10-digit INN.")

    if profile.ogrn is None:
        raise ValueError("Legal entity must have OGRN.")

    if profile.ogrnip is not None:
        raise ValueError("Legal entity cannot have OGRNIP.")


def _validate_foreign_legal_entity(profile: BusinessProfile) -> None:
    if profile.kpp is not None and profile.inn is None:
        raise ValueError("Foreign legal entity cannot have KPP without INN.")

    if profile.ogrnip is not None:
        raise ValueError("Foreign legal entity cannot have OGRNIP.")
