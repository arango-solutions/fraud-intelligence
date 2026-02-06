## Demo rehearsal checklist (Visualizer + app)

### 0) Pre-flight

- [ ] `MODE=REMOTE` configured locally (do not paste `.env`).
- [ ] All phases run:

```bash
python scripts/test_phase1.py --remote-only --install-visualizer
python scripts/test_phase2.py --remote-only
python scripts/test_phase3.py --remote-only
```

### 1) Visualizer: Investigator flow

- [ ] Open Visualizer → select **KnowledgeGraph**
- [ ] Search & add node: `Victor Tella` (Person, synthetic alias)
- [ ] Select Person → run **`[Person] Expand Relationships`**
- [ ] Confirm at least one `BankAccount` appears via `hasAccount`
- [ ] Right-click a `BankAccount` → run **`[BankAccount] Find cycles (AQL)`**
- [ ] Confirm a cycle path is returned (start/end is the same account)

### 2) Reports: Analyst flow

- [ ] Open `docs/phase3-analytics-report.md` and confirm cycle/mule/undervalued counts are non-zero
- [ ] Spot-check risk fields exist on a few entities (`riskScore`, `riskReasons`)

### 3) Streamlit: Executive flow (optional)

- [ ] Run:

```bash
streamlit run apps/phase3_demo_app.py
```

- [ ] Investigator tab: entity search works and shows risk fields
- [ ] Analyst tab: pattern stats are visible
- [ ] Executive tab: district summary renders

