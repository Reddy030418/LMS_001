# TODO: Fix Library Services Cards Navigation on Home Page

The goal is to ensure clicks on the Library Services cards (Opening Hours, Ask a Librarian, Book a Study Room) reliably navigate to their respective pages (/opening-hours/, /ask-librarian/, /book-study-room/) without interference from JS or CSS. Current issues: Clicks not registering, likely due to event propagation or ripple effects in motion-effects.js.

## Steps:

- [x] Step 1: Read and verify templates/home.html - Confirmed <a> tags wrap entire cards with `display: block;`, `text-decoration: none;`, `color: inherit;`, `cursor: pointer;`, and `pointer-events: none;` on child divs (resource-icon, resource-text) to allow bubbling. The structure is correct for native navigation.

- [x] Step 2: Read static/js/motion-effects.js - Confirmed .resource-card is excluded from ripple effects (selector '.card:not(.resource-card)'). Cursor tracking applies to 'a' and '.card', but does not block clicks. No other listeners affect .resource-card. No edits needed.

- [ ] Step 3: Launch browser to http://127.0.0.1:8000/, scroll down to Library Services section, and test click on Opening Hours card (coordinates approx. 200, 250) to see if it navigates.

- [ ] Step 4: If click fails, edit static/js/motion-effects.js to disable all interactions on .resource-card (e.g., add condition to skip if target.closest('.resource-card')).

- [ ] Step 5: Re-test in browser: Scroll, click all three cards, confirm navigation to detail pages (200 OK, content loads).

- [ ] Step 6: Test edge cases: Click on icon/text specifically, keyboard navigation (tab to card, enter), mobile view (resize browser).

- [ ] Step 7: Verify backend: Direct curl to endpoints (e.g., curl http://127.0.0.1:8000/opening-hours/) for 200 OK.

- [ ] Step 8: Update this TODO.md with [x] for completed steps and remove unnecessary ones.

Proceeding with Step 1 now.
