# rqm-notebooks

**rqm-notebooks** is the interactive demonstration layer of the RQM ecosystem. It provides polished, pedagogical Jupyter notebooks that teach quaternion intuition, Bloch sphere interpretation, SU(2) rotations, and Qiskit-backed quantum workflows — all grounded in `rqm-core` as the canonical math layer.

---

## Ecosystem Architecture

```
rqm-core  ──►  rqm-qiskit  ──►  rqm-notebooks
   │                │                  │
   │  Quaternions   │  Qiskit bridge   │  Interactive demos
   │  Spinors       │  Circuit exec    │  Notebooks
   │  Bloch math    │  IBM integration │  Visualisations
   │  SU(2) ops     │                  │  Pedagogical guides
```

| Layer | Role |
|---|---|
| **rqm-core** | Source of truth for all quaternion, spinor, Bloch sphere, and SU(2) mathematics |
| **rqm-qiskit** | Execution bridge — translates rqm-core types into Qiskit circuits and results |
| **rqm-notebooks** | Interactive demonstration layer — imports from both, adds only display helpers |

---

## Notebook Learning Path

| Notebook | Topic |
|---|---|
| `00_welcome_and_repo_map.ipynb` | Orientation — what is this repo and how to navigate it |
| `01_quaternion_intuition.ipynb` | Building quaternion intuition from first principles |
| `02_spinor_to_bloch.ipynb` | From spinors to the Bloch sphere |
| `03_su2_rotations_and_geometry.ipynb` | SU(2) rotations and their geometric meaning |
| `04_rqm_core_as_source_of_truth.ipynb` | rqm-core as the canonical math layer |
| `05_rqm_qiskit_single_qubit_workflows.ipynb` | Single-qubit workflows via rqm-qiskit |
| `06_simulator_measurements.ipynb` | Simulator-first measurement workflows |
| `07_state_preparation_and_visual_checks.ipynb` | State preparation and visual verification |
| `08_gate_composition_as_geometry.ipynb` | Gate composition viewed as geometry |
| `09_ibm_ready_path.ipynb` | IBM hardware-ready examples |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch JupyterLab
jupyter lab notebooks/
```

---

## Repository Layout

```
rqm-notebooks/
├── notebooks/          # Pedagogical Jupyter notebooks
├── helpers/            # Lightweight display/plotting utilities (no canonical math)
│   ├── plotting.py
│   ├── notebook_style.py
│   └── display_utils.py
├── tests/              # Smoke tests — dependency imports and notebook structure
├── .github/workflows/  # CI: smoke-test on every push
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Architectural Rules

- **rqm-core** owns all math. Notebooks must not reimplement quaternion, spinor, Bloch, or SU(2) logic.
- **rqm-qiskit** owns circuit execution. Notebooks call its API, not raw Qiskit directly.
- **helpers/** contains only display/formatting utilities — no canonical math.
- No IBM hardware dependency is required to run any notebook by default.

---

## Running Tests

```bash
pytest tests/
```

---

## License

MIT — see [LICENSE](LICENSE).
