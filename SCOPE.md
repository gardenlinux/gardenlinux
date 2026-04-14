# Project Scope

## Overview

The Garden Linux Project develops and maintains a minimal, purpose-built operating system environment for containerized and cloud-native infrastructure. Garden Linux provides a secure, largely immutable, and reproducible runtime optimized for Kubernetes platforms such as Gardener, while also supporting use as a container base image or standalone system.

Garden Linux is designed as an operating system layer for automated platforms and is not intended to be a general-purpose Linux distribution.

---

## Scope of the Project

The scope of the Project includes the collaborative development, maintenance, and operation of software and related artifacts that support the mission, including:

- A minimal, secure, and largely immutable operating system environment
- System components and configurations required to support containerized and Kubernetes-based workloads
- Programmatic interfaces and declarative configuration mechanisms for system interaction and management
- Build systems and tooling that enable reproducible and verifiable system images
- Integration artifacts for deployment across cloud, edge, and other automated infrastructure environments
- Release engineering processes, including image creation, updates, and lifecycle management
- Documentation, testing, validation, and integration frameworks
- Other artifacts that support the development, deployment, operation, or adoption of the Project

---

## Non-Goals

The Project explicitly does not aim to:

- Provide or replace a general-purpose Linux distribution
- Compete with or substitute enterprise Linux offerings
- Support broad end-user, desktop, or workstation use cases
- Enable or prioritize manual system administration workflows over automated management
- Include components not required for its container-focused and cloud-native use cases
- Provide a full platform solution, including orchestration, cluster management, or application runtimes
- Define or replace standards for Linux distributions or user-space environments
- Support arbitrary customization that compromises reproducibility or system integrity
- Act as a package ecosystem or general-purpose software distribution platform

---

## Guiding Principles

The Project is guided by the following principles:

- **Minimalism**: Maintain a small footprint by including only essential components  
- **Immutability**: Favor a largely immutable system design to ensure consistency and reliability  
- **Reproducibility**: Enable deterministic and repeatable builds and deployments  
- **Security and Reliability**: Prioritize secure defaults and stable system behavior  
- **Automation First**: Design for declarative management and integration into automated infrastructure  
- **API-Driven Interaction**: Enable system management through stable programmatic interfaces  
- **Compatibility**: Maintain alignment with common Linux user-space expectations  

---

## Collaboration and Governance

The Project operates under the applicable Project Licenses and follows an open governance model. Contributions may include source code, documentation, testing, integration, and other artifacts that support the development and adoption of the Project.

All activities of the Project are expected to align with this scope. Changes to the scope must be approved through the Project’s governance processes.

