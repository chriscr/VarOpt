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

The repository contains the VarOpt platform together with its domain applications.

```text
assets/     Images
docs/       System and technical documentation
domains/    ForgeOpt, NavOpt, and NexaOpt
examples/   VarOpt examples
src/        VarOpt source code
tests/      Platform and cross-domain validation

VarOpt/
¦
+-- README.md
+-- LICENSE
+-- pyproject.toml
+-- .gitignore
¦
+-- assets/
¦   +-- logos/
¦       +-- varopt-logo.png
¦       +-- forgeopt-logo.png
¦       +-- navopt-logo.png
¦       +-- nexaopt-logo.png
¦
+-- docs/
¦   ¦
¦   +-- sds/
¦   ¦   +-- varopt-sds.md
¦   ¦
¦   +-- architecture/
¦   ¦   +-- system-architecture.md
¦   ¦   +-- software-architecture.md
¦   ¦   +-- component-model.md
¦   ¦   +-- architecture-decisions/
¦   ¦       +-- README.md
¦   ¦
¦   +-- science/
¦   ¦   +-- scientific-foundations.md
¦   ¦   +-- mathematical-foundations.md
¦   ¦   +-- model-validation.md
¦   ¦
¦   +-- optimization/
¦   ¦   +-- decision-space.md
¦   ¦   +-- optimization.md
¦   ¦   +-- evaluation.md
¦   ¦   +-- simulation.md
¦   ¦   +-- replanning.md
¦   ¦
¦   +-- development/
¦   ¦   +-- development-guide.md
¦   ¦   +-- testing.md
¦   ¦   +-- contributing.md
¦   ¦
¦   +-- validation/
¦       +-- validation-methodology.md
¦       +-- cross-domain-validation.md
¦       +-- benchmarks.md
¦
+-- src/
¦   ¦
¦   +-- varopt/
¦       ¦
¦       +-- __init__.py
¦       ¦
¦       +-- decision/
¦       ¦   +-- __init__.py
¦       ¦   +-- decision_space.py
¦       ¦   +-- decision_set.py
¦       ¦   +-- decision_variables.py
¦       ¦
¦       +-- optimization/
¦       ¦   +-- __init__.py
¦       ¦   +-- optimizer.py
¦       ¦   +-- objectives.py
¦       ¦   +-- constraints.py
¦       ¦   +-- search.py
¦       ¦
¦       +-- evaluation/
¦       ¦   +-- __init__.py
¦       ¦   +-- evaluator.py
¦       ¦   +-- evaluation_result.py
¦       ¦
¦       +-- simulation/
¦       ¦   +-- __init__.py
¦       ¦   +-- simulator.py
¦       ¦   +-- system_state.py
¦       ¦   +-- simulation_result.py
¦       ¦
¦       +-- performance/
¦       ¦   +-- __init__.py
¦       ¦   +-- performance_model.py
¦       ¦
¦       +-- dynamics/
¦       ¦   +-- __init__.py
¦       ¦   +-- dynamic_system.py
¦       ¦
¦       +-- replanning/
¦       ¦   +-- __init__.py
¦       ¦   +-- replanner.py
¦       ¦   +-- replanning_context.py
¦       ¦
¦       +-- models/
¦       ¦   +-- __init__.py
¦       ¦   +-- domain_model.py
¦       ¦
¦       +-- interfaces/
¦       ¦   +-- __init__.py
¦       ¦   +-- optimizer.py
¦       ¦   +-- evaluator.py
¦       ¦   +-- simulator.py
¦       ¦   +-- performance_model.py
¦       ¦   +-- domain.py
¦       ¦
¦       +-- common/
¦           +-- __init__.py
¦           +-- types.py
¦           +-- time.py
¦           +-- units.py
¦           +-- errors.py
¦
+-- domains/
¦   ¦
¦   +-- forgeopt/
¦   ¦   +-- README.md
¦   ¦   +-- src/
¦   ¦   ¦   +-- forgeopt/
¦   ¦   ¦       +-- __init__.py
¦   ¦   ¦       +-- domain/
¦   ¦   ¦       +-- models/
¦   ¦   ¦       +-- optimization/
¦   ¦   ¦       +-- simulation/
¦   ¦   ¦       +-- performance/
¦   ¦   +-- tests/
¦   ¦   +-- docs/
¦   ¦
¦   +-- navopt/
¦   ¦   +-- README.md
¦   ¦   +-- src/
¦   ¦   ¦   +-- navopt/
¦   ¦   ¦       +-- __init__.py
¦   ¦   ¦       +-- domain/
¦   ¦   ¦       +-- models/
¦   ¦   ¦       +-- optimization/
¦   ¦   ¦       +-- simulation/
¦   ¦   ¦       +-- performance/
¦   ¦   +-- tests/
¦   ¦   +-- docs/
¦   ¦
¦   +-- nexaopt/
¦       +-- README.md
¦       +-- src/
¦       ¦   +-- nexaopt/
¦       ¦       +-- __init__.py
¦       ¦       +-- domain/
¦       ¦       +-- models/
¦       ¦       +-- optimization/
¦       ¦       +-- simulation/
¦       ¦       +-- performance/
¦       +-- tests/
¦       +-- docs/
¦
+-- tests/
¦   ¦
¦   +-- unit/
¦   ¦   +-- decision/
¦   ¦   +-- optimization/
¦   ¦   +-- evaluation/
¦   ¦   +-- simulation/
¦   ¦   +-- performance/
¦   ¦   +-- replanning/
¦   ¦
¦   +-- integration/
¦   ¦   +-- optimization/
¦   ¦   +-- simulation/
¦   ¦   +-- replanning/
¦   ¦
¦   +-- cross_domain/
¦   ¦   +-- forgeopt/
¦   ¦   +-- navopt/
¦   ¦   +-- nexaopt/
¦   ¦
¦   +-- validation/
¦       +-- reference_problems/
¦       +-- benchmarks/
¦       +-- regression/
¦
+-- examples/
¦   +-- basic/
¦   +-- optimization/
¦   +-- dynamic/
¦   +-- cross_domain/
¦
+-- scripts/
    +-- development/
    +-- validation/
    +-- benchmarking/
```

## Contributing

Development practices, contribution guidelines, architectural decisions, and project governance will be documented as the project matures.

## License

The project license will be established before the first public software release.

## Maintainer

VarOpt is developed and maintained by Chris Romero.

```
```
