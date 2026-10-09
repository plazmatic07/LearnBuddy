"""Tests for sending to children that are reached via WhatsApp."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.learnbuddy.const import DOMAIN

from .conftest import KIND_ID
from .test_bildversand import _setup
from .test_mathe_ablauf import MATHE_ID
from custom_components.learnbuddy.models import MatheAufgabe


async def _whatsapp(hass: HomeAssistant, kennung: str | None) -> None:
    eintrag = er.async_get(hass).async_get_or_create(
        "notify", "whatsapp", "ziel1", suggested_object_id="whatsapp_schule"
    )
    entry = await _setup(
        hass,
        notify_service=None,
        notify_target=None,
        notify_entity=eintrag.entity_id,
        absender_kennung=kennung,
    )
    entry.runtime_data.task_stores[MATHE_ID].add(
        MatheAufgabe(fach_id=MATHE_ID, aufgabe="1+1", loesung="2")
    )


async def test_whatsapp_schreibt_an_die_absendernummer(hass: HomeAssistant) -> None:
    """The question goes to the sender ID, not to the fixed number of the entity."""
    nachrichten = async_mock_service(hass, "whatsapp", "send_message")
    texte = async_mock_service(hass, "notify", "send_message")
    await _whatsapp(hass, "+49 171 9390814")

    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()
    assert not texte
    assert len(nachrichten) == 1
    assert nachrichten[0].data["number"] == "491719390814"


async def test_whatsapp_ohne_absender_nutzt_die_entitaet(hass: HomeAssistant) -> None:
    nachrichten = async_mock_service(hass, "whatsapp", "send_message")
    texte = async_mock_service(hass, "notify", "send_message")
    await _whatsapp(hass, None)

    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()
    assert not nachrichten
    assert len(texte) == 1
