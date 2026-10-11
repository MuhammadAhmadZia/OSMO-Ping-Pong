# Early Warning of Cross-Border Ping-Pong in Offshore Software Maintenance

Replication package for the paper of the same title.
It contains the notebook that produces every result, the source modules, all result tables from the
reported run, the figures and the environment record.

Version 1.0.0. Code licence: MIT (see `LICENSE`). The event log is not redistributed (see Data).

## Data

BPI Challenge 2013, incidents (Volvo IT, VINST system).
W. Steeman, 4TU.ResearchData, 2013, doi:10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee.
Distributed under the 4TU.ResearchData general terms of use.

The notebook downloads the log by itself. It first fetches a public CSV conversion of the same log and
checks its SHA-256 fingerprint
(`76179b9a202f8bfc20d2754bab2152ae7b58ee945dce5d51ac4ad762facd0e94`) and its size (7,554 incidents,
65,533 events). If that copy is unavailable, it downloads the original XES file from 4TU and converts it
with pm4py. No login or credentials are needed.

## Contents

| Path | What it is |
|---|---|
| `notebooks/OSMO_PingPong_Replication.ipynb` | Complete, self-contained Colab notebook; reproduces all tables and figures |
| `src/osmo_core.py` | Log loading, team segments with the sender correction, ping-pong labels, prefix features |
| `src/osmo_validity.py` | Four cross-border definitions, time-varying Cox models, time-band proportionality check |
| `results/` | All result tables (CSV) from the reported run, `RESULTS_SUMMARY.md`, `environment.json`, `progress_log.txt` |
| `figures/` | Figures 1 to 10 as numbered in the paper (PNG, 300 dpi) |
| `tools/make_method_figures.py` | Draws Fig. 1 (study overview) and Fig. 2 (methodology); icons from Font Awesome Free (`pip install fontawesomefree`, CC BY 4.0) |
| `requirements.txt` | Library versions of the reported run |

The notebook embeds the two source modules, so it runs on its own. The modules are included separately for
readers who want to reuse the label and feature code outside Colab.

## How to Reproduce (Google Colab)

1. Open https://colab.research.google.com and choose File > Upload notebook. Select
   `notebooks/OSMO_PingPong_Replication.ipynb`.
2. Keep the default CPU runtime. No GPU is used.
3. Choose Runtime > Run all.
4. When asked, allow the notebook to connect to Google Drive. All outputs are written to
   `MyDrive/OSMO_PingPong_replication/`.
5. The full run takes about 70 to 90 minutes on the free Colab CPU (the reported run took 77 minutes).
   Every fold, model and table is saved the moment it finishes. If the session disconnects, reconnect and
   choose Run all again; finished work is skipped.
6. At the end, Step 16 zips the results, figures and progress log and downloads the zip. A copy stays in Drive.
   Step 16 can also be run on its own at any time to collect partial results with a `STATUS.md` progress report.

Set `FAST_MODE = True` in Step 1 for a short check run (1 repeat, 3 folds, about 10 minutes).

To run outside Colab, install the packages in `requirements.txt`, set the environment variable `OSMO_BASE`
to an output folder, and execute the notebook with Jupyter.

## Where Each Paper Result Comes From

| Paper item | Result file |
|---|---|
| Table 2 | `T0a_segment_ambiguity.csv` |
| Table 3 | `T0b_label_definitions.csv`, `T0c_definition_overlap.csv` |
| Table 6 | `T1_prevalence_naive_cost.csv` |
| Table 7, Fig. 5 | `T1c_cox_time_varying.csv` |
| Time-band hazard ratios (Section 5.2) | `T1d_cox_time_bands.csv` |
| Section 5.1 country pairs, Fig. 3 | `T2_country_pairs.csv` |
| Section 5.1 opening hour, Fig. 4 | `T3_rate_by_start_hour.csv` |
| Section 5.1 first handler country | `T4_rate_by_first_country.csv` |
| Section 5.2 opening month | `T4b_rate_by_opening_month.csv` |
| Table 8 | `T5_cv_results.csv`, `T13_overfitting_gap.csv` |
| Significance tests (Section 5.3) | `T7_significance.csv`, `T7b_tuning_choices.csv` |
| Fig. 6 | `T6_per_prefix.csv` |
| Fig. 7 | `T12_common_cohort.csv` |
| Table 9, Fig. 8 | `T11_operating_point_k1.csv` (Fig. 8 is drawn from the saved fold predictions) |
| Table 10 | `T14_robustness.csv` |
| Table 11 | `T8_temporal_split.csv` |
| Fig. 9 | `T9_shap_importance_xpp.csv`, `T9_shap_by_*.csv` |
| Table 12, Fig. 10 | `T10_deployment_cost.csv` |
| Fold-level and per-prefix metrics | `fold_metrics.csv`, `per_prefix_metrics.csv` |

Tables 1, 4 and 5 describe related work, features and model settings and have no result file.

Figure files in `figures/` follow the paper numbering. The notebook writes the same plots under its own names:
Fig. 3 `fig1_country_pairs.png`, Fig. 4 `fig3_rate_by_hour.png`, Fig. 5 `fig2_cox_hazard_ratio.png`,
Fig. 6 `fig4_auc_by_prefix.png`, Fig. 7 `fig8_common_cohort.png`, Fig. 8 `fig5_alert_budget.png`,
Fig. 9 `fig6_shap.png`, Fig. 10 `fig7_latency.png`.

## Method in Brief

- Team segments are runs of consecutive events handled by one support team. The event that opens a new
  segment is usually logged under the person who sent the incident, so it is left out when the receiving
  segment's country is decided (`_is_sender_event` in `osmo_core.py`).
- Team ping-pong: an incident returns to a team it had already left. Cross-border ping-pong (D1): the country of
  a returning segment differs from the country of the segment immediately before it. Three alternative
  definitions (D2 team home country, D3 dominant country, D5 handler to handler) are in `osmo_validity.py`.
- Early-warning prefixes of 1 to 10 events are kept only while the outcome is still in the future; each prefix
  is encoded with 44 features known at that point.
- Eleven models are compared with stratified, incident-grouped 5-fold cross-validation repeated three times.
  LightGBM and XGBoost are tuned on an inner incident-grouped split of each training fold.
- Resolution time is analysed with Cox models in which ping-pong is a time-varying exposure, with a
  proportionality check by time band.

## Reproducibility Notes

- Labels, features, folds and tuning choices are deterministic for a given library version.
- The reported run and a second run on another machine agreed within 0.007 in cross-validated AUC. Small
  differences come from library versions.
- `T1d_cox_time_bands.csv` was produced with the same notebook code and the same statsmodels version (0.15.0)
  as the other tables; the Cox models do not depend on any random state.
- Latency and throughput depend on hardware and varied between Colab sessions; they are meant for comparing
  models with each other, not as absolute targets.

## Maintainer

Muhammad Ahmad Zia, Department of Computer Science & IT, The University of Lahore, Pakistan.
Website: [ahmadzia.com](https://ahmadzia.com) · ORCID: [0000-0002-3208-6246](https://orcid.org/0000-0002-3208-6246) · Email: muhammad.zia@cs.uol.edu.pk

Questions and issue reports about this package are welcome through the repository's issue tracker or by email.
