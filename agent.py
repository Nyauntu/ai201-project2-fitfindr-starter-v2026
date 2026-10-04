"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable  # noqa: F401 — used starting unit 4


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """A fresh session for one user interaction."""
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


# ── query parsing ─────────────────────────────────────────────────────────────

_PRICE_RE = re.compile(r"\$\s*(\d+(?:\.\d+)?)")
_SIZE_RE = re.compile(r"\bsize\s+([A-Za-z0-9/]+)\b", re.IGNORECASE)


def _parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a max_price out of free text, with regex.

    - max_price comes from a $-prefixed number anywhere in the query.
    - size comes from an explicit "size X" phrase.
    - description is whatever text is left after removing those phrases,
      used for keyword matching in search_listings.
    """
    max_price = None
    price_match = _PRICE_RE.search(query)
    if price_match:
        max_price = float(price_match.group(1))

    size = None
    size_match = _SIZE_RE.search(query)
    if size_match:
        size = size_match.group(1)

    description = query
    if price_match:
        description = _PRICE_RE.sub("", description)
        description = re.sub(
            r"\b(under|below|over|around)\b", "", description, flags=re.IGNORECASE
        )
    if size_match:
        description = _SIZE_RE.sub("", description)

    description = re.sub(r"\s+", " ", description).strip(" ,")

    return {"description": description, "size": size, "max_price": max_price}


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Branch rule: if search_listings returns an empty list, put a specific
    message in session["error"] and stop — do not call suggest_outfit.
    Otherwise, take the first result and continue through suggest_outfit and
    create_fit_card.
    """
    session = new_session(query, wardrobe)

    # This loop runs straight through without repeating, so the count never
    # climbs — but the check stays in as the habit the brief asks for.
    trace.check_iterations(1)

    parsed = _parse_query(query)
    session["parsed"] = parsed

    results = search_listings(
        description=parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )
    session["search_results"] = results

    # ⚠️ THE BRANCH.
    if not results:
        session["error"] = (
            "No listings matched your search. Try raising your price limit, "
            "removing the size filter, or using broader keywords."
        )
        return session

    session["selected_item"] = results[0]

    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )