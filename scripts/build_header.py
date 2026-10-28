"""Rebuild the original sparse header artwork, retaining the corrected title.

The outlined name and original APOEMA paths are preserved. Geometry is seeded
and uses the original, restrained particle count rather than the denser variant.
"""
from math import sin, cos, pi
from pathlib import Path
import random
import xml.etree.ElementTree as ET

ASSETS=Path(__file__).resolve().parents[1]/'assets'
SVG='http://www.w3.org/2000/svg'
ORANGE='#E79600'
TITLE='Statistical Physicist and Astrophysicist'
ET.register_namespace('',SVG)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')


def group(markup):
    return ET.fromstring(f'<g xmlns="{SVG}">{markup}</g>')


def galaxy(dark):
    rng = random.Random(169)
    neutral = '#E6EDF3' if dark else '#1D1D1B'
    mid = '#9D9D9C' if dark else '#696969'
    parts = ['<g transform="translate(1000 150) rotate(-22)">']
    # Elliptical orbits with a fine, restrained scientific line-art treatment.
    for radius in range(46, 243, 13):
        parts.append(f'<ellipse rx="{radius}" ry="{radius*.37:.2f}" fill="none" stroke="{mid}" stroke-width=".65" opacity=".29" transform="rotate({rng.uniform(-8,8):.2f})"/>')
    for arm in range(3):
        for strand in range(9):
            points = []
            for step in range(170):
                t = step/169
                radius = 8 + 226*t
                angle = 1.8 + arm*2*pi/3 + strand*.055 + 5.2*t
                points.append(f'{radius*cos(angle):.2f},{radius*.37*sin(angle):.2f}')
            color = ORANGE if strand in (0,5) else neutral
            parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="{.7 if strand in (0,5) else .45}" opacity="{.55 if strand in (0,5) else .25}"/>')
    for index in range(660):
        t = rng.random()**.9
        radius = 9+229*t
        arm = rng.randrange(3)
        angle = 1.8+arm*2*pi/3+5.2*t+rng.gauss(0,.14+(.09*t))
        x = radius*cos(angle)+rng.gauss(0,3)
        y = radius*.37*sin(angle)+rng.gauss(0,2.7)
        fill = ORANGE if rng.random()<.29 else neutral
        r = rng.choice([.6,.7,.8,1,1.2,1.6])
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" opacity="{rng.uniform(.25,.9):.2f}"/>')
    for index in range(110):
        x,y=rng.gauss(0,24),rng.gauss(0,8)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rng.uniform(.45,1.8):.2f}" fill="{ORANGE}" opacity=".8"/>')
    for index in range(90):
        x,y=rng.uniform(-255,255),rng.uniform(-114,114)
        if (x/260)**2+(y/118)**2<1.1:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.choice([.6,.8,1.1])}" fill="{ORANGE if index%4==0 else mid}" opacity=".6"/>')
    parts.append('</g>')
    layer=group(''.join(parts))
    layer.set('id','header-galaxy')
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
        leading=group(f'<path d="M722 122 L1000 150" fill="none" stroke="{ORANGE}" stroke-width="1.25"/><circle cx="722" cy="122" r="4.7" fill="{ORANGE}"/>')
        leading.set('id','header-leading-particle')
        root.insert(1,galaxy(theme=='dark'))
        root.insert(2,leading)
        label=f'Davi Santos-Silva — {TITLE} — APOETA'
        root.set('aria-label',label)
        root.find(f'{{{SVG}}}title').text=label
        root.find(f'{{{SVG}}}text').text=TITLE
        path.write_text(ET.tostring(root,encoding='unicode')+'\n',encoding='utf-8')
        print(path.name,'restored original sparse particles and retained corrected title')


if __name__=='__main__':
    main()
