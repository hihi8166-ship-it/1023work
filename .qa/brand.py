from pathlib import Path
import re
root=Path(__file__).resolve().parent.parent
suffix='<g fill="none" stroke="black" stroke-width="2.5"><path d="M128 3.5c-1.5-1.5-3.2-2.2-5.2-2.2-4.7 0-7.5 3.4-7.5 7.7s2.8 7.7 7.5 7.7c2 0 3.7-.7 5.2-2.2"/><ellipse cx="139.8" cy="9" rx="7" ry="7.7"/><path d="M152 17.7V1.3h5.8c3.5 0 5.2 1.6 5.2 4.4s-1.7 4.4-5.2 4.4H152M166 1l5 8.2L176 1M171 9.2v8.5"/></g>'
path=root/'assets/images/common/musinsa_logo_b.svg'
logo=path.read_text(encoding='utf-8')
if 'width="108"' in logo:
    logo=logo.replace('width="108" height="18" viewBox="0 0 108 18"','width="177" height="18" viewBox="0 0 177 18"',1)
    logo=logo.replace('</svg>',suffix+'</svg>')
    path.write_text(logo,encoding='utf-8')
footer=root/'assets/images/common/footer_logo.svg'
footer.write_text(logo.replace('width="177" height="18"','width="348" height="59"',1),encoding='utf-8')
index=root/'index.html'
html=index.read_text(encoding='utf-8')
html=re.sub(r'무신사(?!카피)','무신사카피',html)
html=re.sub(r'MUSINSA(?!COPY)','MUSINSACOPY',html)
index.write_text(html,encoding='utf-8')
for path in (root/'_next/static/chunks').glob('*.js'):
    content=path.read_text(encoding='utf-8')
    content=re.sub(r'MUSINSA(?!COPY)','MUSINSACOPY',content)
    path.write_text(content,encoding='utf-8')
print('Updated visible Korean/English branding and vector wordmarks.')
