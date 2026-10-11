"""Core pipeline: labels + prefix features for BPIC 2013 incidents (OSMO ping-pong study)."""
import numpy as np
import pandas as pd
from collections import Counter

CASE, TS = "case:concept:name", "ts"
GROUP, RCTY, OCTY = "org:group", "resource country", "organization country"
UNKNOWN_CTY = "0"


def load_log(path):
    df = pd.read_csv(path)
    df[TS] = pd.to_datetime(df["time:timestamp"], utc=True, format="mixed")
    df["org:role"] = df["org:role"].fillna("NA")
    df = df.sort_values([CASE, TS], kind="stable").reset_index(drop=True)
    return df


def _is_sender_event(i, groups, resources):
    """BPIC 2013 logs the event that opens a new team segment (usually 'Awaiting Assignment') under the
    person who transferred the incident, i.e. the same resource as the previous event (92% of team changes).
    Such an event says nothing about where the RECEIVING team is, so it is excluded from that team's country."""
    return i > 0 and groups[i] != groups[i - 1] and resources[i] == resources[i - 1]


def _segments(groups, countries, resources):
    """Collapse consecutive events of the same team into segments.
    Returns list of (team, country_mode, first_event_index); the sender-logged opening event is not
    used for the segment's country."""
    segs = []
    for i, (g, c) in enumerate(zip(groups, countries)):
        if segs and segs[-1][0] == g:
            segs[-1][1].append(c)
        else:
            segs.append([g, [] if _is_sender_event(i, groups, resources) else [c], i])
    out = []
    for g, cs, i0 in segs:
        known = [x for x in cs if x != UNKNOWN_CTY]
        mode = Counter(known).most_common(1)[0][0] if known else None  # ties -> first seen (deterministic)
        out.append((g, mode, i0))
    return out


def case_labels(df):
    """Per-case outcome labels with the event index at which each outcome first occurs.
    pp  : team ping-pong = incident returns to a support team it already left (A..B..A)
    xpp : cross-border ping-pong = a ping-pong return where the returning team's country
          differs from the country of the team it bounced back from
    xh  : any handover between teams located in different countries
    """
    rows = []
    for cid, g in df.groupby(CASE, sort=False):
        segs = _segments(g[GROUP].tolist(), g[RCTY].tolist(), g['org:resource'].tolist())
        pp_pos = xpp_pos = xh_pos = None
        n_bounce = n_xbounce = 0
        pairs = []
        for i in range(1, len(segs)):
            team, cty, ev = segs[i]
            pteam, pcty, _ = segs[i - 1]
            if cty and pcty and cty != pcty and xh_pos is None:
                xh_pos = ev
            if team in [s[0] for s in segs[: i - 1]]:
                n_bounce += 1
                if pp_pos is None:
                    pp_pos = ev
                if cty and pcty and cty != pcty:
                    n_xbounce += 1
                    pairs.append(tuple(sorted((cty, pcty))))
                    if xpp_pos is None:
                        xpp_pos = ev
        rows.append(dict(
            case=cid, n_events=len(g), start=g[TS].iloc[0], end=g[TS].iloc[-1],
            duration_h=(g[TS].iloc[-1] - g[TS].iloc[0]).total_seconds() / 3600,
            n_teams=g[GROUP].nunique(), n_handovers=len(segs) - 1,
            n_countries=len({x for x in g[RCTY] if x != UNKNOWN_CTY}),
            pp=pp_pos is not None, pp_pos=pp_pos, xpp=xpp_pos is not None, xpp_pos=xpp_pos,
            xh=xh_pos is not None, xh_pos=xh_pos, n_bounce=n_bounce, n_xbounce=n_xbounce,
            xpp_pairs=";".join(f"{a}|{b}" for a, b in pairs),
        ))
    return pd.DataFrame(rows).set_index("case")


LIFECYCLES = None  # filled from data
CAT_FEATS = ["impact_last", "product", "org_involved_last", "org_country_first", "first_team",
             "first_country", "last_team", "last_country", "last_role", "last_lifecycle", "last_activity"]


def prefix_features(df, max_k=10):
    """Aggregation encoding of every prefix of length 1..max_k (only info known at event k)."""
    lifecycles = sorted(df["lifecycle:transition"].unique())
    acts = sorted(df["concept:name"].unique())
    recs = []
    for cid, g in df.groupby(CASE, sort=False):
        grp = g[GROUP].to_numpy(); cty = g[RCTY].to_numpy(); ts = g[TS].to_numpy()
        lc = g["lifecycle:transition"].to_numpy(); ac = g["concept:name"].to_numpy()
        res = g["org:resource"].to_numpy(); role = g["org:role"].to_numpy()
        imp = g["impact"].to_numpy(); prod = g["product"].to_numpy()
        orgi = g["organization involved"].to_numpy(); octy = g[OCTY].to_numpy()
        n = len(g)
        t0 = pd.Timestamp(ts[0])
        known_cty = [c if c != UNKNOWN_CTY else None for c in cty]
        for k in range(1, min(n, max_k) + 1):
            # team segments within prefix
            seg_teams, seg_cty = [], []
            for j in range(k):
                if not seg_teams or seg_teams[-1] != grp[j]:
                    seg_teams.append(grp[j])
                    seg_cty.append([] if _is_sender_event(j, grp, res) else [known_cty[j]])
                else:
                    seg_cty[-1].append(known_cty[j])
            seg_mode = []
            for cs in seg_cty:
                kn = [x for x in cs if x]
                seg_mode.append(Counter(kn).most_common(1)[0][0] if kn else None)
            x_hand = sum(1 for i in range(1, len(seg_mode))
                         if seg_mode[i] and seg_mode[i - 1] and seg_mode[i] != seg_mode[i - 1])
            tk = pd.Timestamp(ts[k - 1])
            gaps = np.diff(ts[:k]).astype("timedelta64[s]").astype(float) / 3600 if k > 1 else np.array([0.0])
            last_known = next((c for c in reversed(known_cty[:k]) if c), "UNK")
            first_known = next((c for c in known_cty[:k] if c), "UNK")
            r = dict(
                case=cid, k=k,
                impact_last=imp[k - 1], product=prod[k - 1], org_involved_last=orgi[k - 1],
                org_country_first=octy[0], first_team=grp[0], first_country=first_known,
                last_team=grp[k - 1], last_country=last_known, last_role=role[k - 1],
                last_lifecycle=lc[k - 1], last_activity=ac[k - 1],
                n_teams=len(set(grp[:k])), n_handovers=len(seg_teams) - 1, n_xborder_handovers=x_hand,
                n_countries=len({c for c in known_cty[:k] if c}), n_resources=len(set(res[:k])),
                frac_system_events=float(np.mean(res[:k] == "Siebel")),
                elapsed_h=(tk - t0).total_seconds() / 3600, last_gap_h=float(gaps[-1]),
                mean_gap_h=float(gaps.mean()), max_gap_h=float(gaps.max()),
                start_hour=t0.hour, start_wday=t0.dayofweek, cur_hour=tk.hour, cur_wday=tk.dayofweek,
                impact_changed=int(len(set(imp[:k])) > 1),
            )
            for l in lifecycles:
                r["cnt_lc_" + l.replace(" ", "_")] = int(np.sum(lc[:k] == l))
            for a in acts:
                r["cnt_act_" + a] = int(np.sum(ac[:k] == a))
            recs.append(r)
    X = pd.DataFrame(recs)
    for c in CAT_FEATS:
        X[c] = X[c].astype(str)
    return X


def eligible_prefixes(X, labels, target):
    """Early-warning set: keep prefix k only if the case continues after k (n_events > k)
    and the target outcome has not already happened within the first k events."""
    L = labels[["n_events", target, target + "_pos"]]
    M = X.join(L, on="case")
    pos = M[target + "_pos"]
    keep = (M["n_events"] > M["k"]) & (pos.isna() | (pos >= M["k"]))
    M = M[keep].copy()
    y = M[target].astype(int).to_numpy()
    return M.drop(columns=["n_events", target, target + "_pos"]), y
