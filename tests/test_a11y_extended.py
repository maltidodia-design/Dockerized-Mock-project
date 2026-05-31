"""Extended automated accessibility tests (Section 508 / WCAG 2.1 AA).

[tests/test_accessibility.py](test_accessibility.py) covers the lowest-hanging
508 rules (h1 present, inputs labelled, named buttons/links). This file adds
the next layer — still hand-rolled (no headless browser dependency yet) but
covering rules that a real `axe` / `pa11y` scan would also catch.

A proper next step is wiring in axe-core via Playwright; until then this
file documents the rules in executable form. Known gaps are marked ``xfail``
with a reason; remove the marker as part of the fix PR so the test then
guards the fix forever.
"""
import pytest
from bs4 import BeautifulSoup


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _soup(http, base_url, path):
    resp = http.get(base_url + path)
    assert resp.status_code == 200, f"GET {path} -> {resp.status_code}"
    return BeautifulSoup(resp.text, "html.parser")


# Primary pages on which every a11y rule below must hold. The take page
# needs a real quiz id, so it's parametrised separately.
PRIMARY_PATHS = ["/", "/create"]


# --------------------------------------------------------------------------- #
# Page metadata — title and language
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", PRIMARY_PATHS)
def test_page_has_non_empty_title(live_server, http, path):
    soup = _soup(http, live_server, path)
    title = soup.find("title")
    assert title is not None and title.get_text(strip=True), (
        f"{path}: missing or empty <title> (screen readers announce this on load)"
    )


@pytest.mark.xfail(
    reason=(
        "Known gap: templates use <html> without a lang attribute. Required by "
        "WCAG 3.1.1 so screen readers select the correct pronunciation engine."
    )
)
@pytest.mark.parametrize("path", PRIMARY_PATHS)
def test_html_root_declares_language(live_server, http, path):
    soup = _soup(http, live_server, path)
    html = soup.find("html")
    assert html is not None and html.get("lang"), (
        f"{path}: <html> has no lang attribute"
    )


# --------------------------------------------------------------------------- #
# Heading order — no skipped levels (WCAG 1.3.1)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", PRIMARY_PATHS)
def test_heading_levels_do_not_skip(live_server, http, path):
    soup = _soup(http, live_server, path)
    levels = [int(h.name[1]) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    assert levels and levels[0] == 1, f"{path}: first heading is not h1 ({levels})"
    for prev, cur in zip(levels, levels[1:]):
        assert cur <= prev + 1, (
            f"{path}: heading order skips a level "
            f"(h{prev} -> h{cur}, full sequence {levels})"
        )


# --------------------------------------------------------------------------- #
# Duplicate id attributes (WCAG 4.1.1)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", PRIMARY_PATHS)
def test_no_duplicate_ids(live_server, http, path):
    soup = _soup(http, live_server, path)
    ids = [el["id"] for el in soup.find_all(attrs={"id": True})]
    duplicates = {x for x in ids if ids.count(x) > 1}
    assert not duplicates, f"{path}: duplicate id values found: {duplicates}"


# --------------------------------------------------------------------------- #
# Take-quiz page — radio-group semantics
# --------------------------------------------------------------------------- #

@pytest.mark.xfail(
    reason=(
        "Known gap: take_quiz.html wraps each question in <div class=\"question\"> "
        "instead of <fieldset><legend>. Screen readers cannot announce the "
        "question text as the group label for the radio set. WCAG 1.3.1 / 3.3.2."
    )
)
def test_take_page_groups_radios_with_fieldset_and_legend(live_server, http, create_quiz):
    take_url = create_quiz("A11y Fieldset Quiz", [
        {"text": "Q1", "choices": ["a", "b"], "answer_index": 0},
        {"text": "Q2", "choices": ["x", "y"], "answer_index": 1},
    ])
    resp = http.get(take_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    fieldsets = soup.find_all("fieldset")
    assert len(fieldsets) >= 2, (
        f"Expected one <fieldset> per question, found {len(fieldsets)}"
    )
    for fs in fieldsets:
        assert fs.find("legend"), "Fieldset without a <legend>"


def test_take_page_radio_groups_share_name(live_server, http, create_quiz):
    """Radios for the same question must share a `name` so the browser groups
    them and only one can be selected — a functional a11y / UX requirement."""
    take_url = create_quiz("Radio Grouping Quiz", [
        {"text": "Q", "choices": ["a", "b", "c"], "answer_index": 1},
    ])
    soup = BeautifulSoup(http.get(take_url).text, "html.parser")
    radios = soup.find_all("input", attrs={"type": "radio"})
    assert radios, "No radio inputs rendered on the take page"
    names = {r.get("name") for r in radios}
    assert names == {"question-0"}, (
        f"Radios are not all in one group; names found: {names}"
    )
