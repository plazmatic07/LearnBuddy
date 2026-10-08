"""Tests for reacting to what a child asks to practise."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.learnbuddy.ai import baue_wunsch_prompt, lies_wunsch
from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import AbfrageFilter, KindZustand
from custom_components.learnbuddy.storage import migrate_config
from custom_components.learnbuddy.verwaltung import VerwaltungError
from custom_components.learnbuddy.wunsch import Uebungswunsch, WunschFach

from .conftest import FACH_ID, KIND_ID, subentry

GENERATE = "custom_components.learnbuddy.ai._async_generate_data"
MATHE_ID = "fach2"


async def _sende(hass: HomeAssistant, nachricht: str) -> dict[str, Any]:
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"kind_id": KIND_ID, "text": nachricht},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    assert isinstance(ergebnis, dict)
    return ergebnis


def _gefragt(manager: LearnBuddyManager) -> int:
    return sum(
        stat.gefragt
        for aufgabe in manager.task_stores[FACH_ID].aufgaben.values()
        for stat in aufgabe.statistik.values()
    )


@pytest.fixture
async def mit_lektionen(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> MockConfigEntry:
    """Add a second lesson with other words."""
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {
            "fach_id": FACH_ID,
            "inhalt": "Katze; cat\nMaus; mouse\nVogel; bird\n",
            "lektion": "Unit 4",
        },
        blocking=True,
    )
    return mit_vokabeln


async def test_wunsch_mit_zahl_startet_serie(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    ergebnis = await _sende(hass, "Ich möchte 3 Aufgaben Englisch üben")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 3}
    start = notify_calls[-2].data["message"]
    assert "3 Aufgaben aus Englisch" in start
    zustand = manager.zustand(KIND_ID)
    assert zustand.offene_frage is not None
    assert zustand.zusatz_offen == 2
    assert zustand.zusatz_filter == AbfrageFilter()


async def test_wunsch_ohne_zahl_fragt_nach(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    ergebnis = await _sende(hass, "Frag mich die Vokabeln aus der Unit 4 ab")
    assert ergebnis == {"ergebnis": "wunsch_nachfrage"}
    assert "Wie viele Aufgaben aus Englisch, Unit 4" in notify_calls[-1].data["message"]
    zustand = manager.zustand(KIND_ID)
    assert zustand.offene_frage is None
    assert zustand.wunsch_offen is not None
    assert zustand.wunsch_offen.lektion == "Unit 4"

    # The stored wish survives a restart
    neu = KindZustand.from_dict(zustand.to_dict())
    assert neu.wunsch_offen == zustand.wunsch_offen

    ergebnis = await _sende(hass, "4")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 4}
    assert zustand.wunsch_offen is None
    assert zustand.zusatz_filter.lektionen == ("Unit 4",)

    # The whole series stays within the lesson
    aufgaben = manager.task_stores[FACH_ID].aufgaben
    gesehen = []
    for _ in range(4):
        frage = zustand.offene_frage
        assert frage is not None
        gesehen.append(aufgaben[frage.aufgabe_id].lektion)
        await _sende(hass, "weiß nicht")
    assert gesehen == ["Unit 4"] * 4
    assert zustand.offene_frage is None
    assert zustand.zusatz_offen == 0

    # A thumbs up goes on in the same lesson
    await _sende(hass, "👍")
    frage = zustand.offene_frage
    assert frage is not None
    assert aufgaben[frage.aufgabe_id].lektion == "Unit 4"


async def test_nachfrage_ohne_zahl_verfaellt(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    await _sende(hass, "Englisch üben")
    ergebnis = await _sende(hass, "keine Ahnung")
    assert ergebnis == {"ergebnis": "keine_offene_frage"}
    assert manager.zustand(KIND_ID).wunsch_offen is None
    # The number comes too late now
    assert await _sende(hass, "5") == {"ergebnis": "keine_offene_frage"}


async def test_nachfrage_laeuft_ab(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    await _sende(hass, "Englisch üben")
    assert manager.zustand(KIND_ID).wunsch_offen is not None
    freezer.tick(11 * 60)
    assert await _sende(hass, "5") == {"ergebnis": "keine_offene_frage"}
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_wunsch_wird_gekuerzt(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    ergebnis = await _sende(hass, "gib mir 50 Englisch Aufgaben")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 20}
    assert "Mehr als 20" in notify_calls[-2].data["message"]


async def test_wunsch_geht_vor_offener_frage(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    zustand = manager.zustand(KIND_ID)
    assert zustand.offene_frage is not None
    assert _gefragt(manager) == 1
    heute = manager.verwaltung.fortschritt(KIND_ID, 7)["reihe"][-1]
    assert heute["gefragt"] == 1

    ergebnis = await _sende(hass, "Ich will lieber Unit 4 üben, 2 Stück")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 2}
    # The first question does not count, the new one does
    assert _gefragt(manager) == 1
    frage = zustand.offene_frage
    assert frage is not None
    assert manager.task_stores[FACH_ID].aufgaben[frage.aufgabe_id].lektion == "Unit 4"
    heute = manager.verwaltung.fortschritt(KIND_ID, 7)["reihe"][-1]
    assert (heute["gefragt"], heute["falsch"]) == (1, 0)
    assert all(
        stat.falsch == 0
        for aufgabe in manager.task_stores[FACH_ID].aufgaben.values()
        for stat in aufgabe.statistik.values()
    )


async def test_antwort_bleibt_antwort(
    hass: HomeAssistant, mit_lektionen: MockConfigEntry
) -> None:
    """A single word or an unclear wish answers the open question."""
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    for nachricht in ("Englisch", "ich will üben"):
        await hass.services.async_call(
            DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
        )
        with patch(GENERATE, AsyncMock()) as ki:
            ergebnis = await _sende(hass, nachricht)
        assert ergebnis["ergebnis"] == "falsch"
        ki.assert_not_called()
        manager.zustand(KIND_ID).zusatz_offen = 0


async def test_keine_aufgaben_in_der_lektion(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    manager.task_stores[FACH_ID].lektion_hinzufuegen("Unit 9")
    ergebnis = await _sende(hass, "Unit 9 üben")
    assert ergebnis == {"ergebnis": "keine_aufgaben"}
    assert (
        "in Englisch, Unit 9 gibt es gerade keine" in (notify_calls[-1].data["message"])
    )
    assert manager.zustand(KIND_ID).wunsch_offen is None


async def test_offene_frage_bleibt_ohne_aufgaben(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    """A wish that cannot be fulfilled does not take the open question back."""
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    manager.task_stores[FACH_ID].lektion_hinzufuegen("Unit 9")
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    frage = manager.zustand(KIND_ID).offene_frage
    ergebnis = await _sende(hass, "Unit 9 üben")
    assert ergebnis == {"ergebnis": "keine_aufgaben"}
    assert "Unit 9 gibt es gerade keine" in notify_calls[-1].data["message"]
    assert manager.zustand(KIND_ID).offene_frage is frage
    assert _gefragt(manager) == 1


async def test_unklarer_wunsch_ohne_ki(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    with patch(GENERATE, AsyncMock()) as ki:
        ergebnis = await _sende(hass, "ich will das mit den Tieren üben")
    assert ergebnis == {"ergebnis": "wunsch_unklar"}
    assert "Du kannst üben: Englisch" in notify_calls[-1].data["message"]
    # No AI is configured in the options
    ki.assert_not_called()


async def test_ausgeschaltetes_kind(
    hass: HomeAssistant, mit_lektionen: MockConfigEntry
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    manager.zustand(KIND_ID).aktiv = False
    ergebnis = await _sende(hass, "Englisch üben")
    assert ergebnis == {"ergebnis": "keine_offene_frage"}


async def test_simulation_kennt_keine_wuensche(
    hass: HomeAssistant, mit_lektionen: MockConfigEntry
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    with patch.object(
        manager, "_async_sim_antwort", AsyncMock(return_value={"ergebnis": "sim"})
    ) as sim:
        manager.zustand(KIND_ID).simulation = object()  # type: ignore[assignment]
        assert await manager.async_antwort(KIND_ID, "Englisch üben") == {
            "ergebnis": "sim"
        }
        manager.zustand(KIND_ID).simulation = None
    sim.assert_awaited_once()


# ----------------------------------------------------------------------
# AI as a fallback
# ----------------------------------------------------------------------


@pytest.fixture
async def mit_ki(
    hass: HomeAssistant, config_entry: MockConfigEntry, mit_lektionen: MockConfigEntry
) -> MockConfigEntry:
    hass.config_entries.async_update_entry(
        config_entry, options={**config_entry.options, "ki_entity": "ai_task.test"}
    )
    await hass.async_block_till_done()
    return config_entry


async def test_ki_deutet_wunsch(
    hass: HomeAssistant, mit_ki: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mit_ki.runtime_data
    antwort = {"fach": "1", "lektion": "unit 4", "anzahl": "0"}
    with patch(GENERATE, AsyncMock(return_value=antwort)) as ki:
        ergebnis = await _sende(hass, "ich will 2 von den Tieren üben")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 2}
    assert manager.zustand(KIND_ID).zusatz_filter.lektionen == ("Unit 4",)
    prompt = ki.call_args.kwargs["instructions"]
    assert "Englisch (lessons: Unit 3; Unit 4)" in prompt
    assert "Tieren" in prompt
    # The name of the child is not passed on
    assert "Max" not in prompt


@pytest.mark.parametrize(
    "antwort", [{"fach": "0"}, {"fach": "7"}, {"fach": "x"}, "kaputt", None]
)
async def test_ki_ohne_ergebnis(
    hass: HomeAssistant,
    mit_ki: MockConfigEntry,
    notify_calls: list[ServiceCall],
    antwort: Any,
) -> None:
    with patch(GENERATE, AsyncMock(return_value=antwort)):
        ergebnis = await _sende(hass, "ich will das mit den Tieren üben")
    assert ergebnis == {"ergebnis": "wunsch_unklar"}


async def test_ki_faellt_aus(hass: HomeAssistant, mit_ki: MockConfigEntry) -> None:
    with patch(GENERATE, AsyncMock(side_effect=RuntimeError)):
        ergebnis = await _sende(hass, "ich will das mit den Tieren üben")
    assert ergebnis == {"ergebnis": "wunsch_unklar"}


async def test_ki_schalter_aus(
    hass: HomeAssistant, config_entry: MockConfigEntry, mit_ki: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(
        config_entry, options={**config_entry.options, "wunsch_ki": False}
    )
    await hass.async_block_till_done()
    with patch(GENERATE, AsyncMock()) as ki:
        ergebnis = await _sende(hass, "ich will das mit den Tieren üben")
    assert ergebnis == {"ergebnis": "wunsch_unklar"}
    ki.assert_not_called()


async def test_eindeutiger_wunsch_braucht_keine_ki(
    hass: HomeAssistant, mit_ki: MockConfigEntry
) -> None:
    with patch(GENERATE, AsyncMock()) as ki:
        ergebnis = await _sende(hass, "Englisch üben")
    assert ergebnis == {"ergebnis": "wunsch_nachfrage"}
    ki.assert_not_called()


def test_lies_wunsch() -> None:
    faecher = [WunschFach("en", "Englisch", lektionen=("Unit 1",))]
    assert lies_wunsch({"fach": 1, "lektion": "Unit 1", "anzahl": 3}, faecher) == (
        Uebungswunsch("en", "Unit 1", 3)
    )
    # An unknown lesson is dropped, the subject stays
    assert lies_wunsch({"fach": "1", "lektion": "Unit 8"}, faecher) == (
        Uebungswunsch("en")
    )
    assert lies_wunsch({"fach": "1", "anzahl": "viele"}, faecher) is None
    prompt = baue_wunsch_prompt(nachricht="#" * 500, faecher=faecher)
    assert prompt.count("#") == 300


def test_migration_1_13() -> None:
    alt = {
        "kinder": {"k": {"aktiv": True}},
        "arbeiten": {},
        "aufgaben_dateien": [],
        "kalender_ignoriert": {},
    }
    neu = migrate_config(1, 12, alt)
    assert neu["kinder"]["k"]["wunsch_offen"] is None
    assert neu["kinder"]["k"]["zusatz_filter"] is None
    zustand = KindZustand.from_dict({"aktiv": True})
    assert (zustand.wunsch_offen, zustand.zusatz_filter) == (None, AbfrageFilter())


async def test_wunsch_mit_zweitem_fach(
    hass: HomeAssistant, notify_calls: list[ServiceCall]
) -> None:
    """With two subjects the subject of the wish is asked, not the last one."""
    from .conftest import FACH_DATEN, KIND_DATEN  # noqa: PLC0415

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de"},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", KIND_DATEN),
            subentry("fach", FACH_ID, "Englisch (Max)", FACH_DATEN),
            subentry(
                "fach",
                MATHE_ID,
                "Latein (Max)",
                {**FACH_DATEN, "name": "Latein", "sprachen": ["de", "la"]},
            ),
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    for fach_id, inhalt in ((FACH_ID, "Hund; dog\n"), (MATHE_ID, "Hund; canis\n")):
        await hass.services.async_call(
            DOMAIN,
            "import_tasks",
            {"fach_id": fach_id, "inhalt": inhalt},
            blocking=True,
        )
    manager: LearnBuddyManager = entry.runtime_data

    # "Vokabeln" alone fits two subjects
    assert await _sende(hass, "Vokabeln üben") == {"ergebnis": "wunsch_unklar"}
    assert "Englisch, Latein" in notify_calls[-1].data["message"]

    for _ in range(3):
        ergebnis = await _sende(hass, "noch 1 Latein")
        assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 1}
        frage = manager.zustand(KIND_ID).offene_frage
        assert frage is not None
        assert frage.fach_id == MATHE_ID
        await _sende(hass, "canis")


# ----------------------------------------------------------------------
# Asking several questions from the panel
# ----------------------------------------------------------------------


async def test_abfrage_mit_lektionen_und_anzahl(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    await manager.verwaltung.frage_stellen(
        KIND_ID, FACH_ID, {"lektionen": ["Unit 4"]}, 3
    )
    assert (
        "Es kommen 3 Aufgaben aus Englisch (Unit 4)"
        in (notify_calls[-2].data["message"])
    )
    zustand = manager.zustand(KIND_ID)
    assert zustand.zusatz_offen == 2
    assert zustand.zusatz_filter.lektionen == ("Unit 4",)
    aufgaben = manager.task_stores[FACH_ID].aufgaben
    gesehen = []
    for _ in range(3):
        frage = zustand.offene_frage
        assert frage is not None
        gesehen.append(aufgaben[frage.aufgabe_id].lektion)
        await _sende(hass, "weiß nicht")
    assert gesehen == ["Unit 4"] * 3
    assert zustand.offene_frage is None


async def test_abfrage_eine_frage_aus_lektion(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    gesendet = len(notify_calls)
    await manager.verwaltung.frage_stellen(
        KIND_ID, FACH_ID, {"lektionen": ["Unit 3", "Unit 4"]}, 1
    )
    # Only the question itself, with its greeting
    assert len(notify_calls) == gesendet + 1
    assert notify_calls[-1].data["message"].startswith("Hallo Max!")
    assert manager.zustand(KIND_ID).zusatz_offen == 0


async def test_abfrage_ohne_fach(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    await manager.verwaltung.frage_stellen(KIND_ID, None, None, 2)
    assert "Es kommen 2 Aufgaben." in notify_calls[-2].data["message"]
    await _sende(hass, "weiß nicht")
    assert manager.zustand(KIND_ID).offene_frage is not None
    await _sende(hass, "weiß nicht")
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_abfrage_fehler(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    with pytest.raises(VerwaltungError):
        await manager.verwaltung.frage_stellen(
            KIND_ID, FACH_ID, {"lektionen": ["Unit 99"]}, 2
        )
    manager.task_stores[FACH_ID].lektion_hinzufuegen("Unit 9")
    gesendet = len(notify_calls)
    with pytest.raises(VerwaltungError) as fehler:
        await manager.verwaltung.frage_stellen(
            KIND_ID, FACH_ID, {"lektionen": ["Unit 9"]}, 2
        )
    assert fehler.value.schluessel == "keine_aufgaben"
    assert len(notify_calls) == gesendet
    manager.zustand(KIND_ID).simulation = object()  # type: ignore[assignment]
    with pytest.raises(VerwaltungError) as fehler:
        await manager.verwaltung.frage_stellen(KIND_ID, FACH_ID, {}, 2)
    assert fehler.value.schluessel == "simulation_laeuft"
    manager.zustand(KIND_ID).simulation = None


def test_migration_1_14() -> None:
    alt = {
        "kinder": {"a": {"zusatz_lektion": "Unit 1"}, "b": {"zusatz_lektion": None}},
        "arbeiten": {},
        "aufgaben_dateien": [],
        "kalender_ignoriert": {},
    }
    neu = migrate_config(1, 13, alt)
    assert neu["kinder"]["a"] == {"zusatz_filter": {"lektionen": ["Unit 1"]}}
    assert neu["kinder"]["b"] == {"zusatz_filter": None}
    zustand = KindZustand.from_dict(neu["kinder"]["a"])
    assert zustand.zusatz_filter == AbfrageFilter(lektionen=("Unit 1",))
    voll = AbfrageFilter(("A",), 10, 20, 50)
    assert AbfrageFilter.from_dict(voll.to_dict()) == voll
    assert KindZustand.from_dict({}).zusatz_filter == AbfrageFilter()


async def test_abfrage_nach_seite_und_fehlerquote(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_lektionen.runtime_data
    verwaltung = manager.verwaltung
    aufgaben = list(manager.task_stores[FACH_ID].aufgaben.values())
    assert len(aufgaben) == 5
    for seite, aufgabe in zip((10, 11, 12, 13, None), aufgaben, strict=True):
        aufgabe.seite = seite
    # One task was answered wrong twice and right once, one only right
    stat = next(iter(aufgaben[1].statistik.values()), None)
    if stat is None:
        stat = aufgaben[1].statistik_fuer(manager.faecher[FACH_ID].richtungen[0])
    stat.falsch, stat.richtig = 2, 1
    gut = aufgaben[2].statistik_fuer(manager.faecher[FACH_ID].richtungen[0])
    gut.richtig = 3
    aufgaben[3].geprueft = False

    def umfang(**auswahl: Any) -> int:
        return verwaltung.abfrage_umfang(KIND_ID, FACH_ID, auswahl)

    # The task that waits for its approval never takes part
    assert umfang() == 4
    assert verwaltung.abfrage_umfang(KIND_ID, None, {"seite_von": 99}) == 4
    assert umfang(seite_von=11) == 2
    assert umfang(seite_bis=11) == 2
    assert umfang(seite_von=11, seite_bis=11) == 1
    assert umfang(fehlerquote_ab=50) == 1
    assert umfang(fehlerquote_ab=70) == 0
    assert umfang(fehlerquote_ab=1, seite_von=12) == 0
    assert umfang(lektionen=["Unit 4"], seite_von=12) == 1
    with pytest.raises(VerwaltungError) as fehler:
        umfang(seite_von=12, seite_bis=11)
    assert fehler.value.schluessel == "seiten_verdreht"

    await verwaltung.frage_stellen(KIND_ID, FACH_ID, {"fehlerquote_ab": 50}, 2)
    zustand = manager.zustand(KIND_ID)
    # The overview shows the running series and what it is limited to
    laufend = verwaltung.dashboard(KIND_ID)["zustand"]["abfrage"]
    assert (laufend["weitere"], laufend["fehlerquote_ab"]) == (1, 50)
    for _ in range(2):
        frage = zustand.offene_frage
        assert frage is not None
        assert frage.aufgabe_id == aufgaben[1].id
        await _sende(hass, "weiß nicht")
    assert zustand.offene_frage is None

    with pytest.raises(VerwaltungError) as fehler:
        await verwaltung.frage_stellen(KIND_ID, FACH_ID, {"seite_von": 500}, 1)
    assert fehler.value.schluessel == "keine_aufgaben"


async def test_ws_ask_count(
    hass: HomeAssistant,
    mit_lektionen: MockConfigEntry,
    hass_ws_client: Any,
) -> None:
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {
            "type": "learnbuddy/ask_count",
            "kind_id": KIND_ID,
            "fach_id": FACH_ID,
            "lektionen": ["Unit 4"],
            "seite_von": None,
            "fehlerquote_ab": None,
        }
    )
    antwort = await client.receive_json()
    assert antwort["result"] == {"aufgaben": 3}
    await client.send_json_auto_id(
        {
            "type": "learnbuddy/ask",
            "kind_id": KIND_ID,
            "fach_id": FACH_ID,
            "seite_von": 7,
            "anzahl": 2,
        }
    )
    antwort = await client.receive_json()
    assert antwort["error"]["message"] == "keine_aufgaben"
