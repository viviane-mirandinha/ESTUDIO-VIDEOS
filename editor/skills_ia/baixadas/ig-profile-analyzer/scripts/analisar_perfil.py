# -*- coding: utf-8 -*-
"""Analisa posts.jsonl dumpado pelo IGProf. Stdlib puro — sem pandas, sem installs.

Uso: python analisar_perfil.py posts.jsonl [followers]
Saída: analise.md + posts.csv na mesma pasta do JSONL.
"""
import csv, json, re, statistics as st, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CTA_RE = re.compile(r'\b(link in bio|link na bio|comenta|comment|segue|follow|salva|save|compartilh|share|tag a|marca )', re.I)


def url(r):
    kind = 'reel' if r.get('product_type') == 'clips' else 'p'
    return f"https://www.instagram.com/{kind}/{r['code']}/"


def views(r):
    if r.get('product_type') == 'clips':
        return r.get('plays')
    return r.get('view_count') if r.get('media_type') == 2 else None


def fmt(r):
    if r.get('product_type') == 'clips':
        return 'reel'
    return {1: 'imagem', 2: 'video', 8: 'carrossel'}.get(r.get('media_type'), 'outro')


def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else 0


def p90(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[int(len(xs) * 0.9)] if xs else 0


def n(x):
    return f"{x:,.0f}".replace(',', '.') if x is not None else '-'


def main():
    src = Path(sys.argv[1])
    followers = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    rows = [json.loads(l) for l in src.read_text(encoding='utf-8').splitlines() if l.strip()]
    seen, posts = set(), []
    for r in rows:
        if r['pk'] not in seen:
            seen.add(r['pk'])
            posts.append(r)
    posts.sort(key=lambda r: r['taken_at'], reverse=True)  # taken_at, nunca ordem do array
    for r in posts:
        dt = datetime.fromtimestamp(r['taken_at'], tz=timezone.utc)
        r['_dt'], r['_views'], r['_fmt'] = dt, views(r), fmt(r)
        r['_eng'] = (r.get('like_count') or 0) + (r.get('comment_count') or 0)
        cap = r.get('caption') or ''
        # campos pré-computados (transporte slim) têm prioridade sobre o texto da caption
        r['_cap_len'] = r.get('cap_len', len(cap))
        r['_hashtags'] = r.get('hashtags', cap.count('#'))
        r['_cta'] = bool(r.get('cta', CTA_RE.search(cap)))
        r['_collab'] = bool(r.get('coauthors'))

    # z-score vs janela móvel de 20 posts anteriores (cronológico) — corrige crescimento do canal
    chrono = list(reversed(posts))
    for i, r in enumerate(chrono):
        win = [p['_eng'] for p in chrono[max(0, i - 20):i]]
        if len(win) >= 5:
            mu, sd = st.mean(win), (st.pstdev(win) or 1)
            r['_z'] = round((r['_eng'] - mu) / sd, 2)
        else:
            r['_z'] = None

    out_csv = src.with_name('posts.csv')
    cols = ['url', 'data', 'formato', 'views', 'likes', 'comentarios', 'engajamento', 'zscore',
            'duracao_s', 'hashtags', 'cta', 'collab', 'likes_ocultos', 'caption']
    with out_csv.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in posts:
            w.writerow([url(r), r['_dt'].strftime('%d-%m-%Y %H:%M'), r['_fmt'], r['_views'],
                        r.get('like_count'), r.get('comment_count'), r['_eng'], r['_z'],
                        r.get('video_duration'), r['_hashtags'], int(r['_cta']),
                        int(r['_collab']), int(r.get('likes_hidden', False)),
                        (r.get('caption') or '').replace('\n', ' ')[:200]])

    L = []
    A = L.append
    vids = [r for r in posts if r['_views'] is not None]
    A(f"# Análise de perfil — {len(posts)} posts\n")
    if followers:
        A(f"Seguidores: {n(followers)}\n")

    A("## Top 15 por VIEWS (vídeos/reels)\n")
    A("| # | Data | Formato | Views | Likes | Coment. | z | Link |")
    A("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(sorted(vids, key=lambda r: r['_views'], reverse=True)[:15], 1):
        A(f"| {i} | {r['_dt']:%d-%m-%Y} | {r['_fmt']} | {n(r['_views'])} | {n(r.get('like_count'))} "
          f"| {n(r.get('comment_count'))} | {r['_z'] if r['_z'] is not None else '-'} | {url(r)} |")

    A("\n## Top 10 por ENGAJAMENTO (likes+coment.)\n")
    A("| # | Data | Formato | Engaj. | z | Link |")
    A("|---|---|---|---|---|---|")
    for i, r in enumerate(sorted(posts, key=lambda r: r['_eng'], reverse=True)[:10], 1):
        A(f"| {i} | {r['_dt']:%d-%m-%Y} | {r['_fmt']} | {n(r['_eng'])} "
          f"| {r['_z'] if r['_z'] is not None else '-'} | {url(r)} |")

    A("\n## Overperformers (z-score vs 20 posts anteriores — o que estourou pro tamanho da época)\n")
    zt = [r for r in posts if r['_z'] is not None and r['_z'] >= 1.5]
    for r in sorted(zt, key=lambda r: r['_z'], reverse=True)[:10]:
        A(f"- z={r['_z']} | {r['_dt']:%d-%m-%Y} | {r['_fmt']} | eng {n(r['_eng'])} | {url(r)}")
    if not zt:
        A("- nenhum post com z ≥ 1.5")

    A("\n## Formato (mediana, não média — outliers distorcem)\n")
    A("| Formato | Posts | % | Views med | Views P90 | Engaj. med |")
    A("|---|---|---|---|---|---|")
    for f_, c in Counter(r['_fmt'] for r in posts).most_common():
        grp = [r for r in posts if r['_fmt'] == f_]
        gv = [r['_views'] for r in grp if r['_views'] is not None]
        A(f"| {f_} | {c} | {c / len(posts):.0%} | {n(med(gv)) if gv else '-'} "
          f"| {n(p90(gv)) if gv else '-'} | {n(med([r['_eng'] for r in grp]))} |")

    if vids:
        A("\n## Duração x views (reels/vídeos)\n")
        A("| Duração | Posts | Views med |")
        A("|---|---|---|")
        buckets = [(0, 15), (15, 30), (30, 60), (60, 90), (90, 10 ** 6)]
        for lo, hi in buckets:
            grp = [r for r in vids if r.get('video_duration') and lo <= r['video_duration'] < hi]
            if grp:
                A(f"| {lo}-{hi if hi < 10**6 else '+'}s | {len(grp)} | {n(med([r['_views'] for r in grp]))} |")

    A("\n## Cadência\n")
    months = Counter(f"{r['_dt']:%Y-%m}" for r in posts)
    A(f"- Posts/mês (últimos 12): " + ", ".join(f"{m}={c}" for m, c in sorted(months.items())[-12:]))
    gaps = [(posts[i]['_dt'] - posts[i + 1]['_dt']).days for i in range(len(posts) - 1)]
    if gaps:
        A(f"- Gap mediano entre posts: {med(gaps):.1f} dias | maior silêncio: {max(gaps)} dias")

    A("\n## Melhor horário/dia (mediana de engajamento)\n")
    A("| Dia | Posts | Engaj. med |")
    A("|---|---|---|")
    DIAS = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    for wd in range(7):
        grp = [r for r in posts if r['_dt'].weekday() == wd]
        if grp:
            A(f"| {DIAS[wd]} | {len(grp)} | {n(med([r['_eng'] for r in grp]))} |")
    hrs = Counter()
    for r in posts:
        hrs[r['_dt'].hour] += 1
    top_h = sorted(((med([r['_eng'] for r in posts if r['_dt'].hour == h]), h)
                    for h in hrs if hrs[h] >= 3), reverse=True)[:3]
    A("- Top horas (UTC, ≥3 posts): " + ", ".join(f"{h}h (eng med {n(e)})" for e, h in top_h))

    A("\n## Padrões de caption — top 10% vs resto\n")
    ranked = sorted(posts, key=lambda r: r['_eng'], reverse=True)
    top = ranked[:max(1, len(ranked) // 10)]
    rest = ranked[len(top):] or top
    A(f"- Tam. caption med: top {med([r['_cap_len'] for r in top]):.0f} chars "
      f"vs resto {med([r['_cap_len'] for r in rest]):.0f}")
    A(f"- Hashtags med: top {med([r['_hashtags'] for r in top]):.0f} vs resto {med([r['_hashtags'] for r in rest]):.0f}")
    A(f"- CTA presente: top {sum(r['_cta'] for r in top) / len(top):.0%} vs resto {sum(r['_cta'] for r in rest) / len(rest):.0%}")
    collabs = [r for r in posts if r['_collab']]
    if collabs:
        A(f"- Collabs: {len(collabs)} posts, engaj. med {n(med([r['_eng'] for r in collabs]))} "
          f"vs solo {n(med([r['_eng'] for r in posts if not r['_collab']]))}")
    hidden = sum(1 for r in posts if r.get('likes_hidden'))
    if hidden:
        A(f"- {hidden} posts com likes ocultos (contados como null, não zero)")

    out_md = src.with_name('analise.md')
    out_md.write_text("\n".join(L), encoding='utf-8')
    print(out_md)
    print(out_csv)


if __name__ == '__main__':
    main()
