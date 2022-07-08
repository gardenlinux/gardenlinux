---
name: Bug Report
about: Report a bug
labels: kind/bug

---

**What happened:**
- *Brief description of Bug*

**Debug Logs:**
- *Build System debug logs if applicable*
  - *To generate debug logs, you may want to add `set -x` at the beginning of invoked bash scripts*
  - *Logs are located in the `<repo>/.build/` folder*
- *Runtime Debug logs if applicable* 

**How to reproduce it**:
- *Step by step with the given environment specified in the next section*
 
**Environment:**

| Name | Value |
| ------------------- | ----- |
| Garden Linux Branch | e.g.: *main* |
| Container runtime (version)  | e.g.: *podman (3.4.7)* | 
| Host OS of build machine  | e.g: *macOS* | 

- *Please feel free to add additional details*

**Anything else we need to know**:
- *e.g. last time it worked without the bug?* 
- *e.g. link to your garden linux fork*
- *e.g. tested on other build environments*