"""Label-validity and resolution-time functions: alternative cross-border definitions and time-varying Cox models."""
from collections import Counter
import numpy as np
import pandas as pd
from osmo_core import CASE, TS, GROUP, RCTY, UNKNOWN_CTY

ALT_DEFS = ['D2_team_home', 'D3_dominant75', 'D5_handler']


def sender_mask(df):
    """True for events that open a new team segment but were logged by the person who sent the incident
    (same resource as the previous event). These carry the SENDER's country, not the receiving team's."""
    prev_g = df.groupby(CASE)[GROUP].shift(); prev_r = df.groupby(CASE)['org:resource'].shift()
    return (prev_g.notna() & (df[GROUP] != prev_g) & (df['org:resource'] == prev_r)).to_numpy()


def team_home(df, sender_fix=True):
    """Fixed home country of each team = most frequent known handler country over the whole log."""
    k = df[~sender_mask(df)] if sender_fix else df
    k = k[k[RCTY] != UNKNOWN_CTY]
    home = k.groupby(GROUP)[RCTY].agg(lambda s: Counter(s).most_common(1)[0][0])
    purity = k.groupby(GROUP)[RCTY].agg(lambda s: Counter(s).most_common(1)[0][1] / len(s))
    return home.to_dict(), purity, k.groupby(GROUP).size()


def all_definitions(df, sender_fix=True):
    """Cross-border ping-pong under four definitions, each with the event index where it first occurs.
    D1 segment_mode : most frequent handler country of the returning segment differs from that of the segment
                      it came back from (main label of the paper)
    D2 team_home    : fixed home country of the returning team differs from that of the team it came back from
    D3 dominant75   : D1, counted only if both segments have one country holding >= 75% of known events, no tie
    D5 handler      : country of the last known handler before the hand-back differs from the first known
                      handler after it
    Also returns segment ambiguity counts."""
    home, _, _ = team_home(df, sender_fix)
    snd = sender_mask(df) if sender_fix else np.zeros(len(df), bool)
    rows, seg_stats = {}, Counter()
    for cid, g in df.groupby(CASE, sort=False):
        idx = g.index.to_numpy()
        segs = []
        for i, (grp, c) in enumerate(zip(g[GROUP], g[RCTY])):
            c = None if c == UNKNOWN_CTY else c
            if segs and segs[-1]['team'] == grp:
                segs[-1]['c'].append(c)
            else:
                segs.append(dict(team=grp, c=[] if snd[idx[i]] else [c], ev=i))
        for s in segs:
            kn = [x for x in s['c'] if x]; cnt = Counter(kn).most_common(2)
            s['mode'] = cnt[0][0] if cnt else None
            s['tie'] = len(cnt) == 2 and cnt[0][1] == cnt[1][1]
            s['dom'] = bool(cnt) and cnt[0][1] / len(kn) >= 0.75 and not s['tie']
            s['first'] = kn[0] if kn else None; s['last'] = kn[-1] if kn else None
            seg_stats['segments'] += 1
            seg_stats['no_known_country'] += not kn
            seg_stats['multi_country'] += len(set(kn)) > 1
            seg_stats['tie'] += s['tie']
        r = {k: None for k in ['pp_pos', 'D1_segment_mode_pos'] + [d + '_pos' for d in ALT_DEFS]}
        for i in range(1, len(segs)):
            a, b = segs[i], segs[i - 1]
            if a['team'] not in [s['team'] for s in segs[:i - 1]]:
                continue
            def hit(key, cond):
                if cond and r[key] is None:
                    r[key] = a['ev']
            hit('pp_pos', True)
            hit('D1_segment_mode_pos', a['mode'] and b['mode'] and a['mode'] != b['mode'])
            ha, hb = home.get(a['team']), home.get(b['team'])
            hit('D2_team_home_pos', ha and hb and ha != hb)
            hit('D3_dominant75_pos', a['dom'] and b['dom'] and a['mode'] != b['mode'])
            hit('D5_handler_pos', a['first'] and b['last'] and a['first'] != b['last'])
        for k in list(r):
            r[k[:-4]] = r[k] is not None
        rows[cid] = r
    return pd.DataFrame.from_dict(rows, orient='index'), dict(seg_stats)


def episodes(df, L):
    """Counting-process episodes: each incident is split at the moment of its first ping-pong and its first
    cross-border ping-pong, so exposure is TIME-VARYING (removes the time-at-risk bias of ever/never groups)."""
    t0 = df.groupby(CASE)[TS].first()
    ev_times = df.groupby(CASE)[TS].apply(list)
    rows = []
    for cid, r in L.iterrows():
        T = r.duration_h
        if T <= 0:
            continue
        times = ev_times[cid]
        def onset(pos):
            if pd.isna(pos): return None
            return (times[int(pos)] - t0[cid]).total_seconds() / 3600
        tp, tx = onset(r.pp_pos), onset(r.xpp_pos)
        cuts = sorted({0.0, T, *(c for c in (tp, tx) if c is not None and 0 < c < T)})
        for a, b in zip(cuts[:-1], cuts[1:]):
            rows.append(dict(case=cid, start=a, stop=b, event=int(b == T),
                             pp_any=int(tp is not None and tp <= a), xpp=int(tx is not None and tx <= a)))
    E = pd.DataFrame(rows)
    E['domestic_pp'] = E.pp_any * (1 - E.xpp)
    return E


def cox_time_varying(E, L, covars):
    """Cox model with left-truncated (start, stop] episodes. HR < 1 = slower resolution while exposed."""
    from statsmodels.duration.hazard_regression import PHReg
    D = E.join(L[covars], on='case') if covars else E
    X = pd.get_dummies(D[['domestic_pp', 'xpp'] + covars], columns=covars, drop_first=True, dtype=float)
    X = X.loc[:, X.std() > 0]
    m = PHReg(D.stop.values, X.values, status=D.event.values, entry=D.start.values, ties='efron').fit()
    out = pd.DataFrame({'term': X.columns, 'coef': m.params, 'se': m.bse, 'p': m.pvalues})
    out['HR'] = np.exp(out.coef); out['HR_lo'] = np.exp(out.coef - 1.96 * out.se); out['HR_hi'] = np.exp(out.coef + 1.96 * out.se)
    return out[out.term.isin(['domestic_pp', 'xpp'])]


def cox_time_bands(E, L, covars, cuts=(24.0, 168.0)):
    """Proportionality check: split every episode at the given hours after opening, let the exposure effect differ
    by time band (exposure x band) and test equal cross-border effects across bands with a Wald test."""
    from statsmodels.duration.hazard_regression import PHReg
    bands = [f'0-{int(cuts[0])}h'] + [f'{int(a)}-{int(b)}h' for a, b in zip(cuts[:-1], cuts[1:])] + [f'>{int(cuts[-1])}h']
    rows = []
    for r in E.itertuples(index=False):
        pts = sorted({r.start, r.stop, *(c for c in cuts if r.start < c < r.stop)})
        for a, b in zip(pts[:-1], pts[1:]):
            rows.append(dict(case=r.case, start=a, stop=b, event=int(r.event and b == r.stop), xpp=r.xpp,
                             domestic_pp=r.domestic_pp, band=bands[sum(a >= c for c in cuts)]))
    S = pd.DataFrame(rows)
    D = S.join(L[covars], on='case') if covars else S
    X = pd.DataFrame(index=D.index)
    for b in bands:
        X[f'xpp_{b}'] = D.xpp * (D.band == b); X[f'domestic_pp_{b}'] = D.domestic_pp * (D.band == b)
    if covars:
        X = X.join(pd.get_dummies(D[covars], drop_first=True, dtype=float))
    X = X.loc[:, X.std() > 0].astype(float)
    m = PHReg(D.stop.values, X.values, status=D.event.values, entry=D.start.values, ties='efron').fit()
    out = []
    for j, c in enumerate(X.columns):
        if c.startswith(('xpp_', 'domestic_pp_')):
            exp, band = c.rsplit('_', 1)
            out.append(dict(exposure=exp, band=band, events_while_exposed=int(((X[c] > 0) & (D.event == 1)).sum()),
                            HR=np.exp(m.params[j]), HR_lo=np.exp(m.params[j] - 1.96 * m.bse[j]),
                            HR_hi=np.exp(m.params[j] + 1.96 * m.bse[j]), p=m.pvalues[j]))
    idx = [list(X.columns).index(f'xpp_{b}') for b in bands]
    R = np.zeros((len(bands) - 1, X.shape[1]))
    for i in range(len(bands) - 1):
        R[i, idx[i]], R[i, idx[i + 1]] = 1, -1
    wald_p = float(m.wald_test(R, scalar=True).pvalue)
    return pd.DataFrame(out), wald_p
