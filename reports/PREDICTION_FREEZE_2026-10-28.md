# Pre-draw prediction freeze — 2026-10-28

**Frozen at:** 2026-10-28 11:06:13 Europe/Rome  
**Data cutoff:** 2026-10-27  
**Code revision:** `9b715093cd302f631ff14d7b69cc92962ecd3ef0`  
**Status:** frozen shadow test; not a validated prediction system.

The candidate sets below are recorded before the target draws. Every method will be scored after the result; none may be selected or retuned using these outcomes. This is a research record, not a recommendation to wager.

## VinciCasa — target 2026-10-28

Latest known draw: 2026-10-27, **1–6–8–28–34**. History: 3,390 draws. Uniform expected matches for a 5-number ticket: **0.625**.

| Method | Frozen cinquina |
|---|---|
| Global frequency | **8–10–13–37–40** |
| Recent frequency (20) | **1–9–12–26–35** |
| Anti-hot (20) | **3–10–27–38–40** |
| Exponential decay (τ=10) | **1–25–26–35–36** |
| Overdue-first | **3–10–27–38–40** |
| Transition analogue (overlap≥2, power 3) | **3–11–31–35–40** |
| Gap-trajectory nearest 20 | **14–19–27–35–37** |
| Uniform random, seed 0 | **3–17–25–27–33** |

## SuperEnalotto — target 2026-10-29

Latest known draw: 2026-10-27, **23–34–44–48–64–70**. History: 2,943 draws. Uniform expected matches for a 6-number ticket: **0.400**.

| Method | Frozen sestina |
|---|---|
| Global frequency | **6–45–49–52–79–85** |
| Recent frequency (20) | **18–25–26–28–41–55** |
| Anti-hot (20) | **2–6–7–8–9–15** |
| Exponential decay (τ=10) | **18–34–41–44–55–77** |
| Overdue-first | **9–19–58–87–88–90** |
| Transition analogue (overlap≥2, power 3) | **24–25–69–72–78–86** |
| Gap-trajectory nearest 20 | **1–6–21–32–63–70** |
| Uniform random, seed 0 | **6–34–50–54–63–66** |

## Evaluation rules

1. Do not remove a method because its next result is poor.
2. Record exact matches for every method, including the random control.
3. One or two draws cannot establish an edge. Continue the frozen shadow test across future draws and compare aggregate results with uniform baselines.
4. Any change to a method creates a new version and a new freeze; never overwrite this record.
