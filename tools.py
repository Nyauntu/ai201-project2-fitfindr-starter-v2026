"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


def _tokenize(text: str) -> set[str]:
    """Lowercase, split on anything that isn't a letter or digit."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    Size matching uses whole tokens, not substrings: a listing's size string
    (e.g. "S/M", "US 9", "XL (oversized)") is split into tokens, and the query
    size must exactly match one whole token. This avoids false matches like
    "m" inside "us 9" or "l" inside "xl".

    Returns:
        A list of matching listing dicts, best match first, scored by keyword
        overlap between `description` and the listing's title/description/
        style_tags. Returns an empty list when nothing matches.
    """
    listings = load_listings()
    query_words = _tokenize(description)

    scored = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue

        if size is not None:
            size_tokens = _tokenize(listing["size"])
            if size.strip().lower() not in size_tokens:
                continue

        searchable_text = " ".join([
            listing["title"],
            listing["description"],
            " ".join(listing["style_tags"]),
        ])
        listing_words = _tokenize(searchable_text)
        score = len(query_words & listing_words)

        if score == 0:
            continue

        scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    With an empty wardrobe, returns general styling advice instead of failing.
    """
    items = wardrobe.get("items", [])

    item_summary = (
        f"Title: {new_item['title']}\n"
        f"Category: {new_item['category']}\n"
        f"Colors: {', '.join(new_item['colors'])}\n"
        f"Style tags: {', '.join(new_item['style_tags'])}"
    )

    if not items:
        prompt = (
            f"Someone is considering buying this thrifted item:\n\n"
            f"{item_summary}\n\n"
            f"They don't have any wardrobe items on file yet. Give general "
            f"styling advice for this item in one or two sentences — what "
            f"kinds of pieces would pair well with it."
        )
    else:
        wardrobe_lines = "\n".join(
            f"- {item['name']} ({item['category']}, {', '.join(item['colors'])})"
            for item in items
        )
        prompt = (
            f"Someone is considering buying this thrifted item:\n\n"
            f"{item_summary}\n\n"
            f"Their current wardrobe:\n{wardrobe_lines}\n\n"
            f"Suggest one or two outfit combinations that use specific pieces "
            f"from their wardrobe together with this new item. Name the "
            f"pieces by name."
        )

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    If `outfit` is empty or whitespace, returns a descriptive fallback message
    instead of calling the model with nothing to work from.
    """
    if not outfit or not outfit.strip():
        return (
            f"Found this one: {new_item['title']} for ${new_item['price']} "
            f"on {new_item['platform']}. Not enough wardrobe info yet to "
            f"suggest a full outfit, but it's a great piece on its own."
        )

    prompt = (
        f"Write a short, casual social-media caption (2-4 sentences) for "
        f"someone posting about a thrifted find.\n\n"
        f"Item: {new_item['title']}\n"
        f"Price: ${new_item['price']}\n"
        f"Platform: {new_item['platform']}\n"
        f"Outfit idea: {outfit}\n\n"
        f"Mention the item, its price, and the platform once each. Make it "
        f"sound like a real post, not a product description. Be specific "
        f"about the vibe."
    )
    return generate(prompt)