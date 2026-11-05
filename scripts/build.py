#!/usr/bin/env python3
"""Compile public Pages CMS content into a static, GitHub Pages-compatible site.

No server credentials, admin tokens, private files, or Python runtime are published.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
BASE_URL = 'https://harshad8623.github.io'


def load(path: Path):
    with path.open(encoding='utf-8') as fp:
        return json.load(fp)


def order_key(item):
    value = item.get('order', 100)
    try:
        rank = float(value)
    except (TypeError, ValueError):
        rank = 100
    name = item.get('name') or item.get('title') or item.get('label') or ''
    return rank, str(name).casefold()


def collection(name: str):
    folder = ROOT / 'content' / name
    if not folder.is_dir():
        raise FileNotFoundError(f'Missing CMS collection folder: {folder}')
    entries = []
    for file_path in sorted(folder.glob('*.json')):
        item = load(file_path)
        if not isinstance(item, dict):
            raise ValueError(f'Expected a JSON object in {file_path}')
        if item.get('published', True) is False:
            continue
        entries.append(item)
    return sorted(entries, key=order_key)


def public_media(value):
    """Allow HTTPS links and existing assets in the repository; block traversals."""
    if not isinstance(value, str):
        return ''
    value = value.strip()
    if not value:
        return ''
    if value.startswith('https://'):
        u = urlparse(value)
        return value if u.hostname else ''
    if '\\' in value or '?' in value or '#' in value or '\x00' in value:
        return ''
    relative = PurePosixPath(value.lstrip('/'))
    if not relative.parts or relative.parts[0] != 'assets' or '..' in relative.parts:
        return ''
    target = ROOT.joinpath(*relative.parts).resolve()
    asset_dir = (ROOT / 'assets').resolve()
    if not target.is_relative_to(asset_dir) or not target.is_file():
        return ''
    return relative.as_posix()


def compile_site():
    site = load(ROOT / 'content/site.json')
    if not isinstance(site, dict) or not isinstance(site.get('profile'), dict):
        raise ValueError('content/site.json must have a profile object')
    profile = site['profile']
    for key in ('avatar', 'collegeLogo'):
        profile[key] = public_media(profile.get(key, ''))
    if not isinstance(profile.get('name'), str) or not profile['name'].strip():
        raise ValueError('Profile full name is required')
    # Pages CMS can omit optional fields when saving a profile edit.
    # Marathi branding is never allowed to break a valid site build.
    if not isinstance(profile.get('marathiName'), str) or not profile['marathiName'].strip():
        profile['marathiName'] = 'हर्षद माधव धुप्पे'

    projects = collection('projects')
    seen = set()
    for p in projects:
        slug = p.get('id') or ''
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,79}', slug):
            raise ValueError(f'Project ID must be a URL-safe slug: {slug!r}')
        if slug in seen:
            raise ValueError(f'Duplicate project ID: {slug}')
        seen.add(slug)
        p['image'] = public_media(p.get('image', ''))
    site['projects'] = projects

    certificates = collection('certificates')
    for c in certificates:
        c['file'] = public_media(c.get('file', ''))
        c['image'] = public_media(c.get('image', ''))
    resumes = collection('resumes')
    public_resumes = []
    for r in resumes:
        source = public_media(r.get('file', ''))
        if not source or not source.lower().endswith(('.pdf', '.docx')):
            continue
        r['file'] = source
        r['mime'] = 'PDF' if source.lower().endswith('.pdf') else 'DOCX'
        public_resumes.append(r)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(ROOT / 'assets', OUT / 'assets')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')

    # Static SEO metadata for crawlers that do not execute JavaScript.
    source_html = (ROOT / 'index.html').read_text(encoding='utf-8')
    seo = site.get('seo') or {}
    title = str(seo.get('title') or profile['name'] + ' | Software Developer')
    desc = str(seo.get('description') or profile.get('heroDescription') or '')
    source_html = re.sub(r'<title>.*?</title>', '<title>' + html.escape(title) + '</title>', source_html, count=1, flags=re.S)
    for token, key, value in [('name', 'description', desc), ('property', 'og:title', title), ('property', 'og:description', desc)]:
        pattern = r'(<meta\s+' + re.escape(token) + r'="' + re.escape(key) + r'"\s+content=")[^"]*(")'
        source_html = re.sub(pattern, lambda m: m.group(1) + html.escape(value, quote=True) + m.group(2), source_html, count=1)
    person = {
        '@context': 'https://schema.org', '@type': 'Person',
        'name': profile['name'], 'alternateName': profile['marathiName'],
        'description': desc, 'url': BASE_URL + '/',
        'alumniOf': {'@type': 'CollegeOrUniversity', 'name': profile.get('college', '')},
        'knowsAbout': ['Python', 'FastAPI', 'REST APIs', 'SQL', 'Software Engineering'],
        'sameAs': [v for v in (profile.get('github'), profile.get('linkedin')) if isinstance(v, str) and v.startswith('https://')],
    }
    structured = json.dumps(person, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    source_html = source_html.replace('</head>', '<script type="application/ld+json">' + structured + '</script>\n</head>', 1)
    (OUT / 'index.html').write_text(source_html, encoding='utf-8')
    (OUT / 'site-data.json').write_text(
        json.dumps({'site': site, 'certificates': certificates, 'resumes': public_resumes}, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8'
    )
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + BASE_URL + '/sitemap.xml\n', encoding='utf-8')
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + BASE_URL + '/</loc></url></urlset>\n', encoding='utf-8')
    print(f'Built {len(projects)} projects, {len(certificates)} certificates, {len(public_resumes)} resumes -> {OUT}')


if __name__ == '__main__':
    compile_site()
