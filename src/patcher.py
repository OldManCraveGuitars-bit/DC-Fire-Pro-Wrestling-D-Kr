"""Fire Pro Wrestling D Korean v0.901 standalone, verified CHD/GDI patcher."""
from __future__ import annotations
import argparse,hashlib,json,os,queue,shlex,shutil,subprocess,sys,tempfile,threading
from pathlib import Path

VERSION='0.901'
TITLE='파이어 프로 레슬링 D 한글 패처 v0.901'

def resources():
    if getattr(sys,'frozen',False):return Path(sys._MEIPASS)/'payload'
    base=Path(__file__).resolve().parents[1]
    return base/'payload'if(base/'payload/manifest.json').is_file()else base/'release/v0.901/payload'

def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def checked(path,record,label):
    path=Path(path)
    if not path.is_file()or path.stat().st_size!=record['size']:raise ValueError(label+'의 파일 크기가 다릅니다.')
    if sha(path)!=record['sha256']:raise ValueError(label+'의 SHA-256이 다릅니다. 패치 전 일본판 원본을 확인하세요.')

def get_manifest():return json.loads((resources()/'manifest.json').read_text('utf-8'))

def verify_payload():
    m=get_manifest()
    if m['version']!=VERSION or len(m['tracks'])!=50:raise ValueError('내장 패치 정보의 버전/트랙 수가 다릅니다.')
    for record in m['tools'].values():checked(resources()/record['file'],record,'내장 실행 도구')
    for record in m['patches'].values():checked(resources()/record['file'],record,'내장 차이 패치')
    for n,t in enumerate(m['tracks'],1):
        if t['number']!=n or Path(t['output_file']).name!=t['output_file']:raise ValueError('잘못된 트랙 정보입니다.')
    return m

def read_gdi(path,m):
    lines=Path(path).read_text('utf-8-sig').splitlines()
    if not lines or lines[0].strip()!='50':raise ValueError('일본판 원본 50트랙 GDI를 선택하세요.')
    rows=[]
    for line in lines[1:]:
        if not line.strip():continue
        parts=shlex.split(line)
        if len(parts)!=6:raise ValueError('GDI 트랙 정보가 올바르지 않습니다.')
        name=parts[4]
        if Path(name).name!=name or '/'in name or '\\'in name:raise ValueError('GDI와 같은 폴더의 트랙 파일만 지원합니다.')
        track=(Path(path).parent/name).resolve(strict=True)
        if track.parent!=Path(path).parent.resolve():raise ValueError('GDI 폴더 밖의 트랙 경로입니다.')
        rows.append(dict(number=int(parts[0]),lba=int(parts[1]),kind=int(parts[2]),stride=int(parts[3]),offset=int(parts[5]),path=track))
    if len(rows)!=50:raise ValueError('GDI 트랙이 50개가 아닙니다.')
    for row,expected in zip(rows,m['tracks']):
        if any(row[k]!=expected[k]for k in ('number','lba','kind','stride','offset')):raise ValueError('원본 GDI의 트랙 구성이 다릅니다.')
    return rows

def run_tool(tool,args,cwd):
    result=subprocess.run([str(tool),*map(str,args)],cwd=cwd,capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:raise RuntimeError('디스크 처리 도구 오류:\n'+(result.stdout+result.stderr).decode('utf-8','replace')[-1800:])

def apply(source,output,notify=lambda text:None):
    source=Path(source).expanduser().resolve(strict=True);output=Path(output).expanduser().resolve()
    if source.suffix.lower()not in ('.chd','.gdi'):raise ValueError('원본 CHD 또는 GDI를 선택하세요.')
    if output.exists()or output==source:raise ValueError('이미 있는 파일/폴더에는 덮어쓰지 않습니다. 새 출력 폴더를 지정하세요.')
    m=verify_payload();notify('원본 확인 중…')
    source_sha=sha(source)
    if source.suffix.lower()=='.chd':checked(source,m['source_chd'],'일본판 원본 CHD')
    else:read_gdi(source,m)
    output.parent.mkdir(parents=True,exist_ok=True)
    needed=sum(t['source']['size']+t['target']['size']for t in m['tracks'])+m['source_chd']['size']+256*1024*1024
    if shutil.disk_usage(output.parent).free<needed:raise ValueError('출력 드라이브의 여유 공간이 부족합니다. 약 5GB 이상 확보하세요.')
    with tempfile.TemporaryDirectory(prefix='.fpdkr-v09-',dir=output.parent)as temp:
        work=Path(temp).resolve();assert work.parent==output.parent.resolve()
        result=work/'result';result.mkdir()
        if source.suffix.lower()=='.chd':
            notify('CHD에서 원본 50트랙 추출 중…')
            shutil.copyfile(source,work/'input.chd')
            run_tool(resources()/m['tools']['chdman']['file'],['extractcd','-i','input.chd','-o','source.gdi'],work)
            tracks=read_gdi(work/'source.gdi',m)
            (work/'input.chd').unlink()
        else:tracks=read_gdi(source,m)
        notify('원본 50트랙의 SHA-256 확인 중…')
        for row,t in zip(tracks,m['tracks']):checked(row['path'],t['source'],f"원본 트랙 {t['number']:02d}")
        for row,t in zip(tracks,m['tracks']):
            n=t['number'];notify(f'트랙 {n:02d}/50 적용 및 검증 중…')
            target=result/t['output_file'];patch=m['patches'].get(str(n))
            if patch:
                # Use ASCII relative tool paths even inside a Korean output folder.
                raw=work/'original-track.bin';delta=work/'track.xdelta'
                shutil.copyfile(row['path'],raw);shutil.copyfile(resources()/patch['file'],delta)
                run_tool(resources()/m['tools']['xdelta']['file'],['-d','-s',raw.name,delta.name,'result/'+t['output_file']],work)
                raw.unlink();delta.unlink()
            else:shutil.copyfile(row['path'],target)
            checked(target,t['target'],f'결과 트랙 {n:02d}')
        gdi=result/m['target_gdi']['file'];gdi.write_text(m['target_gdi']['text'],encoding='ascii',newline='')
        checked(gdi,m['target_gdi'],'결과 GDI')
        if sha(source)!=source_sha:raise RuntimeError('작업 도중 원본이 변경되었습니다.')
        report=dict(success=True,version=VERSION,source_sha256=source_sha,tracks_verified=50,audio_tracks_preserved=47,
                    output_gdi=m['target_gdi']['file'],output_gdi_sha256=m['target_gdi']['sha256'],
                    output_tracks=[dict(file=t['output_file'],**t['target'])for t in m['tracks']])
        (result/'PATCH-REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        # The user selected a new directory; no existing directory is moved/deleted.
        if output.exists():raise ValueError('작업 도중 출력 폴더가 생겼습니다. 다른 폴더 이름을 지정하세요.')
        assert result.resolve().parent==work and output.parent.resolve()==work.parent
        result.rename(output)
    notify('완료: GDI와 트랙 50개를 함께 사용하세요.')
    return report

class App:
    def __init__(self,root):
        import tkinter as tk
        from tkinter import ttk,filedialog,messagebox
        self.root=root;self.busy=False;self.events=queue.Queue();root.title(TITLE);root.geometry('840x600');root.minsize(780,540)
        self.source=tk.StringVar();self.output=tk.StringVar();frame=ttk.Frame(root,padding=20);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text=TITLE,font=('Malgun Gothic',18,'bold')).pack(anchor='w')
        ttk.Label(frame,text='일본판 원본 CHD 또는 50트랙 GDI를 선택하세요.\n한글화·실제 링네임·해금·다운로드 기술 100개·추가 선수 46명을 적용합니다.',wraplength=780).pack(anchor='w',pady=(10,20))
        self.entries=[]
        for label,var,original in [('원본 CHD / GDI',self.source,True),('새 출력 폴더',self.output,False)]:
            row=ttk.Frame(frame);row.pack(fill='x',pady=8);ttk.Label(row,text=label,width=18).pack(side='left')
            entry=ttk.Entry(row,textvariable=var);entry.pack(side='left',fill='x',expand=True);self.entries.append(entry)
            def choose(v=var,is_source=original):
                if self.busy:return
                if is_source:
                    p=filedialog.askopenfilename(filetypes=[('Dreamcast CHD/GDI','*.chd *.gdi')])
                    if p:v.set(p);self.output.set(str(Path(p).parent/'FireProD-KR-v0.901'))
                else:
                    p=filedialog.askdirectory(title='새 결과 폴더를 만들 상위 폴더 선택')
                    if p:v.set(str(Path(p)/'FireProD-KR-v0.901'))
            ttk.Button(row,text='찾기',command=choose).pack(side='right',padx=(8,0))
        ttk.Label(frame,text='결과는 새 폴더의 GDI + 트랙 50개입니다. 여유 공간 약 5GB가 필요합니다.',wraplength=780).pack(anchor='w',pady=10)
        self.button=ttk.Button(frame,text='v0.901 한글 패치 적용',command=self.start);self.button.pack(anchor='w',pady=6)
        self.bar=ttk.Progressbar(frame,mode='indeterminate');self.bar.pack(fill='x',pady=6)
        self.log=tk.Text(frame,height=12,wrap='word',font=('Malgun Gothic',10),state='disabled');self.log.pack(fill='both',expand=True)
        footer=ttk.Frame(frame);footer.pack(fill='x',pady=(10,0))
        ttk.Label(footer,text='한글화: 기타 깎는 노인 · v0.901 개발판',wraplength=620).pack(side='left')
        ttk.Button(footer,text='도움말 / 라이선스',command=self.licenses).pack(side='right')
        root.protocol('WM_DELETE_WINDOW',self.close);root.after(100,self.tick)
    def licenses(self):
        import tkinter as tk
        top=tk.Toplevel(self.root);top.title('도움말 / 라이선스');top.geometry('820x600')
        text=tk.Text(top,wrap='word',font=('Malgun Gothic',10));text.pack(fill='both',expand=True)
        for p in [resources()/'THIRD_PARTY_NOTICES.md',*sorted((resources()/'licenses').glob('*.txt'))]:
            text.insert('end',p.name+'\n\n'+p.read_text('utf-8')+'\n\n')
        text.configure(state='disabled')
    def start(self):
        from tkinter import messagebox
        if self.busy:return
        if not self.source.get().strip()or not self.output.get().strip():messagebox.showerror(TITLE,'원본과 새 출력 폴더를 지정하세요.');return
        self.busy=True;self.button.configure(state='disabled');self.bar.start()
        source,output=self.source.get(),self.output.get()
        def worker():
            try:apply(source,output,lambda t:self.events.put(('log',t)));self.events.put(('done','패치 완료. 결과 폴더의 GDI와 트랙 50개를 함께 사용하세요.'))
            except Exception as e:self.events.put(('error',str(e)))
        threading.Thread(target=worker,daemon=True).start()
    def tick(self):
        from tkinter import messagebox
        while not self.events.empty():
            kind,text=self.events.get();self.log.configure(state='normal');self.log.insert('end',text+'\n');self.log.see('end');self.log.configure(state='disabled')
            if kind in ('done','error'):
                self.busy=False;self.bar.stop();self.button.configure(state='normal')
                (messagebox.showinfo if kind=='done'else messagebox.showerror)(TITLE,text)
        self.root.after(100,self.tick)
    def close(self):
        from tkinter import messagebox
        if self.busy:messagebox.showinfo(TITLE,'작업이 끝난 뒤 닫아 주세요.');return
        self.root.destroy()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--report',type=Path);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if args.report and(args.report.exists()or any(args.report.resolve()==p.resolve()for p in (args.source,args.output)if p)):
        if sys.stderr:print('검증 보고서는 새 파일 경로로 지정하세요.',file=sys.stderr)
        return 1
    result=None
    try:
        if args.self_test:
            m=verify_payload();import tkinter as tk
            root=tk.Tk();root.withdraw();app=App(root);root.update();assert len(app.entries)==2;root.destroy()
            result=dict(success=True,version=VERSION,frozen=bool(getattr(sys,'frozen',False)),tracks=len(m['tracks']),payload_valid=True,gui_started=True)
        elif args.source or args.output:
            if not(args.source and args.output):raise ValueError('--source와 --output을 함께 지정하세요.')
            result=apply(args.source,args.output,lambda s:print(s,flush=True)if sys.stdout else None)
        else:
            import tkinter as tk
            root=tk.Tk();App(root);root.mainloop();return 0
    except Exception as e:result=dict(success=False,version=VERSION,error=str(e))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if sys.stdout:print(json.dumps(result,ensure_ascii=False))
    return 0 if result['success']else 1
if __name__=='__main__':raise SystemExit(main())
