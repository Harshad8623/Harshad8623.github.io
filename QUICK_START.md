# Start here — Harshad Portfolio V3

## Is this your first GitHub Pages deployment?

1. Extract the ZIP into a new folder on Windows.
2. Install Git and GitHub CLI (`gh`). Sign into **Harshad8623** using `gh auth login`.
3. Double-click `PUBLISH_WINDOWS.bat`. Type `PUBLISH` when it asks to create the **public** `Harshad8623.github.io` repository. If Git requests your name/email, configure them and retry.
4. In the new repository, choose **Settings → Pages → Source: GitHub Actions**.
5. Open the Actions tab and check that **Publish Portfolio to GitHub Pages** succeeds.
6. Visit `https://harshad8623.github.io/`.
7. Open `https://app.pagescms.org/`, sign in with GitHub, and authorize **only** the portfolio repo. Open `Harshad8623.github.io` and edit the site visually.

## Updating a GitHub Pages portfolio you already published?

1. Keep a copy of your old project and CMS content.
2. Extract V3 to a new folder, then double-click **`UPDATE_EXISTING_SITE.bat`**.
3. The updater checks that you are signed into the correct account, clones a full Git-history backup in Documents, preserves your existing project records, resume/certificate records and media, and tests the build.
4. Review its proposed changes. Type `UPDATE` only if you want it to commit and push. Check the Actions run afterwards.

## Running it on your own computer

Double-click `START_LOCAL_PREVIEW.bat` or run:

```powershell
python scripts/test_build.py
python scripts/build.py
python -m http.server 8000 --directory dist
```

Then visit `http://127.0.0.1:8000/`.

## Add and manage your details

Use **Pages CMS** to update Profile & SEO, Projects & live links, Certificates and Resumes. The footer link takes you to the login page for this hosted editor. You do not need a four-digit PIN, FastAPI or SQLite for this static website.

**Security:** GitHub Pages repositories and deployed resumes/certificates are public. Setting a record to `published: false` hides it from the displayed website; it does **not** make uploaded files private or remove earlier Git commits. Never upload private credentials, student identification numbers, non-public documents or passwords.

## Status of this release

- Portfolio seed: **6 featured project cards, 4 skill sections, English + Marathi name, college emblem and local portrait**.
- Certificates: none seeded. Add only certificates you actually own.
- Resumes: none seeded. Upload the version you approve for recruiters.
- Local checks: static build and 4 regression tests pass; JS syntax check passes.
- Live GitHub authentication and production deployment are not tested, because they require your GitHub authorization.

If you are missing a section after a change, check the Actions run's Python build log, confirm the CMS edited files on the `main` branch, and hard-refresh the public site.
