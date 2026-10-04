# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** I picked 4 of 5 because search_listings works by matching keywords. Some ways a person might phrase a request won't share enough words with the listing's title or description, even if a human would agree it's a good match.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** I'm saying 5 of 5 here because this doesn't depend on the model at all — it's just checking if search_listings returned an empty list. That's a plain yes/no check, so there's no reason it should work sometimes and not others, unless something is actually broken.

---

## 3. Same item all the way through

The item that search_listings picks is the exact same item that gets used all the way through to the fit card, every single time (5 of 5 tries). I'll check this by comparing the item's id at each step.

**Why this target:** I expect this to always work because it's just passing the same piece of data along — there's no reason it should sometimes work and sometimes not, unless there's a real bug.

---

## 4. Different wording, same key facts

If I create a fit card for the same item three times, the wording should be a little different each time, but all three should still mention the item's name and price. This should happen 3 out of 3 times.

**Why this target:** The model naturally writes things a bit differently each time, so I don't expect the exact same sentence twice. But the name and price should always show up, because that part comes from my own code, not the model guessing.

---

## 5. Size search actually matches sizes correctly

When someone asks for a specific size, like "size M," the search should not return things that are the wrong size just because the letters happen to match (like matching "M" inside "US 9" or "XL"). This should work correctly in at least 4 of 5 tries.

**Why this target:** I'm not saying 5 of 5 because some size labels in the data are written in unusual ways, and I might not catch every single format perfectly.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it instead.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point. A number you missed stays where it is, gets diagnosed, and
     gets a fix attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->