"""Expose the images of tasks as a media source.

AI task entities take attachments as media sources that resolve to a local
file. Nothing can be browsed here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.media_player.const import MediaClass
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)

from .bilder import URL_BILDER, mime_typ
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def async_get_media_source(hass: HomeAssistant) -> LearnBuddyMediaSource:
    """Set up the media source."""
    return LearnBuddyMediaSource(hass)


class LearnBuddyMediaSource(MediaSource):
    """Resolve the images of tasks."""

    name: str = "LearnBuddy"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the media source."""
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve an image id to its file."""
        entries = self.hass.config_entries.async_loaded_entries(DOMAIN)
        pfad = entries[0].runtime_data.bilder.pfad(item.identifier) if entries else None
        if pfad is None:
            raise Unresolvable(f"Unknown image: {item.identifier}")
        return PlayMedia(
            f"{URL_BILDER}/{item.identifier}", mime_typ(item.identifier), path=pfad
        )

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        """Return an empty folder: the images are not meant to be browsed."""
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=None,
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=self.name,
            can_play=False,
            can_expand=False,
            children=[],
        )
