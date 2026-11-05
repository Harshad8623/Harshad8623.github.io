# Deployment — GitHub Pages & Visual GitHub Admin

Your website can be served at **https://harshad8623.github.io/** after the GitHub repository and GitHub Pages deployment succeed. It remains free within GitHub Pages' plan limits; a separate backend is not required.

## Option A: First time deploying

1. Extract `Harshad_Premium_Portfolio_V3_GitHub_Pages.zip`.
2. Double-click `PUBLISH_WINDOWS.bat`, which confirms the account, creates the **public** `Harshad8623.github.io` repository and pushes these files. Or create that repository and upload all project files yourself.
3. On GitHub, open **Settings → Pages → Build and deployment → GitHub Actions**.
4. Open **Actions → Publish Portfolio to GitHub Pages**. A successful run publishes `dist/` to Pages.
5. Visit https://harshad8623.github.io/ and test on mobile. GitHub Pages may take a moment after the build to serve the latest version.

## Option B: Upgrading an existing GitHub Pages portfolio (recommended if already deployed)

1. Extract V3 into a **different folder**. Keep your previous project and CMS content.
2. Install [Git](https://git-scm.com/) and [GitHub CLI](https://cli.github.com/) if necessary. Run `gh auth login` to sign into your own `Harshad8623` account.
3. Double-click **`UPDATE_EXISTING_SITE.bat`**.
4. The updater verifies the account, creates a full mirrored Git backup in **Documents/HarshadPortfolioBackups**, clones the live repository, replaces only the layout/build/CMS code, and keeps your existing `content` and `assets/uploads` files. It runs build tests, prints changed files, and requests the literal confirmation `UPDATE` before pushing.
5. Review the new deployment in Actions. If you customized your old site, your existing texts remain; edit them through Pages CMS to take advantage of the new design.

**Important:** GitHub Pages is public. Do not upload private `.env` files, API keys, ID documents, private photos, or other sensitive records. Published resumes and certificates become public files and can remain in Git history.

## Visual Admin Dashboard

1. Visit https://app.pagescms.org/ and choose **Sign in with GitHub**.
2. Authorize only your portfolio repository if possible.
3. Open the `Harshad8623.github.io` repository and branch `main`.
4. Edit **Profile, skills & SEO**, **Projects**, **Certificates** and **Resumes** using the CMS forms.
5. Upload media in the appropriate picker; clicking **Save** commits to GitHub. GitHub Actions rebuilds the website from JSON and uploaded files.

The footer's **Manage site (GitHub login)** link opens the hosted CMS. This is not a four-digit-PIN admin on the public website. GitHub login and 2FA protect changes.

## Locally test without running a backend

From the extracted folder:

```bash
python scripts/test_build.py
python scripts/build.py
python -m http.server 8000 --directory dist
```

Then open http://127.0.0.1:8000/ . Do not double-click `index.html` directly: it fetches `site-data.json` and browsers block that on `file://`.

## Adding resume and certificates

Use **Pages CMS → Resumes / CVs** to upload a PDF/DOCX to the document media folder. Set `Visible to recruiters` only when ready. Under **Certificates & achievements**, create an entry, upload an image or PDF, set published true, and save.

If you are upgrading from the FastAPI SQLite version, follow `README.md` for optional data migration. The old backend is not deployed to GitHub Pages.

## Common problems

- **Blank cards or “Portfolio data could not load”**: use the local preview server and verify GitHub Actions runs successfully.
- **Image missing**: make sure the image exists under `assets/`, the path matches the saved JSON, and the CMS media entry is published.
- **Resume missing**: verify the PDF/DOCX was uploaded and the resume record has `published: true`.
- **Changes not visible**: GitHub Actions might still be building; hard refresh after the deploy succeeds.
- **Pages CMS cannot edit**: check installed GitHub App repository access and make sure `.pages.yml` is on the `main` branch.
- **Old custom content not present**: use `UPDATE_EXISTING_SITE.bat` instead of replacing the entire repo with the fresh ZIP.

**GitHub Docs:** https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
**Pages CMS Docs:** https://pagescms.org/docs/quick-start/
