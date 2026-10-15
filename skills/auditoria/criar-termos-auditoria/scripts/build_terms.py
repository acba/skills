#!/usr/bin/env python3
"""Validate audit terms and render their Markdown, canvas and meeting draft."""
import argparse, html, re, sys, base64
from pathlib import Path
from PIL import ImageFont
import yaml, cairosvg
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

TITLES=["Objeto","Critérios","Evidências","Problema de Auditoria","Riscos da Fiscalização","Stakeholders","Nível de Asseguração","Objetivo","Não Escopo","Escopo","Entregas","Datas e Ausências"]
COLORS=['#ef4444','#ef4444','#ef4444','#f97316','#f97316','#f97316','#3b82f6','#10b981','#10b981','#10b981','#3b82f6','#3b82f6']
W=3200; CW=990; GAP=28; X=[60,1105,2150]; PAD=28
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(size,bold=False):
    p=FONTB if bold else FONT
    if not Path(p).exists():
        return ImageFont.load_default()
    return ImageFont.truetype(p,size)
def width(t,size,bold=False):
    f=font(size,bold)
    return f.getlength(t)
def lines(t,limit,size,bold=False):
    words=t.split()
    out=[]; row=''
    for word in words:
        nxt=(row+' '+word).strip()
        if row and width(nxt,size,bold)>limit:
            out.append(row);row=word
        else:row=nxt
        if width(row,size,bold)>limit:
            chars=''; fragments=[]
            for char in row:
                if chars and width(chars+char,size,bold)>limit:
                    fragments.append(chars);chars=char
                else:chars+=char
            out.extend(fragments);row=chars
    if row:out.append(row)
    return out
def esc(t):return html.escape(str(t),quote=True)
def parse(path):
    s=Path(path).read_text(encoding='utf-8-sig')
    meta={}
    if s.startswith('---\n'):
        a,sep,b=s[4:].partition('\n---')
        if not sep:raise ValueError('Frontmatter YAML não fechado.')
        meta=yaml.safe_load(a) or {}
        if not isinstance(meta,dict):raise ValueError('Frontmatter YAML deve ser um mapa de campos.')
        s=b.lstrip('\n')
    sections={}
    current=None; order=[]
    for ln in s.splitlines():
        if ln.startswith('## ') and not re.match(r'^##\s*\d{1,2}\s*[.:\-–]\s*',ln):
            raise ValueError(f'Seção sem número canônico: {ln}')
        m=re.match(r'^##\s*(\d{1,2})\s*[.:\-–]\s*(.*?)\s*$',ln)
        if m:
            current=int(m.group(1))
            if current not in range(1,13):raise ValueError(f'Número de seção inválido: {current}')
            if m.group(2).casefold()!=TITLES[current-1].casefold():
                raise ValueError(f'Seção {current}: título esperado "{TITLES[current-1]}".')
            if current in sections:raise ValueError(f'Seção duplicada: {current}')
            sections[current]=[];order.append(current)
        elif current and ln.strip()!='---':
            sections[current].append(ln)
    if order!=sorted(order):raise ValueError('Seções fora da ordem canônica de 1 a 12.')
    return meta,sections
def validate(meta,sections):
    errs=[]
    for n in range(1,13):
        if n not in sections:errs.append(f'Seção {n} ausente: {TITLES[n-1]}')
        elif not ''.join(sections[n]).strip():errs.append(f'Seção {n} vazia')
    for k in ('fiscalizacao','processo_paag','objetivo_auditoria'):
        if not meta.get(k):errs.append(f'Metadado de cabeçalho ausente: {k}')
        elif not isinstance(meta[k],str):errs.append(f'Metadado {k} deve ser texto entre aspas.')
    for k in ('participantes','decisoes_reuniao'):
        if k in meta and (not isinstance(meta[k],list) or any(not isinstance(v,str) for v in meta[k])):
            errs.append(f'Metadado {k} deve ser uma lista de textos.')
    return errs
def blocks(raw):
    out=[]; paragraph=[]
    def flush():
        if paragraph:
            out.append(('p',' '.join(paragraph)));paragraph.clear()
    for l in raw+['']:
        s=l.strip()
        if not s:flush();continue
        if s.startswith('### '):flush();out.append(('sub',s[4:].strip()));continue
        if re.match(r'^[-*]\s+',s):flush();out.append(('bullet',re.sub(r'^[-*]\s+','',s)));continue
        if re.match(r'^\d+[.)]\s+',s):flush();out.append(('bullet',s));continue
        if s.startswith('|'):
            flush()
            if not re.match(r'^\|[\s:|\-]+\|?$',s):
                out.append(('bullet',s.strip('| ').replace('|','  ·  ')))
            continue
        paragraph.append(s)
    return out
def layout_blocks(items,x,y,w,accent):
    out=[];cur=y
    for kind,t in items:
        if kind=='sub':
            fs=17;lh=27; ls=lines(t,w-30,fs,True);h=20+len(ls)*lh
            out.append(f'<rect x="{x}" y="{cur}" width="{w}" height="{h}" rx="10" fill="#eef4fa"/>')
            xx=x+15; yy=cur+31; col=accent;bold=True;just=False
        else:
            fs=17 if kind=='p' else 16;lh=29 if kind=='p' else 27
            lead='• ' if kind=='bullet' else ''
            ls=lines(t,w-(20 if lead else 0),fs)
            h=len(ls)*lh+12
            xx=x+(15 if lead else 0);yy=cur+fs+5;col='#24364c';bold=False;just=kind=='p'
        for i,ln in enumerate(ls):
            lead='• ' if kind=='bullet' and i==0 else ''
            attrs=''
            # Native SVG justification via spacing only, not glyph stretching.
            if just and i<len(ls)-1 and len(ln.split())>1:
                extra=w-width(ln,fs)
                spaces=ln.count(' ')
                if extra>0 and spaces:attrs=f' word-spacing="{extra/spaces:.3f}"'
            out.append(f'<text x="{xx}" y="{yy+i*lh}" font-size="{fs}" font-weight="{700 if bold else 400}" fill="{col}"{attrs}>{esc(lead+ln)}</text>')
        cur+=h+10
    return out,cur
def render(meta,sections,logo_path=None):
    bodies={};height={}
    for n in range(1,13):
        items=blocks(sections[n]);body,end=layout_blocks(items,0,0,CW-2*PAD,COLORS[n-1])
        bodies[n]=items;height[n]=max(240,end+112)
    objective=str(meta.get('objetivo_auditoria',''))
    objective_lines=lines('OBJETIVO: '+objective,1450,16)
    header_h=max(200,150+23*len(objective_lines))
    top=35+header_h+30; row1=max(height[n] for n in (1,2,3))
    mid=top+row1+28; row2=max(height[n] for n in (4,5,8))
    low=mid+row2+28
    positions={}
    for n,x in [(1,X[0]),(2,X[1]),(3,X[2])]:positions[n]=(x,top,height[n])
    for n,x in [(4,X[0]),(5,X[1]),(8,X[2])]:positions[n]=(x,mid,height[n])
    columns=[([6,9,10],X[0]),([7,11],X[1]),([12],X[2])]
    bottoms=[]
    for ns,x in columns:
        yy=low
        for n in ns:positions[n]=(x,yy,height[n]);yy+=height[n]+28
        bottoms.append(yy-28)
    bottom=max(bottoms)
    for ns,x in columns:
        n=ns[-1];xx,yy,hh=positions[n];positions[n]=(xx,yy,hh+bottom-(yy+hh))
    H=int(bottom+65)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
      '<rect width="100%" height="100%" fill="#f3f5f7"/>',
      f'<rect x="60" y="35" width="3080" height="{header_h}" rx="18" fill="white" stroke="#dfe6ee"/>',
      '<style>text { font-family: "DejaVu Sans", sans-serif; }</style>']
    if logo_path:
        data=base64.b64encode(Path(logo_path).read_bytes()).decode()
        parts.append(f'<image x="85" y="65" width="365" height="135" href="data:image/png;base64,{data}"/>')
    left_x=500 if logo_path else 95
    parts += [
      f'<text x="{left_x}" y="83" font-size="20" font-weight="700" fill="#17253c">{esc(meta.get("orgao",""))}</text>',
      f'<text x="{left_x}" y="115" font-size="17" fill="#334155">{esc(meta.get("secretaria",""))}</text>',
      f'<text x="{left_x}" y="146" font-size="16" fill="#0369a1">{esc(meta.get("unidade",""))}</text>',
      f'<line x1="1550" y1="60" x2="1550" y2="{35+header_h-25}" stroke="#dbe3eb"/>',
      '<text x="1600" y="78" font-size="22" font-weight="700" fill="#17253c">TERMOS DE AUDITORIA (CANVAS ESTRATÉGICO)</text>',
      f'<text x="1600" y="111" font-size="18" fill="#334155">FISCALIZAÇÃO: {esc(meta.get("fiscalizacao",""))} | Processo PAAG: {esc(meta.get("processo_paag",""))}</text>',
      f'<text x="1600" y="141" font-size="17" fill="#334155">JURISDICIONADOS: {esc(meta.get("jurisdicionados",""))}</text>']
    for i,ln in enumerate(objective_lines):
        parts.append(f'<text x="1600" y="{170+i*23}" font-size="16" fill="#334155">{esc(ln)}</text>')
    for n in range(1,13):
        x,y,h=positions[n];c=COLORS[n-1]
        parts += [f'<g id="card-{n}">',
          f'<rect x="{x}" y="{y}" width="{CW}" height="{h}" rx="18" fill="#fff" stroke="#dbe2ea"/>',
          f'<rect x="{x}" y="{y+4}" width="7" height="{h-8}" rx="3" fill="{c}"/>',
          f'<circle cx="{x+43}" cy="{y+43}" r="17" fill="#f2f5f9"/>',
          f'<text x="{x+43}" y="{y+50}" text-anchor="middle" font-size="17" font-weight="700" fill="{c}">{n}</text>',
          f'<text x="{x+75}" y="{y+51}" font-size="24" font-weight="700" fill="#13243d">{n}. {esc(TITLES[n-1])}</text>',
          f'<line x1="{x+26}" y1="{y+76}" x2="{x+CW-26}" y2="{y+76}" stroke="#e5eaf0"/>']
        content,end=layout_blocks(bodies[n],x+PAD,y+100,CW-2*PAD,c)
        if end>y+h-4:raise ValueError(f'Conteúdo excede cartão {n}: {end-y:.0f} > {h}')
        parts.extend(content);parts.append('</g>')
    parts.append('</svg>')
    return '\n'.join(parts)
def ata(meta,sections,dest):
    doc=Document();sec=doc.sections[0];sec.top_margin=Cm(2.1);sec.bottom_margin=Cm(2.1)
    normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(10)
    title=doc.add_heading('MINUTA DE ATA DE REUNIÃO – TERMOS DE AUDITORIA',0);title.alignment=WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Fiscalização: {meta.get('fiscalizacao','[não informado]')} | Processo PAAG: {meta.get('processo_paag','[não informado]')}")
    doc.add_paragraph(f"Data: {meta.get('data_reuniao') or '[a preencher]'} | Horário: {meta.get('horario_reuniao') or '[a preencher]'} | Local: {meta.get('local_reuniao') or '[a preencher]'}")
    doc.add_heading('Participantes',1)
    participants=meta.get('participantes') or []
    doc.add_paragraph('; '.join(participants) if participants else '[Informar participantes efetivos da reunião.]')
    doc.add_heading('Pauta e discussão dos termos',1)
    doc.add_paragraph('Pauta proposta com base nos Termos de Auditoria. A discussão efetiva de cada item deve ser confirmada por registro da reunião.')
    for n in range(1,13):
        doc.add_heading(f'{n}. {TITLES[n-1]}',2)
        for kind,t in blocks(sections[n]):
            if kind=='sub':doc.add_heading(t,3)
            else:doc.add_paragraph(t,style='List Bullet' if kind=='bullet' else None)
    doc.add_heading('Deliberações e encaminhamentos',1)
    decisions=meta.get('decisoes_reuniao') or []
    if decisions:
        for d in decisions:doc.add_paragraph(str(d),style='List Number')
    else:doc.add_paragraph('[PENDENTE: registrar decisões reais da equipe, responsáveis, prazos e eventuais divergências. Não presumir aprovação ou consenso.]')
    doc.add_heading('Assinaturas',1)
    for p in participants:doc.add_paragraph(str(p)+' — ______________________________')
    if not participants:doc.add_paragraph('[Assinaturas a colher]')
    doc.save(dest)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input');ap.add_argument('--output-dir',default='.')
    ap.add_argument('--validate-only',action='store_true')
    ap.add_argument('--logo',help='Arquivo PNG da instituição; omitido por padrão')
    args=ap.parse_args()
    try:meta,sections=parse(args.input)
    except (ValueError,yaml.YAMLError) as exc:
        ap.error(str(exc))
    errs=validate(meta,sections)
    if errs:
        for e in errs:print('ERRO:',e,file=sys.stderr)
        sys.exit(1)
    print('Validação: 12 seções presentes e cabeçalho mínimo completo.')
    if args.validate_only:return
    if args.logo and not Path(args.logo).is_file():ap.error('Logo PNG não encontrado.')
    if args.logo and Path(args.logo).suffix.lower()!='.png':ap.error('O logo deve ser PNG.')
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    source=Path(args.input).read_text(encoding='utf-8-sig')
    (out/'Termos de Auditoria.md').write_text(source,encoding='utf-8')
    svg=render(meta,sections,args.logo)
    (out/'Termos de auditoria.svg').write_text(svg,encoding='utf-8')
    cairosvg.svg2png(bytestring=svg.encode('utf-8'),write_to=str(out/'Termos de auditoria.png'),output_width=3200)
    ata(meta,sections,out/'Ata de Reunião.docx')
    print('Arquivos gerados em:',out)
if __name__=='__main__':main()
