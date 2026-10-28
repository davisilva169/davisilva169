"""Refresh the header's particle field while preserving its lettering and logo.

The existing outlined name and original APOEMA vector paths stay intact. All
generated particles are seeded, and rebuilding replaces rather than adds layers.
"""
from math import cos, sin, pi, exp
from pathlib import Path
import random
import xml.etree.ElementTree as ET

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
SVG = 'http://www.w3.org/2000/svg'
ORANGE = '#E79600'
TITLE = 'Statistical Physicist and Astrophysicist'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')


def group(markup):
    return ET.fromstring(f'<g xmlns="{SVG}">{markup}</g>')


def circle(x, y, radius, fill, opacity):
    return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" '
            f'fill="{fill}" opacity="{opacity:.2f}"/>')


def particle_field(dark):
    rng = random.Random(16927)
    neutral = '#E6EDF3' if dark else '#1D1D1B'
    muted = '#9D9D9C' if dark else '#686B6D'
    parts = []
    # Wide, diffuse volume around the established galaxy. A clear left margin
    # protects the name, with density and opacity tapering as particles approach it.
    for _ in range(1350):
        x, y = rng.gauss(1004, 151), rng.gauss(149, 67)
        if not (624 < x < 1272 and 9 < y < 292):
            continue
        taper = min(1., max(0., (x-624)/300))
        if rng.random() > .12 + .88*taper:
            continue
        fill = ORANGE if rng.random() < .18 else (neutral if rng.random()<.57 else muted)
        radius = rng.choices([.55,.75,1.,1.3,1.65],weights=[2,4,5,3,1])[0]
        opacity = rng.uniform(.18,.62) * (.25+.75*taper)
        parts.append(circle(x,y,radius,fill,opacity))
    # A sparse approach toward the leading particle, broadening toward the core.
    for _ in range(290):
        t = rng.random()**.42
        x = 638 + 409*t
        y = 122 + 28*t + rng.gauss(0,10+52*t)
        if 12 < y < 288:
            parts.append(circle(x,y,rng.uniform(.55,1.4),
                                ORANGE if rng.random()<.22 else neutral,
                                (.12+.42*t)*rng.uniform(.55,1.)))
    layer=group(''.join(parts))
    layer.set('id','header-particles')
    return layer


def galaxy(dark):
    rng = random.Random(169)
    neutral = '#E6EDF3' if dark else '#1D1D1B'
    muted = '#9D9D9C' if dark else '#696969'
    parts=[]
    for radius in range(46,243,13):
        parts.append(f'<ellipse rx="{radius}" ry="{radius*.37:.2f}" fill="none" stroke="{muted}" stroke-width=".65" opacity=".29" transform="rotate({rng.uniform(-8,8):.2f})"/>')
    for arm in range(3):
        for strand in range(9):
            points=[]
            for step in range(170):
                t=step/169
                radius=8+226*t
                angle=1.8+arm*2*pi/3+strand*.055+5.2*t
                points.append(f'{radius*cos(angle):.2f},{radius*.37*sin(angle):.2f}')
            accent=strand in (0,5)
            parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{ORANGE if accent else neutral}" stroke-width="{.7 if accent else .45}" opacity="{.55 if accent else .25}"/>')
    # A denser particle distribution follows the same existing spiral arms.
    for _ in range(1900):
        t=rng.random()**.82
        radius=9+229*t
        arm=rng.randrange(3)
        angle=1.8+arm*2*pi/3+5.2*t+rng.gauss(0,.16+.13*t)
        x=radius*cos(angle)+rng.gauss(0,3.5)
        y=radius*.37*sin(angle)+rng.gauss(0,3.7)
        parts.append(circle(x,y,rng.choices([.6,.8,1.,1.3,1.75],weights=[2,4,5,2,1])[0],
                            ORANGE if rng.random()<.24 else neutral,rng.uniform(.24,.86)))
    for _ in range(175):
        parts.append(circle(rng.gauss(0,24),rng.gauss(0,8),rng.uniform(.5,1.65),ORANGE,rng.uniform(.45,.87)))
    layer=group(''.join(parts))
    layer.set('id','header-galaxy')
    layer.set('transform','translate(1000 150) rotate(-22)')
    return layer


def leading_particle():
    # The leading orange particle is much larger than the surrounding field.
    # The lighter line conveys its connection to the dense interaction region.
    markup=(f'<path d="M706 122L1000 150" fill="none" stroke="{ORANGE}" stroke-width="1.7" opacity=".95"/>'
            +circle(706,122,18,ORANGE,.045)
            +circle(706,122,12.8,ORANGE,.10)
            +circle(706,122,8,ORANGE,1.))
    layer=group(markup)
    layer.set('id','header-leading-particle')
    return layer


def main():
    for theme in ('dark','light'):
        path=ASSETS/f'header-{theme}.svg'
        root=ET.parse(path).getroot()
        for child in list(root):
            if (child.get('id') in {'header-particles','header-galaxy','header-leading-particle'}
                or child.get('transform')=='translate(1000 150) rotate(-22)'
                or child.get('d')=='M722 122 L1000 150'
                or (child.tag==f'{{{SVG}}}circle' and child.get('cx')=='722')):
                root.remove(child)
        for index,layer in enumerate([particle_field(theme=='dark'),galaxy(theme=='dark'),leading_particle()]):
            root.insert(index+1,layer)
        label=f'Davi Santos-Silva — {TITLE} — APOETA'
        root.set('aria-label',label)
        root.find(f'{{{SVG}}}title').text=label
        subtitle=root.find(f'{{{SVG}}}text')
        subtitle.text=TITLE
        path.write_text(ET.tostring(root,encoding='unicode')+'\n',encoding='utf-8')
        circles=len(root.findall(f'.//{{{SVG}}}circle'))
        print(f'{path.name}: {circles} particle circles; title updated')


if __name__=='__main__':
    main()
