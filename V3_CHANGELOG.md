# Portfolio V3 — fixes and enhancements

## Visual redesign
- Rebuilt hero for a more recruiter-oriented presentation emphasizing **Harshad Madhav Dhuppe**, the 2027 degree, Python/backend expertise and clear project links.
- Added a Marathi name treatment **हर्षद माधव धुप्पे**, inspired by your yellow-on-indigo lettering reference. It uses *Tiro Devanagari Marathi* loaded at runtime, with a local Devanagari fallback, decorated with a custom flourish.
- Included a carefully cropped portrait from your previously supplied screenshot, with a CMS-replaceable image field. Included the college logo too.
- Polished the navigation, buttons, project cards, skills, certificates and contact/footers, using typography, restrained shadows, 2D effects and responsive layout.

## Functional fixes
- **Project search and category filtering** work together, with live counts and no-result states.
- Engineering notes have collapsible details. Real demo links display only when an HTTPS/HTTP URL is provided.
- Fixed the copy-email action to work gracefully when the clipboard API is unavailable.
- The mobile menu is visible, opens/closes properly, and closes on Escape; a back-to-top control appears after scrolling.
- Fixed sideways overflow on large desktop, tablet and narrow-phone viewports.
- Improved certificate image display, resume download entries, missing-photo fallbacks, and missing-data feedback.
- Updated dynamic SEO and added build-time SEO metadata, `robots.txt`, `sitemap.xml` and Person structured data.

## GitHub Pages + CMS
- Fixed Pages CMS collection list configuration to match the current `view.sort` and `view.default` schema.
- Separated upload folders for image and document assets, while continuing to support old existing asset URLs.
- Added a test step before automatic GitHub Pages deployment.
- Strengthened local asset path validation, support for Unicode filenames, and public-versus-hidden entries.
- Added `UPDATE_EXISTING_SITE.bat` for owners with an existing portfolio repo: it backs up Git history and **does not overwrite existing CMS content or uploaded files**.

## Not claimed
- The site was built and browser-tested locally. A real GitHub sign-in on the hosted Pages CMS and a real production deployment need to be completed by the GitHub account owner.
- The HTML design is not pixel-identical to the uploaded Marathi example: that image contains a different word. The site uses real Marathi text in a traditional artistic typeface so the name remains editable and accessible.
- No fake work experience, performance metrics, certificates, or deployment links have been added.

## Final release verification
- Kept `content/certificates/` and `content/resumes/` in Git with `.gitkeep`, so first-time deployments still expose empty CMS collections.
- Safe updater initializes any missing CMS collection/media directories without touching existing JSON entries or uploads.
- Expanded the dependency-free static build regression suite to 4 tests covering published/hidden content, Unicode media names, unsafe paths, duplicate project IDs and required assets.
- Checked `assets/site.js` with Node.js syntax validation.
