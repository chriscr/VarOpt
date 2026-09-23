# VarOpt — Phase 0 System Definition Specification (SDS)

**Document status:** LOCKED — Architectural Baseline  
**Phase:** Phase 0 — Architecture  
**Source of truth:** The locked SDS established in the conversation. This Markdown file is an external representation of that source of truth.

## Status Legend

- **LOCKED** — Established architectural decision currently governing the design
- **PROPOSED** — Deliberate candidate decision under review
- **WORKING HYPOTHESIS** — Useful assumption guiding development but not yet established architecture
- **OPEN** — Unresolved architectural question
- **EXPERIMENTAL** — Capability or approach being explored for evidence
- **DEFERRED** — Deliberately postponed pending future requirement/evidence
- **FUTURE CONCEPT** — Idea retained for possible future investigation

## Consolidated Baseline Clarifications

1. Section 5 conceptual vocabulary and Section 14 runtime execution concepts are distinct.
2. Section 10 defines dynamic optimization/replanning semantics; Section 14 defines runtime consequences.
3. Architectural boundary ≠ conceptual responsibility ≠ abstraction/contract ≠ implementation component.
4. Information authority, organizational ownership, operational authority, and access authorization are distinct concepts.
5. Scientific/domain validation (Section 15) is distinct from architectural validation (Section 20).
6. Section 7 is canonical for core abstraction definitions; Section 9 defines optimization/evaluation behavior and relationships.
7. Execution traceability contributes to broader provenance; provenance is not reducible to execution logging.
8. Significant architectural decisions should, where applicable, be traceable to requirements, intended use, architectural questions, evidence, or rationale.
9. Minimum executable problem definition remains a Phase 1 design question; no universal schema is locked in Phase 0.
10. Future concepts and stress-test domains are not silently promoted into core architecture.

## Section 1 — Purpose and System Vision — LOCKED

- Domain-agnostic optimization framework supporting static and dynamic optimization where practical.
- Dynamic systems are a central motivation and architectural stress test, not a mandatory characteristic of every core abstraction.
- Primary reference domain: Manufacturing — Spacecraft Manufacturing; ForgeOpt remains the manufacturing project name.
- Reference/stress-test domains: Maritime — Voyage Optimization and Energy — Grid Operations.
- Detailed abstractions, interfaces, implementation mechanisms, and technology choices remain subject to subsequent validation.
- The platform is an optimization framework, not a universal scientific simulation platform, domain modeling framework, or operational execution system.

## Section 2 — Architectural Principles — LOCKED

- **AP-001 — Domain Independence**
- **AP-002 — Problem-Class Flexibility**
- **AP-003 — Separation of Concerns**
- **AP-004 — Explicit Architectural Boundaries**
- **AP-005 — Dependency Inversion**
- **AP-006 — Separation of Optimization and Evaluation**
- **AP-007 — Evaluation Mechanism Independence**
- **AP-008 — Solver Independence**
- **AP-009 — Explicit Constraints and Objectives**
- **AP-010 — Separation of Performance Models from Optimization**
- **AP-011 — Simulation Independence**
- **AP-012 — Preserve Domain-Specific Mathematics**
- **AP-013 — Replaceability Through Explicit Contracts**
- **AP-014 — Incremental Architectural Complexity**
- **AP-015 — Discover Commonality Through Implementation**
- **AP-016 — Testability and Validation**
- **AP-017 — Reproducibility and Traceability**
- **AP-018 — Performance Must Be Measured**

## Section 3 — System Scope and Capability Boundaries — LOCKED

Core capabilities include optimization problem representation, decision-space representation, candidate generation/search, candidate evaluation, constraints/objectives, performance models, simulation integration, optimization results, traceability/reproducibility, dynamic optimization, replanning, and uncertainty/stochastic methods accommodation.

Domain-specific physics remains in domain implementations or external systems where appropriate.

Not core: universal simulation engine; universal optimization solver; operational control systems; enterprise data infrastructure; visualization framework.

**Scope boundary:** The Optimization Platform is an optimization framework, not a universal scientific simulation platform, domain modeling framework, or operational execution system.

## Section 4 — Conceptual System Model — LOCKED

Canonical vocabulary:

- Optimization Problem
- Decision Space
- Candidate Decision
- Constraint
- Objective
- Evaluation
- Performance Model
- Simulation
- Evaluation Result
- Optimization Result
- Domain Context

Fundamental relationship:

> Optimizer → Candidate → Evaluation → Evaluation Result → Optimizer → Next Candidate → …

Domain Context surrounds the optimization process and provides information needed by problem definition, decision space, constraints, objectives, performance models, evaluation, and simulation.

Static and dynamic optimization are both supported without requiring state, environment, observations, or simulation in every case.

A Performance Model may conceptually map:

> Performance = F(State, Decision, Environment, Parameters)

Evaluation Result may contain feasibility, constraint results, objectives, metrics, simulation outputs, uncertainty, diagnostics, and provenance as relevant.

Optimization Result represents the outcome of the optimization process, including selected candidates, feasibility/objective information, alternatives/tradeoffs, termination information, and provenance as relevant.

## Section 5 — Conceptual Relationships and Responsibilities — LOCKED

- Optimization Process is an explicit conceptual concept covering candidate generation, evaluation, iteration, and optimization result.
- State and Environment are supporting concepts, especially for dynamic optimization, but are not mandatory for static optimization.
- Observation and Information are distinct supporting concepts; acquisition, processing, estimation, and assimilation are not core responsibilities at this stage.
- Execution Context is deliberately not part of the core conceptual vocabulary; runtime execution concepts are defined later in Section 14.
- Relevant time, uncertainty, and provenance shall be accommodated where they affect results.
- Replanning reuses the same core conceptual relationships.
- Exact boundaries and contracts are defined in Section 6.

## Section 6 — Architectural Boundaries — LOCKED

Conceptual boundaries:

1. Domain ↔ Optimization
2. Problem Definition ↔ Optimization Process
3. Optimization ↔ Evaluation
4. Platform ↔ External Systems
5. Evaluation ↔ Performance Model
6. Evaluation ↔ Simulation
7. Evaluation Result ↔ Optimization Result

State/Environment/Observation/Information remain supporting concepts outside core acquisition/estimation responsibility.

Traceability is cross-cutting rather than a dedicated layer.

Conceptual regions:

> Domain Region → Domain Boundary → Optimization Definition → Optimization Boundary → Optimization Process → Evaluation Boundary → Evaluation → Results & Traceability

**Architectural boundary ≠ conceptual responsibility ≠ abstraction/contract ≠ implementation component.**

## Section 7 — Core Abstractions and Contracts — LOCKED

Core responsibilities:

1. Optimization Problem
2. Decision Space
3. Candidate Decision
4. Constraints and Objectives
5. Optimization Method
6. Evaluation
7. Evaluation Result
8. Performance Model
9. Simulation
10. Optimization Result
11. Domain Integration
12. Traceability/provenance

Candidate representability is distinct from feasibility.

Evaluation failure is distinct from infeasibility.

Batch evaluation is accommodated but not mandatory.

Method-specific capabilities may be optional; avoid a universal interface.

Exact interfaces, schemas, APIs, modules, and technologies remain open.

## Section 8 — Dependency Structure — LOCKED

- Methods depend on problem abstractions and required capabilities, not concrete domain implementations.
- Candidate evaluation occurs through an explicit boundary.
- Problem definition is independent of optimization method.
- Results cross boundaries through explicit contracts.
- Domain implementations depend inward through abstractions.
- Evaluation may depend on performance models/simulation; those do not depend on evaluation by default.
- Preserve domain mathematics.
- External systems interact through explicit boundaries.
- Traceability crosses dependency boundaries.
- Supporting information does not imply ownership or production responsibility.

Conceptual dependency does not imply a runtime call, direct reference, compile-time dependency, package, process, service, or deployment separation.

## Section 9 — Optimization and Evaluation Architecture — LOCKED

- Methods own search strategy.
- Method capabilities vary.
- No universal search lifecycle.
- Method selection is problem/capability dependent.
- Evaluation determines candidate properties.
- Optimization proceeds through iterative feedback.
- Evaluation mechanisms are replaceable where meaningful.
- Evaluation can combine mechanisms.
- Constraint and objective assessment remain distinct.
- Feasibility is not assumed.
- Evaluation failure is distinct from infeasibility.
- Evaluation results retain semantic meaning.
- Batch/parallel evaluation is optional.
- Evaluation execution occurs behind an architectural boundary.
- Fidelity and computational cost may affect optimization strategy.
- Termination has process-level and method-specific aspects.

No solver, algorithm, synchronous/asynchronous model, result schema, or multi-fidelity strategy is locked here.

## Section 10 — Dynamic Optimization and Replanning — LOCKED

- Dynamic optimization accommodates changing conditions.
- State and environment provide contextual inputs where relevant.
- Observations and information may update context.
- Replanning reuses the existing optimization process.
- Replanning may modify the existing problem.
- A changed problem may be a materially different problem class.
- Architectural continuity does not require problem-class continuity.
- Decision Space may change.
- Decision continuity is not universal.
- Partially committed decisions are supported.
- Multiple replanning triggers are accommodated.
- Replanning need not be continuous.
- Timing and computational time are distinct considerations.
- Dynamic evaluation may use current/predicted conditions without simulation.
- Trajectory candidates are accommodated.
- Rolling/receding horizon is allowed but no mandatory Horizon abstraction is established.
- Replanning history shall remain traceable.

Initial implementation shall not introduce generalized arbitrary problem-class transition machinery, a universal ProblemClass hierarchy, automatic transition detection, migration/transformation, cross-problem orchestration, or a universal meta-optimizer unless demonstrated need exists.

## Section 11 — Uncertainty, Stochasticity, and Robustness — LOCKED

- Uncertainty may matter anywhere in the architecture.
- No universal uncertainty representation is required.
- Possible forms include intervals, bounds, distributions, random variables, stochastic processes, samples, ensembles, scenarios, empirical distributions, and domain-specific forms.
- Accommodate exogenous and model-intrinsic uncertainty.
- Preserve dependence/correlation where material.
- Deterministic operation remains first-class.
- Uncertainty shall be composable without forcing it into every core concept.
- Evaluation may be deterministic or stochastic.
- Repeated evaluation is supported.
- Evaluation Results may represent uncertain outcomes.
- Stochastic evaluation is not synonymous with simulation.
- Reproducibility information shall be retained for stochastic processes.
- Stochastic variability is distinct from failure, infeasibility, and constraint violation.
- Optimization may use uncertainty information.
- Robustness is distinct from feasibility.
- Sensitivity analysis is optional.
- Robustness is problem/domain dependent.
- Multiple uncertainty treatments may coexist.
- Robustness analysis may occur inside or outside optimization.

**Key principle:** The Optimization Platform provides architectural capability for uncertainty without imposing a universal uncertainty framework.

## Section 12 — Domain Adaptation and Integration — LOCKED

- Core remains independent of concrete domains.
- Integration translates meaning, not necessarily structure.
- Domain adaptation may be required but is not assumed to be a separate component.
- Preserve semantic meaning including units, frames, time, validity, and physical interpretation.
- Integration need not be symmetric.
- Multi-domain problems are supported without collapsing domains.
- Domain-specific mathematics remains outside core unless demonstrated commonality.
- Domain integrations may provide performance models.
- Multiple specialized models may compose.
- External scientific/computational systems are allowed.
- Fidelity/model selection remains domain/problem responsibility where appropriate.
- Domain-specific outputs may cross the boundary.
- Integration does not imply ownership.
- **Ownership ≠ Provision ≠ Adaptation ≠ Use.**
- Cross-domain validation influences architectural evolution.
- No universal domain adapter is assumed.

Authority clarification:

- Information authority
- Organizational ownership
- Operational authority
- Access authorization

are distinct concepts.

**Central pattern:** Common architectural boundary, variable domain implementation, preserved domain meaning, distributed ownership.

## Section 13 — Data, Results, Provenance, and Traceability — LOCKED

### Information and Data Semantics

- Information retains semantic meaning.
- No universal representation is prescribed.
- Semantic requirements are distinct from representation.
- Relevant context accompanies information.
- Domain-specific information may cross boundaries.
- Production, transformation, and consumption do not imply ownership.
- Information identity/context is supported where materially relevant.

### Results and Provenance

- Evaluation Result ≠ Optimization Result.
- Meaningful relationships are preserved.
- Provenance is more than logging.
- Reproducibility is supported.
- Stochastic traceability is supported.
- Replanning history is retained.
- Provenance crosses boundaries.
- Granularity is purpose-dependent.
- **Provenance shall support contribution and dependency relationships.**
- This does not imply formal causal inference.

### Lifecycle and Authority

- Distinguish authoritative, derived, and optimization information.
- Distinguish current and historical information.
- Derived information shall not be mistaken for authoritative information.
- Distinguish transient and persistent information.
- Retention is purpose-dependent.
- External data dependencies are identifiable.
- Lifecycle does not imply ownership.
- No storage technology is prescribed.

**Key principle:** The platform operates on information whose semantic meaning, context, provenance, authority, derivation, temporal status, lifecycle, and relevant dependencies must be preserved where they materially affect optimization, evaluation, reproducibility, validation, or traceability.

## Section 14 — Execution, Orchestration, and Runtime Architecture — LOCKED

### Area A — Optimization Process Execution

ORE-001–ORE-010 establish execution progression, method-controlled search, evaluation feedback, distinguishable execution state, execution isolation, configuration/semantics distinction, interruption/suspension/cancellation, termination vs failure, completion vs mathematical optimality, and execution traceability.

### Area B — Evaluation Execution and Coordination

ORE-011–ORE-029 establish an explicit evaluation boundary, encapsulated evaluation execution, candidate/context association, individual or multiple candidate evaluation, optional concurrency, no universal ordering, resource requirements, cost/latency/fidelity information, resource limits, representable failure, cancellation, external computational capabilities, changing external availability, multiple outcomes, reproducibility, changing evaluation context, and execution-model flexibility.

### Area C — Dynamic Execution and Replanning

ORE-030–ORE-047 establish changing context, distinction between context changes and execution events, treatment of pending evaluations, replanning through the existing architecture, updated or materially changed problems, no generalized transition machinery initially, partially committed decisions, no universal decision correspondence, preservation of relationships, multiple triggers, non-continuous replanning, timing vs computational time, context preservation, reuse/invalidation of prior results where applicable, continuation or restart, and traceability.

### Area D1 — Runtime Resources

- **ORE-048 — Runtime Resource Requirements**
- **ORE-049 — Resource Availability**
- **ORE-050 — Resource Requirements Are Not Universal**

### Area D2 — Execution Isolation and Concurrency

- **ORE-051 — Execution State Isolation**
- **ORE-052 — Concurrency Is Capability, Not Architecture**

**Isolation is an architectural requirement; concurrency is an optional capability.**

### Area D3 — External Computational Capabilities

- **ORE-053 — External Computational Capabilities**
- **ORE-054 — External Execution Characteristics**

External capabilities may include simulation libraries/tools, specialized solvers, engineering software, and numerical/scientific tools. They may also serve as verification, validation, or benchmark references without becoming part of the core architecture.

### Runtime Guardrail

> The initial implementation shall favor the simplest runtime architecture that satisfies demonstrated requirements. Future scaling from local development to hosted and, if justified, cloud infrastructure shall be treated as an architectural evolution rather than a Phase 0 assumption.

Intended progression:

> Laptop → hosted environment for a small number of users → larger/cloud infrastructure only when demonstrated requirements justify it.

No implicit requirement exists for distributed computing, microservices, queues, worker pools, Kubernetes, or cloud-native infrastructure.

**Cross-reference:** Section 5 defines conceptual vocabulary; Section 14 defines runtime realization. Section 10 defines dynamic optimization/replanning semantics; Section 14 defines runtime consequences.

## Section 15 — Testing, Validation, and Verification — LOCKED

Foundational distinction:

> **Software verification, numerical/mathematical verification, and domain/scientific validation are related but different activities.**

### Software Testing and Architectural Verification

TVV-001–TVV-004 establish testable software behavior, verifiable architectural contracts, practical independent testing, and avoidance of unnecessary architecture solely for testing.

### Mathematical and Numerical Verification

TVV-005–TVV-008 establish verifiable mathematical formulations, verification of numerical implementations against mathematical expectations, characterization of numerical error and limitations, and independent verification where appropriate.

### Domain and Scientific Validation

TVV-009–TVV-012 establish validation against appropriate references, distinction from software verification, scope matching intended use, and visibility of assumptions and limitations.

### Reproducibility, Benchmarking, and Evidence

TVV-013–TVV-016 establish traceable evidence, benchmark problems, use of external tools as verification/benchmark references, and evidence proportionate to significance.

**Clarification:** Scientific/domain validation validates models and results against appropriate domain references. Architectural validation evaluates whether platform assumptions, abstractions, boundaries, responsibilities, and contracts remain appropriate across different problems and domains.

## Section 16 — Technology Architecture — LOCKED

### Technology Selection Principles

TA-001–TA-008 establish technology as support for architecture, requirements-driven selection, incremental complexity, practical technology independence, deliberate external dependencies, measured performance, meaningful replaceability, and preservation of scientific/domain semantics.

### Core Implementation Technology

TB-001–TB-007 establish:

- Python-first initial primary language.
- Core logic should not be unnecessarily coupled to frameworks.
- Additional languages/runtimes may be introduced when justified.
- Portability and dependency management matter.
- Core capability is distinguished from supporting infrastructure.

### Mathematical, Numerical, and Optimization Technology

TC-001–TC-008 establish mathematical independence, explicit numerical methods where material, replaceable optimization methods, external library integration, possible internally developed mathematics where meaningful, preservation of domain semantics, verification support, and advanced numerical technologies when justified.

### Simulation and External Computational Integration

TD-001–TD-008 establish explicit boundaries, external tools not defining core architecture, multiple computational mechanisms, optional simulation, representation of external characteristics, use of external tools as independent references, semantic preservation, and meaningful replaceability.

### Data, Persistence, and Provenance Technology

TE-001–TE-008 establish support for information semantics, non-universal representation, purpose-driven persistence, transient/persistent distinction, provenance, authority/derivation distinction, external dependency identification, and evolution.

### Interfaces and Integration Technology

TF-001–TF-008 establish interfaces as implementations of contracts, mechanism selection by requirement, core independence from specific interface technology, explicit external boundaries, semantic preservation, evolution, measured performance, and coexistence of multiple mechanisms.

### Development, Testing, and Scientific Validation Tooling

TG-001–TG-008 establish architectural verification, scientific/numerical verification, domain validation, benchmarking/profiling, regression, reproducible environments, reference implementations/external tools, and avoidance of unnecessary development architecture.

### Runtime, Deployment, and Technology Evolution

TH-001–TH-008 establish simple initial runtime, deployment evolution with requirements, no assumed distributed technology, runtime support for isolation, appropriate concurrency, observable performance/resource use, preserved contracts, and cloud only when justified.

## Section 17 — Scalability and Performance — LOCKED

**Central principle:** Scale and performance are properties to be measured and characterized, not assumptions to be designed around prematurely.

Eight areas:

1. Performance and Scalability Principles
2. Problem and Workload Scaling
3. Optimization and Evaluation Performance
4. Resource Utilization and Capacity
5. Measurement, Profiling, and Benchmarking
6. Scalability Strategies and Evolution
7. Performance Tradeoffs and Quality
8. Scalability Validation

SP-001–SP-060 are locked.

Explicit principles:

- **SP-004 — Scalability Shall Not Be Reduced to a Universal Measure**
- **SP-030 — No Universal Scalability Guarantee**
- **SP-045 — Scaling Shall Not Become a Second Architecture**

Distinguish:

- performance vs scalability
- problem size vs computational workload
- optimization cost vs evaluation cost
- individual execution vs execution count
- latency vs throughput
- resource consumption vs runtime
- theoretical complexity vs measured performance
- algorithmic limitation vs infrastructure limitation
- fidelity vs computational cost
- performance vs solution quality

**Summary:** The platform treats performance and scalability as measurable properties of optimization problems, evaluation mechanisms, workloads, executions, and computational environments. Scaling mechanisms are introduced incrementally based on evidence.

## Section 18 — Security, Access, Authority, and Operational Considerations — LOCKED

Scope includes:

- identity and access
- authorization/capability control
- ownership/authority
- configuration control
- information protection
- execution control
- shared/multi-user operation
- external integrations
- auditing/accountability
- operational resilience
- human accessibility
- evolution from local to hosted/shared environments

SOA-001–SOA-067 are locked.

Explicit decisions:

- **SOA-018 — Authority Should Not Be Reduced to User Roles**
- **SOA-042 — Local and Hosted Operation Should Share Architectural Semantics**

Authorization model, organizational hierarchy, UI architecture, and threat-modeling methodology remain open.

Not locked:

- RBAC
- ABAC
- OAuth
- specific identity provider
- enterprise SSO
- multi-tenancy
- microservices
- zero-trust architecture
- cloud deployment
- specific encryption technology
- specific database
- specific UI framework
- specific audit system
- 24/7 availability
- disaster recovery infrastructure
- Kubernetes
- distributed authorization services

Human accessibility is distinct from authorization:

> “Can this person use the interface?” ≠ “Is this person authorized to perform this operation?”

Operational authority is distinct from organizational ownership and access authorization.

## Section 19 — Implementation Strategy and Phasing — LOCKED

**Core principle:** The Optimization Platform shall be implemented incrementally, with each phase establishing demonstrable capability and evidence sufficient to justify subsequent architectural and technological complexity.

### Areas

- Area A — Implementation Principles — ISP-001–ISP-008
- Area B — Initial Implementation Strategy — ISP-009–ISP-015
- Area C — Mathematical and Optimization Capability Development — ISP-016–ISP-022
- Area D — Reference-Domain Implementation and Cross-Domain Validation — ISP-023–ISP-029
- Area E — Capability Expansion and Phase Progression — ISP-030–ISP-037
- Area F — Runtime, Deployment, and Scaling Evolution — ISP-038–ISP-044
- Area G — Incremental Verification, Validation, and Demonstration — ISP-045–ISP-050
- Area H — Architectural Learning and Evolution — ISP-051–ISP-058
- Area I — Implementation Artifacts and Traceability — ISP-059–ISP-063
- Area J — Phase Exit Criteria and Readiness — ISP-064–ISP-070

**ISP-015 — Initial Problem Class** remains OPEN.

**ISP-057 — Implementation Shall Not Become the Architecture.**

**ISP-058 — Experimental Success Shall Not Automatically Establish Generality.**

**ISP-070 — Formal Phase Gates** remains OPEN.

Working implementation progression:

1. Phase 0 — Architecture
2. Phase 1 — Minimal Core Optimization Capability
3. Phase 2 — ForgeOpt / Spacecraft Manufacturing Reference Implementation
4. Phase 3 — Dynamic Optimization and Replanning
5. Phase 4 — Uncertainty and Robustness
6. Phase 5 — External Computational Integration
7. Phase 6 — Cross-Domain Architectural Validation
8. Phase 7 — Performance and Scalability Evolution
9. Phase 8 — Shared / Hosted Operational Platform

This is a working progression, not a fixed schedule.

Not locked: dates, staffing, algorithms, solvers, simulation libraries, databases, API technology, cloud providers, microservices, distributed computing, multi-user architecture, authorization model, or fixed future capability sequence.

## Section 20 — Reference Domain Validation — LOCKED

**Central principle:** The Optimization Platform shall validate its architecture through materially different reference domains and problem classes, using implementation and objective evidence to determine which abstractions, boundaries, responsibilities, and contracts represent genuine commonality.

Areas:

1. Reference-Domain Validation Principles
2. Primary Reference Domains
3. Problem-Class and Mathematical Diversity
4. Evaluation and Performance-Model Validation
5. Dynamic Optimization, Replanning, and Changing Context
6. Uncertainty, Stochasticity, and Robustness Validation
7. Multi-Domain and Composed Optimization Validation
8. Additional Architectural Stress-Test Domains
9. Architectural Assessment and Evolution
10. Reference-Domain Evidence and Completion

RDV-001–RDV-070 are locked.

Key decisions include:

- meaningful difference without an artificial numeric criterion
- successful implementation in one domain does not presume generality
- architectural friction is evidence
- preserve domain meaning
- ForgeOpt/spacecraft manufacturing is the initial reference
- Maritime and Energy are architectural stress tests
- unequal implementation depth is allowed
- different decision structures and evaluation mechanisms are important
- preserve mathematical structure
- generalize from demonstrated commonality
- validate dynamic/replanning behavior
- validate uncertainty/robustness
- investigate multi-domain/Port Logistics
- use additional stress-test domains including telecommunications, water distribution, and hospital operations
- retain evidence for ongoing architectural assessment and controlled generalization

**Clarification:** Architectural validation is distinct from scientific/domain validation in Section 15.

## Section 21 — SDS Governance and Change Control — LOCKED

**Central governance principle:** The Optimization Platform SDS shall provide architectural stability through explicit decisions while remaining capable of controlled evolution.

Material architectural changes shall be driven by demonstrated requirements, implementation experience, mathematical or scientific analysis, validation evidence, performance measurements, or other credible architectural evidence.

### Status Model

- **LOCKED** — Established architectural decision currently governing the design
- **PROPOSED** — Deliberate candidate decision under review
- **WORKING HYPOTHESIS** — Useful assumption guiding development but not yet established architecture
- **OPEN** — Unresolved architectural question
- **EXPERIMENTAL** — Capability or approach being explored for evidence
- **DEFERRED** — Deliberately postponed pending future requirement/evidence
- **FUTURE CONCEPT** — Idea retained for possible future investigation

### Governance Areas

1. SDS Authority and Purpose
2. Decision Status and Classification
3. Architectural Change Principles
4. Change Impact and Dependency Analysis
5. Evidence, Validation, and Architectural Learning
6. Review and Decision Process
7. Versioning, History, and Traceability
8. Change Categories and Approval Thresholds
9. Governance of Experiments, Prototypes, and Future Concepts
10. SDS Integrity and Long-Term Evolution

GOV-001–GOV-081 are locked.

Key protections:

- LOCKED does not mean immutable.
- Status changes are explicit.
- Implementation and learning do not automatically change the SDS.
- Scope boundaries are preserved.
- Simplification is valid.
- Prototypes may deliberately violate current architecture for meaningful experiments but do not become architectural authority.
- Future concepts create no present obligations.
- New concerns are not added merely for completeness.
- Governance itself remains incremental.

Significant architectural decisions should, where applicable, be traceable to requirements, intended use, architectural questions, evidence, or rationale.

### Phase 0 Completion

The consolidated Phase 0 baseline is authoritative as represented by the locked conversational SDS and its external document representations.
