#!/usr/bin/env python3
"""One-time importer of *public* content from old V2 local SQLite data.

Reads local disk only; does NOT import the admin password hash, sessions,
private/draft resume uploads, or secrets. Run from a clean working copy and
review all imported records before pushing them to a PUBLIC GitHub repository.
"""
import argparse, json, re, shutil, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def copy_image(from_file,basename):
    if not from_file.is_file():return ''
    data=from_file.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):extension='.png'
    elif data.startswith(b'\xff\xd8\xff'):extension='.jpg'
    elif data[:4]==b'RIFF' and data[8:12]==b'WEBP':extension='.webp'
    else:return ''
    dest=ROOT/'assets/uploads'/f'{basename}{extension}'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
    return '/assets/uploads/'+dest.name

def main():
    ap=argparse.ArgumentParser(description='Import public content from local Portfolio V2 SQLite data')
    ap.add_argument('data_dir',type=Path,help='Old Portfolio V2 app/data folder containing portfolio.db')
    ap.add_argument('--apply',action='store_true',help='Write converted data (without flag, preview only)')
    args=ap.parse_args()
    db_path=args.data_dir/'portfolio.db'
    if not db_path.is_file():raise SystemExit(f'Not found: {db_path}')
    c=sqlite3.connect(f'file:{db_path.resolve()}?mode=ro',uri=True)
    c.row_factory=sqlite3.Row
    with c:
        site=json.loads(c.execute("SELECT value FROM settings WHERE key='site'").fetchone()['value'])
        projects=site.pop('projects',[])
        site.pop('certificates',None)
        certificates=[dict(x) for x in c.execute('SELECT * FROM certificates WHERE published=1')]
        resumes=[dict(x) for x in c.execute('SELECT * FROM resumes WHERE published=1')]
        media_records={r['key']:r['value'] for r in c.execute("SELECT key,value FROM settings WHERE key='avatar_file' OR key='college_logo' OR key LIKE 'project-image:%'")}
    print('PREVIEW: profile:',site['profile'].get('name'),'projects:',len(projects),'published certificates:',len(certificates),'published resumes:',len(resumes))
    print('WARNING: Content and uploaded files may contain personal information. PUBLIC repository will expose them.')
    if not args.apply:
        print('No changes made. Review and rerun with --apply to import.');return
    if media_records.get('avatar_file'):
        site['profile']['avatar']=copy_image(args.data_dir/'media'/media_records['avatar_file'],'portrait')
    if media_records.get('college_logo'):
        # Replace the stock college logo only if the old version contains a valid custom image.
        site['profile']['collegeLogo']=copy_image(args.data_dir/'media'/media_records['college_logo'],'college-logo-custom')
    write_json(ROOT/'content/site.json',site)
    for i,p in enumerate(projects,1):
        pid=p.get('id','')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,79}',pid):continue
        rec=media_records.get('project-image:'+pid)
        if rec:p['image']=copy_image(args.data_dir/'media'/rec,'project-'+pid)
        p['order']=i*10;p['published']=True
        write_json(ROOT/'content/projects'/f'{pid}.json',p)
    for i,r in enumerate(resumes,1):
        stored=r.get('stored_name','')
        source=args.data_dir/'resumes'/Path(stored).name
        if not source.is_file() or not source.suffix.lower() in ('.pdf','.docx'):continue
        if source.suffix.lower()=='.pdf' and not source.read_bytes().startswith(b'%PDF-'):continue
        dest=ROOT/'assets/uploads'/('resume-'+re.sub('[^a-z0-9-]','-',r['id'].lower())+source.suffix.lower())
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        write_json(ROOT/'content/resumes'/f"resume-{r['id']}.json",{
            'label':r['label'],'role':r['role'],'file':'/assets/uploads/'+dest.name,'published':True,'order':i*10
        })
    for i,c in enumerate(certificates,1):
        fid=c.get('stored_name','')
        file=copy_image(args.data_dir/'media'/Path(fid).name,'certificate-'+c['id']) if fid and not fid.lower().endswith('.pdf') else ''
        if fid and fid.lower().endswith('.pdf'):
            src=args.data_dir/'media'/Path(fid).name
            if src.is_file() and src.read_bytes().startswith(b'%PDF-'):
                dest=ROOT/'assets/uploads'/('certificate-'+c['id']+'.pdf');shutil.copyfile(src,dest)
                file='/assets/uploads/'+dest.name
        write_json(ROOT/'content/certificates'/f"certificate-{c['id']}.json",{
            'title':c['title'],'issuer':c['issuer'],'issued':c['issued'],'description':c['description'],
            'url':c['url'],'file':file,'published':True,'order':i*10
        })
    print('Public content imported. Review new files and run: python scripts/build.py')

if __name__=='__main__':main()
