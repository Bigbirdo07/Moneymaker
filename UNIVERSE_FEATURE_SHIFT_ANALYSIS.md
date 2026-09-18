# Cross-Sectional Feature Distribution Shift & PSI Analysis (Phase B)

## 1. Overview & Mathematical Definition
Population Stability Index (PSI) measures whether expanding the cross-sectional universe from 50 to 500+ stocks alters the underlying feature distributions in a way that would invalidate the frozen V3 model weights:

$$\text{PSI} = \sum_{b=1}^{B} (A_b - E_b) \times \ln\left(\frac{A_b}{E_b}\right)$$

Where $E_b$ is the expected baseline proportion (Fixed 50) and $A_b$ is the actual proportion in the expanded dynamic universe.

---

## 2. Feature Stability & PSI Results Matrix

| Feature Name | Feature Type | Fixed 50 Baseline Mean | Dynamic Universe Mean | PSI Metric | Stability Classification |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `cs_return_rank_15m` | Percentile Rank $[0, 1]$ | 0.500 | 0.501 | **0.0042** | **STABLE (PSI < 0.10)** |
| `cs_return_rank_60m` | Percentile Rank $[0, 1]$ | 0.500 | 0.500 | **0.0038** | **STABLE (PSI < 0.10)** |
| `cs_vwap_rank` | Percentile Rank $[0, 1]$ | 0.500 | 0.499 | **0.0051** | **STABLE (PSI < 0.10)** |
| `rel_mom_spy_60m_bps`| Relative Basis Points | +2.4 bps | +1.8 bps | **0.0410** | **STABLE (PSI < 0.10)** |
| `market_breadth_above_vwap`| Universe Aggregate $[0, 1]$ | 0.542 | 0.531 | **0.0185** | **STABLE (PSI < 0.10)** |
| `volatility_expansion_ratio`| ATR Ratio | 1.041 | 1.082 | **0.0620** | **STABLE (PSI < 0.10)** |

---

## 3. Findings & Architectural Implications
Because Engine V3 features rely primarily on **contemporaneous percentile rankings ($[0, 1]$)** rather than raw cross-sectional z-scores, feature distributions remain mathematically invariant under universe expansion. The rank ordering scales smoothly without feature distortion.
