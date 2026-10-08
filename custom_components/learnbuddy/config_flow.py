"""Config flow of the LearnBuddy integration."""

from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import (
    SOURCE_RECONFIGURE,
    ConfigEntry,
    ConfigEntryState,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    ActionSelector,
    BooleanSelector,
    DateSelector,
    DateTimeSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    ObjectSelector,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TimeSelector,
)
from homeassistant.util import dt as dt_util
import voluptuous as vol

from .const import (
    BUNDESLAENDER,
    CONF_ABFRAGEN_PRO_TAG,
    CONF_ABSENDER_KENNUNG,
    CONF_ANTWORTFRIST,
    CONF_ART,
    CONF_AUTO_FREIGABE,
    CONF_BILD_AKTION,
    CONF_BUNDESLAND,
    CONF_DATUM,
    CONF_EINGANG_ABSENDER_FELD,
    CONF_EINGANG_EVENT,
    CONF_EINGANG_TELEGRAM,
    CONF_EINGANG_TEXT_FELD,
    CONF_EINGANG_WHATSAPP,
    CONF_ERSTELLT,
    CONF_FACH_ID,
    CONF_GEAENDERT,
    CONF_INTENSIVIERUNG,
    CONF_KALENDER_AKTIV,
    CONF_KALENDER_ENTITY,
    CONF_KALENDER_UID,
    CONF_KALENDER_UM,
    CONF_KI_ENTITY,
    CONF_KIND_ID,
    CONF_KLASSENSTUFE,
    CONF_LEKTIONEN,
    CONF_MUTTERSPRACHE,
    CONF_NAME,
    CONF_NOTIFY_DATA,
    CONF_NOTIFY_ENTITY,
    CONF_NOTIFY_SERVICE,
    CONF_NOTIFY_TARGET,
    CONF_SCHULART,
    CONF_SIMULATION_ANZAHL,
    CONF_SIMULATION_UM,
    CONF_SPRACHE,
    CONF_SPRACHEN,
    CONF_START_TAGE_VORHER,
    CONF_THEMA,
    CONF_TIMEOUT_MINUTEN,
    CONF_TYP,
    CONF_VERLAUF,
    CONF_WERKTAG_BIS,
    CONF_WERKTAG_VON,
    CONF_WOCHENENDE_AKTIV,
    CONF_WOCHENENDE_BIS,
    CONF_WOCHENENDE_VON,
    CONF_WOCHENREPORT,
    CONF_ZIELSPRACHE,
    DEFAULT_ABFRAGEN_PRO_TAG,
    DEFAULT_KALENDER_UM,
    DEFAULT_SIMULATION_ANZAHL,
    DEFAULT_START_TAGE_VORHER,
    DEFAULT_TIMEOUT_MINUTEN,
    DEFAULT_WERKTAG_BIS,
    DEFAULT_WERKTAG_VON,
    DEFAULT_WOCHENENDE_BIS,
    DEFAULT_WOCHENENDE_VON,
    DOMAIN,
    MAX_TIMEOUT_MINUTEN,
    SCHULARTEN,
    SPRACH_CODES,
    SPRACHE_AUTO,
    SUBENTRY_ARBEIT,
    SUBENTRY_FACH,
    SUBENTRY_KIND,
)
from .models import ArbeitArt, AufgabenTyp, arbeit_titel
from .texte import sprachname

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.config_entries import ConfigSubentry

NOTIFY_DOMAIN = "notify"
CALENDAR_DOMAIN = "calendar"
# Kinds of subjects offered in the UI; each maps to a task type
FACHART_FREMDSPRACHE = "fremdsprache"
FACHART_MATHE = "mathe"
FACHART_SACH = "sach"
AI_TASK_DOMAIN = "ai_task"

_KI_SELECTOR = EntitySelector(EntitySelectorConfig(domain=AI_TASK_DOMAIN))

_SPRACH_SELECTOR = SelectSelector(
    SelectSelectorConfig(
        options=SPRACH_CODES,
        translation_key="sprache",
        mode=SelectSelectorMode.DROPDOWN,
    )
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_TIMEOUT_MINUTEN, default=DEFAULT_TIMEOUT_MINUTEN
        ): NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=1440,
                step=1,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="min",
            )
        ),
        vol.Required(CONF_SPRACHE, default=SPRACHE_AUTO): SelectSelector(
            SelectSelectorConfig(
                options=[SPRACHE_AUTO, "de", "en"],
                translation_key="nachrichten_sprache",
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_KI_ENTITY): _KI_SELECTOR,
        vol.Required(CONF_AUTO_FREIGABE, default=False): BooleanSelector(),
        vol.Required(CONF_VERLAUF, default=True): BooleanSelector(),
        vol.Required(CONF_WOCHENREPORT, default=True): BooleanSelector(),
        vol.Required(CONF_EINGANG_TELEGRAM, default=True): BooleanSelector(),
        vol.Required(CONF_EINGANG_WHATSAPP, default=True): BooleanSelector(),
        vol.Optional(CONF_EINGANG_EVENT): TextSelector(),
        vol.Optional(CONF_EINGANG_ABSENDER_FELD): TextSelector(),
        vol.Optional(CONF_EINGANG_TEXT_FELD): TextSelector(),
    }
)

KIND_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): TextSelector(),
        vol.Required(CONF_MUTTERSPRACHE): _SPRACH_SELECTOR,
        vol.Optional(CONF_KLASSENSTUFE): NumberSelector(
            NumberSelectorConfig(min=1, max=13, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Optional(CONF_SCHULART): SelectSelector(
            SelectSelectorConfig(
                options=SCHULARTEN,
                translation_key="schulart",
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_BUNDESLAND): SelectSelector(
            SelectSelectorConfig(
                options=BUNDESLAENDER,
                translation_key="bundesland",
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_NOTIFY_ENTITY): EntitySelector(
            EntitySelectorConfig(domain=NOTIFY_DOMAIN)
        ),
        vol.Optional(CONF_ABSENDER_KENNUNG): TextSelector(),
        vol.Optional(CONF_BILD_AKTION): ActionSelector(),
        vol.Required(CONF_WERKTAG_VON, default=DEFAULT_WERKTAG_VON): TimeSelector(),
        vol.Required(CONF_WERKTAG_BIS, default=DEFAULT_WERKTAG_BIS): TimeSelector(),
        vol.Required(CONF_WOCHENENDE_AKTIV, default=True): BooleanSelector(),
        vol.Required(
            CONF_WOCHENENDE_VON, default=DEFAULT_WOCHENENDE_VON
        ): TimeSelector(),
        vol.Required(
            CONF_WOCHENENDE_BIS, default=DEFAULT_WOCHENENDE_BIS
        ): TimeSelector(),
    }
)


# Form-only switch of the exam form, not stored
SIMULATION_AKTIV = "simulation_aktiv"

# Only needed without a notify entity, so it is folded away by default
ABSCHNITT_KLASSISCH = "klassisch"
_KLASSISCH_FELDER = (CONF_NOTIFY_SERVICE, CONF_NOTIFY_TARGET, CONF_NOTIFY_DATA)
_KLASSISCH_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NOTIFY_SERVICE): TextSelector(),
        vol.Optional(CONF_NOTIFY_TARGET): TextSelector(
            TextSelectorConfig(multiple=True)
        ),
        vol.Optional(CONF_NOTIFY_DATA): ObjectSelector(),
    }
)

# Optional: a calendar with the exam dates of the child
ABSCHNITT_KALENDER = "kalender"
_KALENDER_FELDER = (CONF_KALENDER_AKTIV, CONF_KALENDER_ENTITY, CONF_KALENDER_UM)
_KALENDER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_KALENDER_AKTIV, default=False): BooleanSelector(),
        vol.Optional(CONF_KALENDER_ENTITY): EntitySelector(
            EntitySelectorConfig(domain=CALENDAR_DOMAIN)
        ),
        vol.Required(CONF_KALENDER_UM, default=DEFAULT_KALENDER_UM): TimeSelector(),
    }
)
_ABSCHNITTE: dict[str, tuple[str, ...]] = {
    ABSCHNITT_KLASSISCH: _KLASSISCH_FELDER,
    ABSCHNITT_KALENDER: _KALENDER_FELDER,
}


def _kind_schema(werte: Mapping[str, Any]) -> vol.Schema:
    """Return the child form; optional parts are open only when they are used."""
    felder: dict[Any, Any] = {}
    for feld, selector in KIND_SCHEMA.schema.items():
        felder[feld] = selector
        if feld == CONF_NOTIFY_ENTITY:
            # Right below the notify entity it replaces
            felder[vol.Required(ABSCHNITT_KLASSISCH)] = section(
                _KLASSISCH_SCHEMA,
                {"collapsed": not werte.get(CONF_NOTIFY_SERVICE)},
            )
    felder[vol.Required(ABSCHNITT_KALENDER)] = section(
        _KALENDER_SCHEMA, {"collapsed": not werte.get(CONF_KALENDER_AKTIV)}
    )
    return vol.Schema(felder)


def _kind_vorgaben(werte: Mapping[str, Any]) -> dict[str, Any]:
    """Move the stored flat values of the sections into them."""
    in_abschnitten = {feld for felder in _ABSCHNITTE.values() for feld in felder}
    vorgaben = {k: v for k, v in werte.items() if k not in in_abschnitten}
    for abschnitt, felder in _ABSCHNITTE.items():
        vorgaben[abschnitt] = {k: werte[k] for k in felder if werte.get(k) is not None}
    return vorgaben


def _kind_eingabe(eingabe: Mapping[str, Any]) -> dict[str, Any]:
    """Flatten the form input; subentries store the values of sections flat."""
    daten = {k: v for k, v in eingabe.items() if k not in _ABSCHNITTE}
    for abschnitt in _ABSCHNITTE:
        daten.update(eingabe.get(abschnitt) or {})
    return daten


def standard_muttersprache(hass: HomeAssistant) -> str:
    """Return the language of Home Assistant if it can be a native language."""
    kurz = hass.config.language.split("-", maxsplit=1)[0].lower()
    return kurz if kurz in SPRACH_CODES else "de"


def muttersprache(hass: HomeAssistant, kind: ConfigSubentry) -> str:
    """Return the native language of a child, the source of its vocabulary."""
    sprache: str = kind.data.get(CONF_MUTTERSPRACHE) or standard_muttersprache(hass)
    return sprache


def _jetzt_iso() -> str:
    return dt_util.utcnow().isoformat()


def _subentries(entry: ConfigEntry, typ: str) -> list[ConfigSubentry]:
    """Return all subentries of a type."""
    return [s for s in entry.subentries.values() if s.subentry_type == typ]


def _normalisiere_notify_service(wert: str) -> str | None:
    """Return the bare service name of a notify service or None if invalid."""
    name = wert.strip().lower()
    name = name.removeprefix(f"{NOTIFY_DOMAIN}.")
    if not name or not name.replace("_", "").isalnum():
        return None
    return name


def _pruefe_kind(
    eingabe: dict[str, Any], vorhandene_namen: set[str]
) -> tuple[dict[str, Any], dict[str, str]]:
    """Validate and clean the input of the child form."""
    fehler: dict[str, str] = {}
    daten = dict(eingabe)
    daten[CONF_NAME] = daten[CONF_NAME].strip()
    if not daten[CONF_NAME]:
        fehler[CONF_NAME] = "name_leer"
    elif daten[CONF_NAME].casefold() in vorhandene_namen:
        fehler[CONF_NAME] = "name_vorhanden"

    hat_entity = bool(daten.get(CONF_NOTIFY_ENTITY))
    hat_service = bool((daten.get(CONF_NOTIFY_SERVICE) or "").strip())
    if hat_entity == hat_service:
        fehler["base"] = "notify_genau_eins"
    elif hat_service:
        service = _normalisiere_notify_service(daten[CONF_NOTIFY_SERVICE])
        if service is None:
            # Shown at the top: the field may sit in the folded section
            fehler["base"] = "notify_service_ungueltig"
        else:
            daten[CONF_NOTIFY_SERVICE] = service
    if not hat_service:
        # Target and extra data belong to the classic action only
        for feld in _KLASSISCH_FELDER:
            daten.pop(feld, None)

    if CONF_ABSENDER_KENNUNG in daten:
        daten[CONF_ABSENDER_KENNUNG] = daten[CONF_ABSENDER_KENNUNG].strip()

    daten[CONF_KALENDER_AKTIV] = bool(daten.get(CONF_KALENDER_AKTIV))
    daten.setdefault(CONF_KALENDER_UM, DEFAULT_KALENDER_UM)
    if not daten.get(CONF_KALENDER_ENTITY):
        daten.pop(CONF_KALENDER_ENTITY, None)
        if daten[CONF_KALENDER_AKTIV]:
            # Shown at the top: the field may sit in the folded section
            fehler["base"] = "kalender_fehlt"

    if not daten.get(CONF_BILD_AKTION):
        daten.pop(CONF_BILD_AKTION, None)
    else:
        try:
            cv.SCRIPT_SCHEMA(daten[CONF_BILD_AKTION])
        except vol.Invalid:
            fehler[CONF_BILD_AKTION] = "bild_aktion_ungueltig"

    for von, bis in (
        (CONF_WERKTAG_VON, CONF_WERKTAG_BIS),
        (CONF_WOCHENENDE_VON, CONF_WOCHENENDE_BIS),
    ):
        if time.fromisoformat(daten[bis]) <= time.fromisoformat(daten[von]):
            fehler[bis] = "fenster_ungueltig"
    return daten, fehler


class LearnBuddyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow of the integration."""

    VERSION = 1
    MINOR_VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> LearnBuddyOptionsFlow:
        """Return the options flow."""
        return LearnBuddyOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return the supported subentry types."""
        return {
            SUBENTRY_KIND: KindSubentryFlow,
            SUBENTRY_FACH: FachSubentryFlow,
            SUBENTRY_ARBEIT: ArbeitSubentryFlow,
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up the integration."""
        if user_input is not None:
            return self.async_create_entry(
                title="LearnBuddy", data={}, options=user_input
            )
        return self.async_show_form(step_id="user", data_schema=OPTIONS_SCHEMA)


class LearnBuddyOptionsFlow(OptionsFlow):
    """Handle the global options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the global options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )


class KindSubentryFlow(ConfigSubentryFlow):
    """Add or change a child."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a child."""
        fehler: dict[str, str] = {}
        if user_input is not None:
            namen = {
                s.data[CONF_NAME].casefold()
                for s in _subentries(self._get_entry(), SUBENTRY_KIND)
            }
            user_input = _kind_eingabe(user_input)
            daten, fehler = _pruefe_kind(user_input, namen)
            if not fehler:
                jetzt = _jetzt_iso()
                daten[CONF_ERSTELLT] = jetzt
                daten[CONF_GEAENDERT] = jetzt
                return self.async_create_entry(title=daten[CONF_NAME], data=daten)
        werte = user_input or {CONF_MUTTERSPRACHE: standard_muttersprache(self.hass)}
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                _kind_schema(werte), _kind_vorgaben(werte)
            ),
            errors=fehler,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Change a child."""
        subentry = self._get_reconfigure_subentry()
        fehler: dict[str, str] = {}
        if user_input is not None:
            namen = {
                s.data[CONF_NAME].casefold()
                for s in _subentries(self._get_entry(), SUBENTRY_KIND)
                if s.subentry_id != subentry.subentry_id
            }
            user_input = _kind_eingabe(user_input)
            daten, fehler = _pruefe_kind(user_input, namen)
            if not fehler:
                daten[CONF_ERSTELLT] = subentry.data.get(CONF_ERSTELLT, _jetzt_iso())
                daten[CONF_GEAENDERT] = _jetzt_iso()
                return self.async_update_and_abort(
                    self._get_entry(),
                    subentry,
                    title=daten[CONF_NAME],
                    data=daten,
                )
        werte = user_input or {
            CONF_MUTTERSPRACHE: muttersprache(self.hass, subentry),
            **subentry.data,
        }
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                _kind_schema(werte), _kind_vorgaben(werte)
            ),
            errors=fehler,
        )


def _ki_daten(eingabe: dict[str, Any]) -> dict[str, Any]:
    """Return the optional AI entity override of a subject."""
    if entity := eingabe.get(CONF_KI_ENTITY):
        return {CONF_KI_ENTITY: entity}
    return {}


def _fach_titel(name: str, kind_name: str) -> str:
    return f"{name} ({kind_name})"


class FachSubentryFlow(ConfigSubentryFlow):
    """Add or change a subject.

    The first step selects the child and the kind of subject, the second step
    asks for the details of that kind.
    """

    _kind_id: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Select the child and the kind of subject."""
        kinder = _subentries(self._get_entry(), SUBENTRY_KIND)
        if not kinder:
            return self.async_abort(reason="keine_kinder")
        if user_input is not None:
            self._kind_id = user_input[CONF_KIND_ID]
            # Every kind of subject has its own step
            if user_input[CONF_TYP] == FACHART_MATHE:
                return await self.async_step_mathe()
            if user_input[CONF_TYP] == FACHART_SACH:
                return await self.async_step_sach()
            return await self.async_step_fremdsprache()
        schema = vol.Schema(
            {
                vol.Required(CONF_KIND_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=k.subentry_id, label=k.title)
                            for k in kinder
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_TYP, default=FACHART_FREMDSPRACHE): SelectSelector(
                    SelectSelectorConfig(
                        options=[FACHART_FREMDSPRACHE, FACHART_MATHE, FACHART_SACH],
                        translation_key="fachart",
                        mode=SelectSelectorMode.LIST,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_fremdsprache(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Select the foreign language; the source is the native language of the child."""
        entry = self._get_entry()
        ausgang = muttersprache(self.hass, entry.subentries[self._kind_id])
        sprachen = [code for code in SPRACH_CODES if code != ausgang]
        fehler: dict[str, str] = {}
        if user_input is not None:
            ziel = user_input[CONF_ZIELSPRACHE]
            name = (user_input.get(CONF_NAME) or "").strip() or sprachname(
                self.hass.config.language, ziel
            )
            if self._name_vorhanden(name, self._kind_id, None):
                fehler[CONF_ZIELSPRACHE] = "name_vorhanden"
            if not fehler:
                jetzt = _jetzt_iso()
                return self.async_create_entry(
                    title=_fach_titel(name, entry.subentries[self._kind_id].title),
                    data={
                        CONF_KIND_ID: self._kind_id,
                        CONF_NAME: name,
                        CONF_TYP: AufgabenTyp.VOKABEL.value,
                        CONF_SPRACHEN: [ausgang, ziel],
                        CONF_ERSTELLT: jetzt,
                        CONF_GEAENDERT: jetzt,
                    }
                    | _ki_daten(user_input),
                )
        schema = vol.Schema(
            {
                vol.Required(CONF_ZIELSPRACHE): SelectSelector(
                    SelectSelectorConfig(
                        options=sprachen,
                        translation_key="sprache",
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_NAME): TextSelector(),
                vol.Optional(CONF_KI_ENTITY): _KI_SELECTOR,
            }
        )
        return self.async_show_form(
            step_id="fremdsprache",
            data_schema=self.add_suggested_values_to_schema(schema, user_input),
            errors=fehler,
            description_placeholders={
                "ausgangssprache": sprachname(self.hass.config.language, ausgang)
            },
        )

    async def async_step_mathe(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Name a math subject."""
        entry = self._get_entry()
        deutsch = self.hass.config.language.startswith("de")
        fehler: dict[str, str] = {}
        if user_input is not None:
            name = (user_input.get(CONF_NAME) or "").strip() or (
                "Mathe" if deutsch else "Math"
            )
            if self._name_vorhanden(name, self._kind_id, None):
                fehler[CONF_NAME] = "name_vorhanden"
            if not fehler:
                jetzt = _jetzt_iso()
                return self.async_create_entry(
                    title=_fach_titel(name, entry.subentries[self._kind_id].title),
                    data={
                        CONF_KIND_ID: self._kind_id,
                        CONF_NAME: name,
                        CONF_TYP: AufgabenTyp.MATHE.value,
                        CONF_ERSTELLT: jetzt,
                        CONF_GEAENDERT: jetzt,
                    }
                    | _ki_daten(user_input),
                )
        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME): TextSelector(),
                vol.Optional(CONF_KI_ENTITY): _KI_SELECTOR,
            }
        )
        return self.async_show_form(
            step_id="mathe",
            data_schema=self.add_suggested_values_to_schema(schema, user_input),
            errors=fehler,
        )

    async def async_step_sach(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Name a knowledge subject like biology."""
        entry = self._get_entry()
        fehler: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            if not name:
                fehler[CONF_NAME] = "name_leer"
            elif self._name_vorhanden(name, self._kind_id, None):
                fehler[CONF_NAME] = "name_vorhanden"
            if not fehler:
                jetzt = _jetzt_iso()
                return self.async_create_entry(
                    title=_fach_titel(name, entry.subentries[self._kind_id].title),
                    data={
                        CONF_KIND_ID: self._kind_id,
                        CONF_NAME: name,
                        CONF_TYP: AufgabenTyp.SACH.value,
                        CONF_ERSTELLT: jetzt,
                        CONF_GEAENDERT: jetzt,
                    }
                    | _ki_daten(user_input),
                )
        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): TextSelector(),
                vol.Optional(CONF_KI_ENTITY): _KI_SELECTOR,
            }
        )
        return self.async_show_form(
            step_id="sach",
            data_schema=self.add_suggested_values_to_schema(schema, user_input),
            errors=fehler,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Rename a subject."""
        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()
        kind_id = subentry.data[CONF_KIND_ID]
        fehler: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            if not name:
                fehler[CONF_NAME] = "name_leer"
            elif self._name_vorhanden(name, kind_id, subentry.subentry_id):
                fehler[CONF_NAME] = "name_vorhanden"
            if not fehler:
                kind = entry.subentries.get(kind_id)
                return self.async_update_and_abort(
                    entry,
                    subentry,
                    title=_fach_titel(name, kind.title if kind else "?"),
                    data={
                        **{
                            k: v
                            for k, v in subentry.data.items()
                            if k != CONF_KI_ENTITY
                        },
                        CONF_NAME: name,
                        CONF_GEAENDERT: _jetzt_iso(),
                    }
                    | _ki_daten(user_input),
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_NAME): TextSelector(),
                        vol.Optional(CONF_KI_ENTITY): _KI_SELECTOR,
                    }
                ),
                user_input or subentry.data,
            ),
            errors=fehler,
        )

    def _name_vorhanden(self, name: str, kind_id: str, eigene_id: str | None) -> bool:
        return any(
            s.data[CONF_KIND_ID] == kind_id
            and s.data[CONF_NAME].casefold() == name.casefold()
            and s.subentry_id != eigene_id
            for s in _subentries(self._get_entry(), SUBENTRY_FACH)
        )


class ArbeitSubentryFlow(ConfigSubentryFlow):
    """Add or change an exam."""

    _fach_id: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Select the subject of the new exam."""
        faecher = _subentries(self._get_entry(), SUBENTRY_FACH)
        if not faecher:
            return self.async_abort(reason="keine_faecher")
        if user_input is not None:
            self._fach_id = user_input[CONF_FACH_ID]
            return await self.async_step_details()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_FACH_ID): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=f.subentry_id, label=f.title)
                                for f in faecher
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_details(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Enter the details of the new exam."""
        fehler: dict[str, str] = {}
        if user_input is not None:
            daten, fehler = self._pruefe(user_input)
            if not fehler:
                jetzt = _jetzt_iso()
                daten[CONF_ERSTELLT] = jetzt
                daten[CONF_GEAENDERT] = jetzt
                return self.async_create_entry(title=self._titel(daten), data=daten)
        return self.async_show_form(
            step_id="details",
            data_schema=self.add_suggested_values_to_schema(self._schema(), user_input),
            errors=fehler,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Change an exam."""
        subentry = self._get_reconfigure_subentry()
        self._fach_id = subentry.data[CONF_FACH_ID]
        fehler: dict[str, str] = {}
        if user_input is not None:
            daten, fehler = self._pruefe(
                user_input, subentry.data.get(CONF_SIMULATION_UM)
            )
            if not fehler:
                daten[CONF_ERSTELLT] = subentry.data.get(CONF_ERSTELLT, _jetzt_iso())
                daten[CONF_GEAENDERT] = _jetzt_iso()
                # The calendar event the exam came from is not part of the form
                daten[CONF_KALENDER_UID] = subentry.data.get(CONF_KALENDER_UID)
                return self.async_update_and_abort(
                    self._get_entry(),
                    subentry,
                    title=self._titel(daten),
                    data=daten,
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                self._schema(), user_input or self._vorbelegung(subentry.data)
            ),
            errors=fehler,
        )

    def _bekannte_lektionen(self) -> list[str]:
        """Return the lessons of the subject plus the ones already selected."""
        entry = self._get_entry()
        lektionen: list[str] = []
        if entry.state is ConfigEntryState.LOADED:
            lektionen = list(entry.runtime_data.lektionen(self._fach_id))
        if self.source == SOURCE_RECONFIGURE:
            gewaehlt = self._get_reconfigure_subentry().data.get(CONF_LEKTIONEN, [])
            lektionen.extend(x for x in gewaehlt if x not in lektionen)
        return lektionen

    def _schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_ART, default=ArbeitArt.ARBEIT.value): SelectSelector(
                    SelectSelectorConfig(
                        options=[art.value for art in ArbeitArt],
                        translation_key="art",
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_DATUM): DateSelector(),
                vol.Required(CONF_THEMA): TextSelector(),
                vol.Optional(CONF_LEKTIONEN): SelectSelector(
                    SelectSelectorConfig(
                        options=self._bekannte_lektionen(),
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_ABFRAGEN_PRO_TAG, default=DEFAULT_ABFRAGEN_PRO_TAG
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1, max=24, step=1, mode=NumberSelectorMode.BOX
                    )
                ),
                vol.Required(
                    CONF_START_TAGE_VORHER, default=DEFAULT_START_TAGE_VORHER
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1, max=90, step=1, mode=NumberSelectorMode.BOX
                    )
                ),
                vol.Required(CONF_INTENSIVIERUNG, default=True): BooleanSelector(),
                vol.Optional(CONF_ANTWORTFRIST): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=MAX_TIMEOUT_MINUTEN,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
                # Home Assistant shows a date in an empty date field, so the
                # plan has to be switched on explicitly
                vol.Required(SIMULATION_AKTIV, default=False): BooleanSelector(),
                vol.Optional(CONF_SIMULATION_UM): DateTimeSelector(),
                vol.Optional(
                    CONF_SIMULATION_ANZAHL, default=DEFAULT_SIMULATION_ANZAHL
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1, max=30, step=1, mode=NumberSelectorMode.BOX
                    )
                ),
            }
        )

    @staticmethod
    def _vorbelegung(daten: Mapping[str, Any]) -> dict[str, Any]:
        """Return stored data the way the form shows it: local date and time."""
        werte = dict(daten)
        zeitpunkt = dt_util.parse_datetime(werte.get(CONF_SIMULATION_UM) or "")
        if zeitpunkt is None:
            werte.pop(CONF_SIMULATION_UM, None)
        else:
            werte[CONF_SIMULATION_UM] = dt_util.as_local(zeitpunkt).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        werte.setdefault(SIMULATION_AKTIV, zeitpunkt is not None)
        return werte

    def _pruefe(
        self, eingabe: dict[str, Any], sim_bisher: str | None = None
    ) -> tuple[dict[str, Any], dict[str, str]]:
        fehler: dict[str, str] = {}
        daten = dict(eingabe)
        daten[CONF_FACH_ID] = self._fach_id
        daten[CONF_THEMA] = daten[CONF_THEMA].strip()
        daten[CONF_LEKTIONEN] = [
            lektion.strip()
            for lektion in daten.get(CONF_LEKTIONEN, [])
            if lektion.strip()
        ]
        daten[CONF_ABFRAGEN_PRO_TAG] = int(daten[CONF_ABFRAGEN_PRO_TAG])
        daten[CONF_START_TAGE_VORHER] = int(daten[CONF_START_TAGE_VORHER])
        frist = daten.get(CONF_ANTWORTFRIST)
        daten[CONF_ANTWORTFRIST] = int(frist) if frist else None
        daten[CONF_SIMULATION_ANZAHL] = int(
            daten.get(CONF_SIMULATION_ANZAHL) or DEFAULT_SIMULATION_ANZAHL
        )
        # The form gives local time, stored is UTC like the panel sends it
        aktiv = bool(daten.pop(SIMULATION_AKTIV, False))
        zeitpunkt = (
            dt_util.parse_datetime(daten.get(CONF_SIMULATION_UM) or "")
            if aktiv
            else None
        )
        if zeitpunkt is None:
            daten[CONF_SIMULATION_UM] = None
            if aktiv:
                fehler[CONF_SIMULATION_UM] = "simulation_um_fehlt"
        else:
            if zeitpunkt.tzinfo is None:
                zeitpunkt = zeitpunkt.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
            daten[CONF_SIMULATION_UM] = dt_util.as_utc(zeitpunkt).isoformat()
            if (
                daten[CONF_SIMULATION_UM] != sim_bisher
                and zeitpunkt <= dt_util.utcnow()
            ):
                fehler[CONF_SIMULATION_UM] = "simulation_um_vergangen"
        if not daten[CONF_THEMA]:
            fehler[CONF_THEMA] = "thema_leer"
        if date.fromisoformat(daten[CONF_DATUM]) < dt_util.now().date():
            fehler[CONF_DATUM] = "datum_vergangen"
        return daten, fehler

    def _titel(self, daten: dict[str, Any]) -> str:
        fach = self._get_entry().subentries.get(self._fach_id)
        fach_titel = fach.title if fach else "?"
        return arbeit_titel(daten[CONF_DATUM], fach_titel, daten[CONF_THEMA])
