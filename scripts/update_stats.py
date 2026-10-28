"""Refresh self-hosted profile cards using public GitHub REST data only."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USER = 'davisilva169'
ROOT = Path(__file__).resolve().parents[1]
ORANGE = '#E79600'


def request_json(path, token):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': USER + '-profile-stats'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    for attempt in range(3):
        try:
            with urlopen(Request('https://api.github.com' + path, headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 409:
                return []
            if attempt == 2 or error.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(2 ** attempt)


def paginated(path, token):
    result = []
    for page in range(1, 101):
        separator = '&' if '?' in path else '?'
        batch = request_json(f'{path}{separator}per_page=100&page={page}', token)
        if not isinstance(batch, list):
            raise ValueError('Expected a paginated API list')
        result.extend(batch)
        if len(batch) < 100:
            return result
    raise RuntimeError('Pagination limit reached; refusing to publish partial counts')


def card(body, label, height, width=1000):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label, quote=True)}">'
            f'<title>{escape(label)}</title>{body}</svg>\n')


def text(x, y, value, color, size=17, weight='400'):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" '
            f'font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>')


def build_cards(data, languages):
    assets = ROOT / 'assets'
    assets.mkdir(exist_ok=True)
    for theme in ('dark', 'light'):
        foreground = '#E6EDF3' if theme == 'dark' else '#1D1D1B'
        muted = '#A2ADB8' if theme == 'dark' else '#656D76'
        border = '#30363D' if theme == 'dark' else '#D0D7DE'
        body = text(24, 37, 'GitHub at a glance', foreground, 24, '600')
        metrics = [('Public repositories', data['repositories']),
                   ('Commits', data['commits']),
                   ('Stars received', data['stars']),
                   ('Followers', data['followers'])]
        for index, (label, value) in enumerate(metrics):
            x = 24 + index * 244
            body += text(x, 100, f'{value:,}', ORANGE, 40, '600')
            body += text(x, 132, label, foreground, 17)
            if index < 3:
                body += f'<path d="M{x+217} 64V139" stroke="{border}"/>'
        body += text(24, 179, 'Owned public repositories; forks excluded. Commits: default branches.', muted, 13)
        body += text(24, 200, f'Updated {data["updated"]} UTC', muted, 13)
        alt = ', '.join(f'{label}: {value}' for label, value in metrics)
        (assets / f'stats-{theme}.svg').write_text(card(body, alt, 216), encoding='utf-8')
        entries = languages.most_common(5)
        remainder = sum(languages.values()) - sum(value for _, value in entries)
        if remainder:
            entries.append(('Other', remainder))
        total = sum(languages.values())
        colors = [ORANGE, '#C38125', '#9D9D9C', '#707A84', '#AFA18E', '#555F69']
        body = text(24, 37, 'Languages in my public repositories', foreground, 24, '600')
        cursor = 24.0
        for index, (language, count) in enumerate(entries):
            width = 952 * count / max(total, 1)
            body += f'<rect x="{cursor:.3f}" y="63" width="{width:.3f}" height="12" fill="{colors[index]}"/>'
            cursor += width
            column, row = index % 3, index // 3
            x, y = 24 + column * 322, 111 + row * 31
            body += f'<circle cx="{x+5}" cy="{y-5}" r="4" fill="{colors[index]}"/>'
            body += text(x+18, y, f'{language}  {count/max(total,1):.1%}', foreground, 16)
        body += text(24, 183, 'Share of code bytes reported by GitHub; not a proficiency rating.', muted, 13)
        alt = 'Language share by code size: ' + ', '.join(f'{name} {count/max(total,1):.1%}' for name, count in entries)
        (assets / f'languages-{theme}.svg').write_text(card(body, alt, 202), encoding='utf-8')
        mobile = text(20, 36, 'GitHub at a glance', foreground, 24, '600')
        for index, (label, value) in enumerate(metrics):
            x, y = 20 + (index % 2) * 240, 102 + (index // 2) * 105
            mobile += text(x, y, f'{value:,}', ORANGE, 40, '600')
            mobile += text(x, y+30, label, foreground, 19)
        mobile += text(20, 275, 'Owned public repositories; forks excluded.', muted, 15)
        mobile += text(20, 298, 'Commits: default branches.', muted, 15)
        mobile += text(20, 321, f'Updated {data["updated"]} UTC', muted, 15)
        (assets / f'stats-{theme}-mobile.svg').write_text(card(mobile, 'Public GitHub statistics', 340, 500), encoding='utf-8')
        mobile = text(20, 36, 'Languages in public repositories', foreground, 24, '600')
        cursor = 20.0
        for index, (language, count) in enumerate(entries):
            width = 460 * count / max(total, 1)
            mobile += f'<rect x="{cursor:.3f}" y="62" width="{width:.3f}" height="12" fill="{colors[index]}"/>'
            cursor += width
            x, y = 20 + (index % 2) * 240, 112 + (index // 2) * 38
            mobile += f'<circle cx="{x+4}" cy="{y-6}" r="4" fill="{colors[index]}"/>'
            mobile += text(x+17, y, f'{language} {count/max(total,1):.1%}', foreground, 18)
        mobile += text(20, 238, 'Share of code bytes reported by GitHub;', muted, 15)
        mobile += text(20, 260, 'not a proficiency rating.', muted, 15)
        (assets / f'languages-{theme}-mobile.svg').write_text(card(mobile, alt, 280, 500), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-auth', action='store_true', help='Read the signed-in GitHub CLI credential in memory')
    args = parser.parse_args()
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if args.local_auth and not token:
        token = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, check=True).stdout.strip()
    profile = request_json(f'/users/{USER}', token)
    repositories = [repo for repo in paginated(f'/users/{USER}/repos?type=owner', token)
                    if not repo['private'] and not repo['fork'] and repo['owner']['login'].lower() == USER.lower()]
    languages = Counter()
    commits = 0
    for repo in repositories:
        languages.update(request_json(f'/repos/{USER}/{repo["name"]}/languages', token))
        contributors = paginated(f'/repos/{USER}/{repo["name"]}/contributors', token)
        commits += sum(person['contributions'] for person in contributors if person.get('login', '').lower() == USER.lower())
    data = {'repositories': len(repositories), 'commits': commits,
            'stars': sum(repo['stargazers_count'] for repo in repositories),
            'followers': profile['followers'],
            'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d')}
    # Do not replace published cards until every data request has succeeded.
    build_cards(data, languages)
    print(json.dumps(data))


if __name__ == '__main__':
    main()
