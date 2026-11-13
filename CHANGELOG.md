# Changelog

## v0.2 – 2026-11-13

Added
- `update_office.py`: writes `office-data.js` from a CSV or JSON list. Options for title, goal, room and colours, `--watch` to rewrite whenever the list is saved, `--history` to keep time-stamped copies. Standard library only.
- `team.sample.csv` and `team.sample.json` as starting points.
- Light colours. Switch with the button in the header or the `T` key; the browser remembers the choice. New optional field `theme` in the data file: `dark`, `light` or `auto`.
- Keyboard: desks can be reached with `Tab`, arrow keys, `Home`, `End` and `1` to `6`. `R` reads the data file again at once. `?` shows the list of keys.
- Phone layout: tap a desk to read its sentence and role (before, both were hidden on narrow screens).
- Screen readers now get the sentence of a desk together with name, status and progress.
- Preview GIF and screenshots in `docs/`.

Fixed
- Phone layout: the status label "needs a human" was cut off at the edge of the card.

Changed
- README rewritten: quick start, data format, comparison, FAQ.

Not changed
- `office-data.js` files written for v0.1 work as they are. `update_example.py` is unchanged.

Tested
- Chrome 153, headless: 1600 px wide and phone widths 320, 360, 390 and 430 px. No script errors. Firefox and Safari are not tested.

## v0.1 – 2026-11-13

- First release: one room, up to six desks, `office-data.js`, `update_example.py`.
