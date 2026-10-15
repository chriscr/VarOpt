# VarOpt

> **Domain-Agnostic Optimization Platform**

<!--
Logo
Proposed location:
assets/logos/varopt-logo.png

When the logo asset is available, use:

![VarOpt](assets/logos/varopt-logo.png)
-->

![VarOpt](assets/logos/varopt-logo.png)

## Overview

**VarOpt** is a domain-agnostic optimization platform for optimizing decisions in complex systems.

The platform is designed around a separation between:

* the decisions being optimized;
* the system state and dynamics affected by those decisions;
* simulation and evaluation of candidate decisions;
* performance models that determine how a system responds;
* optimization methods that search the decision space; and
* dynamic optimization and replanning as system conditions evolve.

VarOpt is intended to support both static and dynamic optimization problems while maintaining clear boundaries between optimization, simulation, system modeling, and domain-specific concerns.

## Domain Applications

VarOpt is developed and validated through multiple domain applications. These applications provide concrete implementations and increasingly demanding test cases for the underlying platform.

| Domain       | Focus                                       | Initial Reference Application |
| ------------ | ------------------------------------------- | ----------------------------- |
| **ForgeOpt** | Manufacturing Optimization                  | Spacecraft Manufacturing      |
| **NavOpt**   | Navigation & Voyage Optimization            | Maritime Voyage Optimization  |
| **NexaOpt**  | Networked & Distributed-System Optimization | Energy Grid Operations        |

The domain applications are intentionally broader than their initial reference problems.

### ForgeOpt

**ForgeOpt** applies VarOpt to manufacturing systems, with spacecraft manufacturing as the initial reference domain.

[ForgeOpt README](domains/ForgeOpt/README.md)

### NavOpt

**NavOpt** applies VarOpt to navigation and voyage optimization. Maritime voyage optimization is the initial reference domain, while the architecture is intended to support other navigation and routing problems.

[NavOpt README](domains/NavOpt/README.md)

### NexaOpt

**NexaOpt** applies VarOpt to networked and distributed systems. Energy grid operations provide the initial reference domain, while the architecture is intended to support other networked physical systems, including water and resource-distribution networks.

[NexaOpt README](domains/NexaOpt/README.md)

## Platform Architecture

The fundamental architectural relationship is:

```text
                         VarOpt
             Domain-Agnostic Optimization
                         Platform
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
      ForgeOpt           NavOpt           NexaOpt
   Manufacturing     Navigation/Voyage   Networked/
     Systems             Systems        Distributed Systems
          |                 |                 |
          v                 v                 v
 Spacecraft Manufacturing  Maritime       Energy Grid
                           Voyages        Operations
```

The domain applications are not independent optimization platforms. They are domain implementations and validation environments built around the VarOpt platform.

## Core Concepts

The VarOpt architecture includes concepts such as:

* **Decision Space**
* **Candidate Decision Set**
* **Optimization**
* **Evaluation**
* **Simulation**
* **Performance Model**
* **System State**
* **Dynamic Optimization**
* **Replanning**
* **Constraints**
* **Objectives**
* **Domain Models**

The detailed definitions and architectural relationships are maintained in the VarOpt System Definition Specification (SDS).

## Documentation

The authoritative system definition is maintained in:

[VarOpt SDS](docs/sds/VarOpt_Phase_0_SDS.md)

Additional documentation will be developed as the implementation matures, including:

* System architecture
* Software architecture
* Domain integration
* Scientific foundations
* Mathematical foundations
* Requirements
* Architecture decisions
* Validation methodology

## Development Status

**Current status: Architecture and foundation phase**

The VarOpt system definition has been established before beginning substantial implementation.

The project is being developed incrementally, with architectural decisions and domain abstractions established before implementation details are committed.

## Design Philosophy

VarOpt is intended to remain domain-agnostic through explicit architectural boundaries rather than through excessive abstraction.

The platform should provide common optimization capabilities without assuming that every domain uses:

* the same optimization algorithm;
* the same simulation method;
* the same evaluator;
* the same mathematical formulation;
* the same state representation; or
* the same execution architecture.

Domain independence will be demonstrated through application across substantially different problem classes.

## Repository Organization

VarOpt uses a Python `src/` package layout. The repository separates the domain-agnostic optimization platform from experimental optimization approaches, automated tests, and phase-specific documentation.

The implementation is developed incrementally. Completed phases establish a tested baseline, while experiments are kept separate from the core platform unless their general applicability and architectural role justify further integration.

### Repository Structure

```text
VarOpt/
├── README.md
├── LICENSE
├── pyproject.toml
│
├── src/
│   └── varopt/
│       ├── core/
│       │   ├── candidate.py
│       │   ├── callable_evaluation.py
│       │   ├── constraint.py
│       │   ├── decision_space.py
│       │   ├── evaluation.py
│       │   ├── evaluation_result.py
│       │   ├── objective.py
│       │   ├── optimizer.py
│       │   └── problem.py
│       │
│       └── experiments/
│           ├── hill_climbing_experiment.py
│           ├── multi_start_experiment.py
│           ├── simulated_annealing_experiment.py
│           └── inventory_evaluation_experiment.py
│
├── tests/
│   ├── core/
│   └── experiments/
│
└── docs/
    ├── phase_5/
    │   └── VarOpt_Phase_5_Inventory_Experiment.md
    │
    └── sds/
        └── VarOpt_Phase_0_SDS.md
```

*The tree above identifies the known core modules and experimental components. It is a logical overview rather than an exhaustive file listing; additional files and directories should be included only after verifying them against the remote repository.*

### Core Platform — `src/varopt/core/`

The core package implements the foundational optimization contracts:

- **Problem definition:** Represents an optimization problem and its decision space.
- **Candidate decisions:** Represents the decisions being evaluated.
- **Objectives and constraints:** Defines optimization direction and decision eligibility.
- **Evaluation:** Evaluates candidate decisions and represents evaluation results.
- **Optimization:** Searches candidate decisions and selects the best eligible result.

These components form the baseline on which further optimization approaches and domain-specific applications can be developed.

### Experimental Approaches — `src/varopt/experiments/`

The experiments investigate alternative optimization strategies and evaluate their behavior without prematurely expanding or changing the core platform.

The repository includes experiments for:

- Hill climbing.
- Multi-start optimization.
- Simulated annealing.
- Deterministic inventory evaluation over a finite planning horizon.

The inventory experiment extends the investigation into dynamic systems, where candidate decisions are evaluated in the context of an evolving system and its operating constraints. Its implementation and supporting documentation remain distinct from the established core optimization contracts.

### Automated Tests — `tests/`

The test suite validates the platform and its experiments.

- **`tests/core/`** contains tests for core optimization behavior and contracts.
- **`tests/experiments/`** contains tests for experimental implementations, including their expected behavior, constraints, and edge cases.

Tests provide evidence that changes preserve established behavior and that experiments operate according to their defined requirements.

### Documentation — `docs/`

Documentation records the system definition, implementation decisions, and phase-specific technical details.

Phase-specific documentation provides traceability between an experiment's purpose, its implementation, and its validation. The Phase 5 inventory experiment is documented in `docs/phase_5/VarOpt_Phase_5_Inventory_Experiment.md`.

### Development Configuration

- **`pyproject.toml`** defines the Python project and its development configuration.
- **`README.md`** provides the project overview, architecture, and development status.
- **`LICENSE`** contains the repository's licensing information.

The repository's organization preserves a clear distinction between established platform capabilities and experimental work, supporting controlled evolution of VarOpt as additional optimization problems and system dynamics are investigated.

## Contributing

Development practices, contribution guidelines, architectural decisions, and project governance will be documented as the project matures.

## License

The project license will be established before the first public software release.

## Maintainer

VarOpt is developed and maintained by Chris Romero.

```
```
