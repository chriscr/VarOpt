# NexaOpt

> **Networked & Distributed-System Optimization**

<!--
Logo
Proposed location:
assets/logos/nexaopt-logo.png

When the logo asset is available, use:

![NexaOpt](../assets/logos/nexaopt-logo.png)
-->
![NexaOpt](../assets/logos/nexaopt-logo.png)

## Overview

**NexaOpt** is the networked and distributed-system application of the VarOpt optimization platform.

NexaOpt is intended for optimization problems involving interconnected components, network topology, distributed resources, flows, capacities, and system-wide operating objectives.

The initial reference application is **energy grid operations**.

The architecture is intentionally broader than electrical power systems and is intended to support other networked physical systems.

## Relationship to VarOpt

NexaOpt is built on the VarOpt platform.

```text id="4f8q2v"
                    VarOpt
        Domain-Agnostic Optimization
                    Platform
                       |
                       v
                   NexaOpt
       Networked & Distributed Systems
                       |
                       v
             Energy Grid Operations
```

VarOpt provides the domain-agnostic optimization framework.

NexaOpt provides network- and distributed-system-specific:

* nodes;
* edges and connections;
* topology;
* network state;
* flows;
* capacities;
* distributed resources;
* conservation constraints;
* operating constraints;
* network performance models; and
* system-level objectives.

## Reference Domain

The initial reference domain is **energy grid operations**.

The energy-grid reference problem provides a demanding networked-system environment involving potentially coupled decisions related to:

* generation;
* transmission;
* distribution;
* network topology;
* power flow;
* resource allocation;
* capacity;
* operating constraints;
* system state;
* reliability; and
* changing demand and supply conditions.

The NexaOpt architecture is intended to remain applicable to other networked physical systems.

Potential future applications include areas such as:

* water distribution;
* hydraulic networks;
* resource-distribution systems;
* pipeline networks;
* other infrastructure networks; and
* coupled network systems.

## Optimization Focus

NexaOpt will investigate optimization of decisions including, as appropriate:

* network configuration;
* topology;
* resource allocation;
* flow management;
* capacity utilization;
* operating conditions;
* network resilience;
* distributed resources;
* system-wide objectives; and
* dynamic network operation and replanning.

## Documentation

The NexaOpt documentation will eventually include:

* NexaOpt System Definition Specification
* Networked-System Domain Model
* NexaOpt Architecture
* Energy Grid Reference Model
* Network and Flow Formulations
* Validation Problems
* Experiments
* Benchmarks

## Development Status

**Current status: Domain architecture / foundation phase**

NexaOpt is being developed as a domain application of VarOpt rather than as a separate optimization framework.

## Design Principle

NexaOpt should provide a substantially different validation environment from both ForgeOpt and NavOpt.

Its purpose is to exercise VarOpt against problems characterized by interconnected components, topology, distributed resources, network constraints, and system-wide interactions.

Network-specific concepts should remain within NexaOpt unless they represent genuinely domain-independent capabilities appropriate for the VarOpt platform.

## Repository Location

```text id="j4r8sx"
domains/NexaOpt/
```

## Maintainer

NexaOpt is developed as part of the VarOpt project and maintained by Chris Romero.
