"""Build self-contained SVG workflow and animated project showcase assets.

No JavaScript, external fonts, image files, or external services are needed to
display the SVGs. Diagrams illustrate project themes; they are not data plots.
"""
from html import escape
from math import cos, sin, pi
from pathlib import Path
import random

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
ORANGE = '#E79600'
PROJECTS = [
    ('Uniform Fragmentation', '', 'STATISTICAL PHYSICS',
     'A null model for energy sharing', 'in cosmic-ray air showers.',
     'Python  /  Monte Carlo  /  Statistical modeling', 'shower'),
    ('Leading Particles', '& the Muon Puzzle', 'PARTICLE ASTROPHYSICS',
     'Leading-particle effects and muon', 'production in cosmic-ray cascades.',
     'CONEX  /  ROOT  /  Cosmic rays', 'muons'),
    ('CONEX / APOEMA', 'Operations Guide', 'REPRODUCIBLE SCIENCE',
     'A practical guide to air-shower analysis', 'with PyROOT and C++ / ROOT.',
     'CONEX  /  PyROOT  /  Documentation', 'guide'),
    ('Poincaré Maps', '& the Duffing Oscillator', 'NONLINEAR DYNAMICS',
     'A visual introduction to phase space', 'and the transition to chaos.',
     'Dynamical systems  /  Scientific visualization', 'phase'),
    ('Quanta Flashcards', '', 'SCIENTIFIC SOFTWARE',
     'Technical flashcards with LaTeX', 'and spaced repetition. Local-first.',
     'TypeScript  /  React  /  Electron', 'quanta'),
]


def text(x, y, value, color, size=18, weight=400, extra=''):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" {extra}>{escape(value)}</text>')


def svg(width, height, content, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}" '
            'font-family="Arial,Helvetica,sans-serif">'
            f'<title>{escape(title)}</title>{content}</svg>\n')


def icon(name, x, y, scale=1):
    shapes = {
        'model': '<path d="M10 5h17l8 8v30H10zM27 5v10h8M16 22h12M16 29h12M16 36h8"/>',
        'simulate': '<path d="M19 4h10l2 6 6 3 6-1 5 8-4 5v7l4 5-5 8-6-1-6 3-2 6H19l-2-6-6-3-6 1-5-8 4-5v-7l-4-5 5-8 6 1 6-3z" transform="translate(4 -3) scale(.85)"/><circle cx="25" cy="22" r="7"/>',
        'compare': '<path d="M6 41V23h8v18zM21 41V14h8v27zM36 41V5h8v36z"/>',
        'visualize': '<rect x="5" y="7" width="40" height="34" rx="3"/><circle cx="34" cy="16" r="3"/><path d="M5 35l12-14 9 9 6-5 13 14"/>',
    }
    return (f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{ORANGE}" '
            'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">'
            + shapes[name] + '</g>')


def workflow(dark, mobile):
    foreground = '#E6EDF3' if dark else '#1D1D1B'
    result = []
    for index, (label, symbol) in enumerate(zip(['Model', 'Simulate', 'Compare', 'Visualize'],
                                               ['model', 'simulate', 'compare', 'visualize'])):
        if mobile:
            x, y = 16+(index % 2)*270, 22+(index // 2)*102
        else:
            x, y = 18+index*260, 26
        result.append(icon(symbol, x, y, .9))
        result.append(text(x+60, y+30, label, foreground, 25, 500))
        if (mobile and index % 2 == 0) or (not mobile and index < 3):
            ax = x+222
            result.append(f'<path d="M{ax} {y+23}h23m-7-6 7 6-7 6" fill="none" stroke="{ORANGE}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(560 if mobile else 1060, 226 if mobile else 108, ''.join(result),
               'Research workflow: Model, Simulate, Compare, Visualize')


def shower(ink, muons=False):
    rng = random.Random(407 if muons else 169)
    result = [f'<path d="M215 0v21" stroke="{ORANGE}" stroke-width="2"/>']
    current = [(215., 21., 165.)]
    leaves = []
    for generation in range(6):
        following = []
        for x, y, spread in current:
            for side in (-1, 1):
                child_x = x + side * spread * rng.uniform(.36, .60)
                child_y = 21+(generation+1)*21 + rng.uniform(-2, 2)
                orange = (x > 205 and side > 0) if muons else rng.random()<.26
                color = ORANGE if orange else ink
                opacity = .95 if orange else (.66 if generation<3 else .38)
                result.append(f'<path d="M{x:.2f} {y:.2f}Q{x:.2f} {y+8:.2f} {child_x:.2f} {child_y:.2f}" fill="none" stroke="{color}" stroke-width="{1.5 if orange else .85}" opacity="{opacity}"/>')
                following.append((child_x,child_y,spread*.54))
                if generation==5:
                    leaves.append((child_x,child_y,orange))
        current=following
    result.append(f'<path d="M15 160H415" fill="none" stroke="{ink}" opacity=".3"/>')
    if muons:
        for x,y,orange in leaves[::5]:
            result.append(f'<path d="M{x:.1f} {y:.1f}l9 {159-y:.1f}" stroke="{ORANGE if orange else ink}" stroke-width=".75" opacity=".6"/>')
            result.append(f'<circle cx="{x+9:.1f}" cy="160" r="2.2" fill="{ORANGE}" opacity=".8"/>')
        result.append(text(357, 151, 'μ', ORANGE, 18))
        result.append(text(307, 94, 'π', ORANGE, 16))
    return ''.join(result)


def phase_space(ink):
    # Illustrative forced Duffing trajectory, integrated using classical RK4.
    def derivative(t, x, v):
        return v, x-x*x*x-.2*v+.3*cos(1.2*t)
    x,v,t,dt=.1,0.,0.,.03
    points=[]
    section=[]
    previous_period=-1
    for index in range(15000):
        a,b=derivative(t,x,v)
        c,d=derivative(t+dt/2,x+a*dt/2,v+b*dt/2)
        e,f=derivative(t+dt/2,x+c*dt/2,v+d*dt/2)
        g,h=derivative(t+dt,x+e*dt,v+f*dt)
        x+=dt*(a+2*c+2*e+g)/6
        v+=dt*(b+2*d+2*f+h)/6
        t+=dt
        if index>5000 and index%7==0:
            points.append((215+x*115,84-v*55))
        period=int(t/(2*pi/1.2))
        if period!=previous_period and index>5000:
            section.append((215+x*115,84-v*55))
        previous_period=period
    path=' '.join(f'{px:.2f},{py:.2f}' for px,py in points)
    result=f'<path d="M25 84H405M215 10V158" stroke="{ink}" opacity=".2" stroke-width=".7"/><polyline points="{path}" fill="none" stroke="{ink}" stroke-width=".6" opacity=".38"/>'
    for px,py in section:
        result+=f'<circle cx="{px:.2f}" cy="{py:.2f}" r="1.8" fill="{ORANGE}"/>'
    return result


def guide(ink, panel):
    result=f'<rect x="64" y="10" width="304" height="147" rx="7" fill="{panel}" stroke="{ink}" stroke-width=".7" opacity=".9"/>'
    result+=f'<path d="M64 35H368" stroke="{ink}" opacity=".3"/>'
    for x in (77,89,101):
        result+=f'<circle cx="{x}" cy="23" r="2" fill="{ORANGE if x==77 else ink}" opacity=".7"/>'
    result+=text(82,61,'CONEX',ORANGE,16,600)
    result+=text(82,87,'ROOT  →  PyROOT / C++',ink,15)
    result+=text(82,114,'inspect · analyze · reproduce',ink,13)
    result+=f'<path d="M82 137h99m13 0h48m12 0h39" stroke="{ORANGE}" stroke-width="1.3" opacity=".7"/>'
    return result


def quanta(ink,panel):
    result=''
    for x,y,angle in [(101,21,-8),(118,13,5),(125,15,0)]:
        result+=f'<rect x="{x}" y="{y}" width="198" height="130" rx="8" fill="{panel}" stroke="{ink}" stroke-width=".8" transform="rotate({angle} 224 80)" opacity=".8"/>'
    result+=text(144,43,'QUANTA',ORANGE,12,600, 'letter-spacing="2"')
    result+=text(165,91,'E = mc²',ink,28)
    result+=text(145,127,'LaTeX  ·  Spaced repetition',ink,11)
    return result


def card(index,dark,active=False):
    foreground='#E6EDF3' if dark else '#1D1D1B'
    muted='#A8B3BE' if dark else '#626B73'
    panel='#0D1117' if dark else '#FFFFFF'
    border=ORANGE if active else ('#353D45' if dark else '#D0D7DE')
    title,subtitle,category,desc1,desc2,tags,kind=PROJECTS[index]
    result=f'<rect x="1" y="1" width="498" height="368" rx="13" fill="{panel}" stroke="{border}" stroke-width="{1.6 if active else 1}"/>'
    result+=f'<path d="M24 1h52" stroke="{ORANGE}" stroke-width="2"/>'
    result+=text(24,29,category,ORANGE,11,600,'letter-spacing="1.4"')
    result+=text(439,29,f'{index+1:02d} / 05',muted,11)
    if kind in ('shower','muons'):
        art=shower(foreground,kind=='muons')
    elif kind=='phase':
        art=phase_space(foreground)
    elif kind=='guide':
        art=guide(foreground,panel)
    else:
        art=quanta(foreground,panel)
    result+=f'<g transform="translate(35 43)">{art}</g>'
    result+=text(24,237,title,foreground,25,600)
    if subtitle:
        result+=text(24,265,subtitle,foreground,23,600)
    result+=text(24,301,desc1,muted,18)
    result+=text(24,325,desc2,muted,18)
    result+=text(24,352,tags,ORANGE,12)
    return result


def animation_style():
    rules=['.scene{opacity:0;animation-duration:30s;animation-iteration-count:infinite;animation-timing-function:linear;transform-box:fill-box;transform-origin:center}.scene-0{opacity:1}']
    for index in range(5):
        start=index*20
        if index==0:
            frames='0%,16%{opacity:1;transform:translateX(0)}20%,96%{opacity:0;transform:translateX(-22px)}100%{opacity:1;transform:translateX(0)}'
        else:
            frames=f'0%,{start-4}%{{opacity:0;transform:translateX(22px)}}{start}%,{start+16}%{{opacity:1;transform:translateX(0)}}{start+20}%,100%{{opacity:0;transform:translateX(-22px)}}'
        rules.append(f'.scene-{index}{{animation-name:project{index}}}@keyframes project{index}{{{frames}}}')
    rules.append('@media(prefers-reduced-motion:reduce){.scene{animation:none!important;opacity:0!important}.scene-0{opacity:1!important}}')
    return '<style>'+''.join(rules)+'</style>'


def carousel(dark,mobile):
    width,height=(540,430) if mobile else (1080,450)
    result=animation_style()+f'<defs><clipPath id="viewport"><rect width="{width}" height="{height}"/></clipPath></defs><g clip-path="url(#viewport)">'
    for index in range(5):
        result+=f'<g class="scene scene-{index}">'
        if not mobile:
            result+=f'<g transform="translate(-70 72) scale(.75)" opacity=".3">{card((index-1)%5,dark)}</g>'
            result+=f'<g transform="translate(775 72) scale(.75)" opacity=".3">{card((index+1)%5,dark)}</g>'
        result+=f'<g transform="translate({20 if mobile else 290} 18)">{card(index,dark,True)}</g>'
        for dot in range(5):
            cx=width/2-40+dot*20
            result+=f'<circle cx="{cx}" cy="410" r="{3.6 if dot==index else 2.7}" fill="{ORANGE if dot==index else ("#626D77" if dark else "#A0A7AD")}"/>'
        result+='</g>'
    result+='</g>'
    return svg(width,height,result,'Selected work: five projects rotate automatically; repository links are listed below')


def main():
    ASSETS.mkdir(exist_ok=True)
    for dark in (True,False):
        for mobile in (False,True):
            suffix=('dark' if dark else 'light')+('-mobile' if mobile else '')
            (ASSETS/f'workflow-{suffix}.svg').write_text(workflow(dark,mobile),encoding='utf-8')
            (ASSETS/f'selected-work-{suffix}.svg').write_text(carousel(dark,mobile),encoding='utf-8')
    print('Built workflow images and five-project animated SVG showcases for desktop and mobile.')


if __name__=='__main__':
    main()
