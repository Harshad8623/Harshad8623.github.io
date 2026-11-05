# Harshad Madhav Dhuppe — Premium Developer Portfolio

**Static GitHub Pages edition · GitHub-login visual editing via Pages CMS · No backend required**

The site preserves the lime/forest visual design from Portfolio V2, with English + Marathi name, flagship projects, skills, college logo, biography, contact links, certificates, and downloadable resumes. The bottom-footer **Admin login** opens [Pages CMS](https://app.pagescms.org/) where you authenticate through GitHub and edit website files visually.

## One-time deployment (free GitHub Pages)

1. On GitHub, create a **PUBLIC** repository named exactly **`Harshad8623.github.io`** on your `Harshad8623` account. Initialize it with no files; use `main` as the branch.
2. Extract this ZIP. Upload **all files and folders** in its root to the new GitHub repository. Include hidden `.pages.yml`, `.github/workflows/pages.yml`, and `assets`.
3. In the repository, go to **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Wait until **Actions → Publish Portfolio to GitHub Pages** succeeds. Visit **https://harshad8623.github.io/**. It is not live until you create and publish the repository.
5. Go to **https://app.pagescms.org/** → **Sign in with GitHub**. Approve installing the GitHub App for the new portfolio repository (choose **Only select repositories** for least privilege). Select `Harshad8623.github.io` and branch `main`.
6. You will see editor sections **Profile, skills & SEO**, **Projects & live links**, **Certificates & achievements**, and **Resumes / CVs**. Edit, upload, and **Save**; Pages CMS commits changes to GitHub and the Pages workflow redeploys.

The public website has **no PIN login** and **no publicly exposed GitHub token**. Your admin link directs you to the hosted editor (a different, trusted domain), not a login form on GitHub Pages.

## Add a new resume through Admin

1. Footer → **Admin login** → GitHub login → open portfolio repository.
2. **Resumes / CVs** → create an entry such as `Python Developer Resume`.
3. Select a PDF/DOCX with the media upload picker, set **Visible to recruiters**, and save.
4. Allow the GitHub Pages deployment to finish. The file appears in **Resume** with a download link.

Do not upload a resume you intend to keep private; published GitHub Pages content and its repository are public.

## Add project demos and certificates

- **Projects:** edit the item in the CMS. Enter the actual demo URL in `Live demo URL`; optionally attach a screenshot. You can add/reorder/hide projects.
- **Certificates:** create a certificate entry with issuer/date and optional credential URL or certificate PDF. Set `Show publicly` to true.
- **Photo:** Profile & SEO → Profile & introduction → Portrait photograph. Upload or replace.
- **Skills, CGPA, college, links, and Marathi name:** edit **Profile, skills & SEO**.

These fields are backed by JSON records under `content/`. Git tracks revisions automatically.

## Optional Windows one-click GitHub repository creation

If you already use GitHub CLI, double-click **`PUBLISH_WINDOWS.bat`** inside the extracted folder instead of manually uploading files. It verifies you're signed in as `Harshad8623`, asks before creating the public repository, and refuses to overwrite an existing portfolio repository. Afterwards you must still enable GitHub Actions in Settings → Pages and connect the Pages CMS GitHub App yourself.

## Local preview (Python only, no installation)

Run in this folder:

```bash
python scripts/build.py
python -m http.server 8000 --directory dist
```

Visit http://127.0.0.1:8000. Do **not** simply double-click `index.html` from your filesystem, because browsers may block JSON loading without a local web server.

## Upgrade from the older FastAPI + SQLite version

The old version's SQLite data **is not automatically synced** to GitHub Pages. If you customized that version, copy your old `app/data` folder somewhere safe, then run:

```bash
python scripts/import_from_v2.py "C:\\path\\to\\old\\Harshad_Premium_Portfolio_V2\\app\\data"
python scripts/import_from_v2.py "C:\\path\\to\\old\\Harshad_Premium_Portfolio_V2\\app\\data" --apply
python scripts/build.py
```

The first command is a preview. The second imports **only public** site content and published resumes/certificates; it does not import admin PINs, password hashes or sessions. Review all imported files before committing to a public repo. Do **not** upload `.env` or `portfolio.db` to GitHub.

## How editing works

`Pages CMS → GitHub commit → GitHub Actions build.py → GitHub Pages`.

Pages CMS edits these files:

- `content/site.json` — profile, skills, milestones, SEO
- `content/projects/*.json` — each project and its live/demo links
- `content/certificates/*.json` — each published credential
- `content/resumes/*.json` — each resume entry
- `assets/uploads/*` — uploaded photos and documents

`.pages.yml` describes the visual editor; `scripts/build.py` collects content and copies static assets to `dist/`. The workflow publishes `dist/`.

## Limitations and security

- GitHub Pages only supports static hosting; FastAPI, local PIN entry and SQLite edits are **not used** in this version.
- Anyone can see public repo files and published resumes/certificates, including their history. Never upload credentials, IDs, private docs, or old SQLite databases.
- GitHub authentication and permissions are managed by **Pages CMS / GitHub**; no self-hosted OAuth service is necessary for this hosted setup.
- Pages CMS is free and open-source according to its current site; long-term third-party hosting policies can change.
- GitHub Pages updates occur **after a successful build/deploy**, not necessarily immediately when you hit Save.
- If deploying under another repository name, the default paths and CMS media paths assume the root `Harshad8623.github.io` user-site URL. Adjust them before publishing to a `/repo/` path.
- This package contains only the original seeded public content. Your real resumes/certificates need to be added, or migrated from V2.
- No assertion that every linked demo is online or every skill is independently verified.

**Original design basis:** the Portfolio V2 lime/forest website, with its static UI preserved, project content retained, and college logo included.

## V3 release checks

```bash
python scripts/test_build.py
python scripts/build.py
```

The 4 static regression tests check CMS publication filtering, Unicode filenames, unsafe asset paths, duplicate project identifiers and required source files. JavaScript syntax can also be checked locally using `node --check assets/site.js`. Screenshot/browser tests were performed for the V3 layouts previously, but live Pages CMS authentication and a production deployment still require your GitHub authorization.

**First-time CMS collections:** Empty `content/resumes` and `content/certificates` directories include `.gitkeep` files so they exist immediately after cloning. You can add your first entries visually in Pages CMS.
