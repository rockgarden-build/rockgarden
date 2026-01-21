"""Obsidian-specific syntax processing."""

from rockgarden.obsidian.embeds import process_image_embeds
from rockgarden.obsidian.wikilinks import process_wikilinks

__all__ = ["process_wikilinks", "process_image_embeds"]
