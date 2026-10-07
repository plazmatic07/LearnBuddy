"""Tests for the data model."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from types import MappingProxyType

from homeassistant.config_entries import ConfigSubentry

from custom_components.learnbuddy.models import (
    Arbeit,
    ArbeitArt,
    AufgabenTyp,
    Fach,
    Kind,
    KindZustand,
    OffeneFrage,
    Quelle,
    Statistik,
    Vokabel,
    richtung,
    richtung_teile,
)

JETZT = datetime(2026, 10, 6, 15, 0, tzinfo=UTC)


def _subentry(typ: str, data: dict[str, object], sid: str = "sub1") -> ConfigSubentry:
    return ConfigSubentry(
        data=MappingProxyType(data),
        subentry_id=sid,
        subentry_type=typ,
        title="x",
        unique_id=None,
    )


def test_richtung_roundtrip() -> None:
    assert richtung("de", "en") == "de>en"
    assert richtung_teile("de>en") == ("de", "en")


def test_statistik_roundtrip() -> None:
    stat = Statistik(box=3, richtig=4, falsch=1, zuletzt_gefragt=JETZT)
    assert Statistik.from_dict(stat.to_dict()) == stat
    assert Statistik.from_dict({}) == Statistik()
    # Data from before questions were counted starts with the answered ones
    assert Statistik.from_dict({"richtig": 2, "falsch": 1}).gefragt == 3
    assert Statistik.from_dict({"gefragt": 9, "richtig": 2}).gefragt == 9


def test_vokabel_roundtrip() -> None:
    vokabel = Vokabel(
        fach_id="f1",
        frage={"de": "Hund", "en": "dog"},
        alternativen={"en": ["hound"]},
        hinweis="Nomen",
        seite=226,
        lektion="Unit 3",
        quelle=Quelle.UPLOAD,
        geprueft=False,
    )
    vokabel.statistik_fuer("de>en").richtig = 2
    daten = vokabel.to_dict()
    assert daten["typ"] == "vokabel"
    assert daten["statistik"]["de>en"]["richtig"] == 2
    assert Vokabel.from_dict(daten) == vokabel


def test_vokabel_defaults() -> None:
    eins = Vokabel(fach_id="f1", frage={"de": "a", "en": "b"})
    zwei = Vokabel(fach_id="f1", frage={"de": "a", "en": "b"})
    assert eins.id != zwei.id
    assert eins.erstellt.tzinfo is not None
    assert eins.statistik_fuer("de>en") is eins.statistik_fuer("de>en")


def test_kind_from_subentry_defaults() -> None:
    kind = Kind.from_subentry(_subentry("kind", {"name": "Max"}, "k1"))
    assert kind.id == "k1"
    assert kind.name == "Max"
    assert kind.notify_entity is None
    assert kind.notify_target == ()
    assert kind.werktag_von == time(15, 0)


def test_kind_from_subentry_full() -> None:
    kind = Kind.from_subentry(
        _subentry(
            "kind",
            {
                "name": "Max",
                "klassenstufe": 6.0,
                "schulart": "gymnasium",
                "bundesland": "rp",
                "notify_service": "notify.whatsapp",
                "notify_target": ["49123"],
                "notify_data": {"a": 1},
                "absender_kennung": "49123",
                "werktag_von": "14:00:00",
                "werktag_bis": "18:30:00",
                "wochenende_aktiv": False,
            },
        )
    )
    assert kind.klassenstufe == 6
    assert kind.notify_service == "notify.whatsapp"
    assert kind.notify_target == ("49123",)
    assert kind.notify_data == {"a": 1}
    # 2026-10-06 is a Tuesday, 2026-10-10 a Saturday
    assert kind.fenster(date(2026, 10, 6)) == (time(14, 0), time(18, 30))
    assert kind.fenster(date(2026, 10, 10)) is None


def test_kind_fenster_wochenende() -> None:
    kind = Kind(id="k", name="Max")
    assert kind.fenster(date(2026, 10, 11)) == (time(10, 0), time(18, 0))


def test_fach_from_subentry() -> None:
    fach = Fach.from_subentry(
        _subentry(
            "fach",
            {"kind_id": "k1", "name": "Englisch", "sprachen": ["de", "en"]},
            "f1",
        )
    )
    assert fach.typ is AufgabenTyp.VOKABEL
    assert fach.richtungen == ("de>en", "en>de")
    assert Fach(id="f", kind_id="k", name="Mathe").richtungen == ()


def test_arbeit_from_subentry() -> None:
    arbeit = Arbeit.from_subentry(
        _subentry(
            "arbeit",
            {
                "fach_id": "f1",
                "datum": "2026-10-20",
                "art": "hue",
                "thema": "Unit 3",
                "lektionen": ["Unit 3"],
                "abfragen_pro_tag": 5.0,
                "start_tage_vorher": 10,
                "intensivierung": False,
            },
            "a1",
        )
    )
    assert arbeit.datum == date(2026, 10, 20)
    assert arbeit.art is ArbeitArt.HUE
    assert arbeit.lektionen == ("Unit 3",)
    assert arbeit.abfragen_pro_tag == 5
    assert arbeit.intensivierung is False

    minimal = Arbeit.from_subentry(
        _subentry("arbeit", {"fach_id": "f1", "datum": "2026-10-20"})
    )
    assert minimal.abfragen_pro_tag == 3
    assert minimal.start_tage_vorher == 7


def test_kind_zustand_roundtrip() -> None:
    frage = OffeneFrage(
        fach_id="f1",
        aufgabe_id="a1",
        richtung="de>en",
        gestellt_um=JETZT,
        timeout_um=JETZT.replace(hour=16),
        arbeit_id="x",
    )
    zustand = KindZustand(
        aktiv=True, pausiert_bis=JETZT, offene_frage=frage, letzte_frage_um=JETZT
    )
    assert KindZustand.from_dict(zustand.to_dict()) == zustand
    assert KindZustand.from_dict({}) == KindZustand()


def test_kind_zustand_pausiert() -> None:
    assert KindZustand(aktiv=False).ist_pausiert(JETZT)
    assert not KindZustand().ist_pausiert(JETZT)
    assert KindZustand(pausiert_bis=JETZT.replace(hour=16)).ist_pausiert(JETZT)
    assert not KindZustand(pausiert_bis=JETZT.replace(hour=14)).ist_pausiert(JETZT)
