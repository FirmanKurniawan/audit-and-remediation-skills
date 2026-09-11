# Playbook — Infrastructure, CI/CD, and IaC

Standards: OWASP Top 10 CI/CD Security Risks, NIST SSDF 800-218, SLSA,
OpenSSF Scorecard, CIS Benchmarks.

## Pipeline security
- Can a pull request from a fork run privileged jobs or read secrets?
  (`pull_request_target` and equivalents)
- Third-party actions/orbs pinned to a commit SHA, not a moving tag
- Secret scope: repository-wide secrets available to every job and every step
- Self-hosted runners: shared between trusted and untrusted workloads, persistent
  state between jobs
- Artifact integrity: signed builds, provenance attestation, immutable tags
- Branch protection, required reviews, and whether they can be bypassed
- Deployment approvals and who can trigger production

## Secrets management
- Secrets in the repo, in CI config, in container images, in build args
- Rotation process and whether it has ever been exercised
- Secret manager usage vs environment variables baked into images
- Git history scan (report locations only; recommend rotation regardless of the
  current file state)

## Infrastructure as code
- Overly permissive IAM (`*` actions, `*` resources, wildcard principals)
- Public storage buckets, open security groups, public database endpoints
- Unencrypted volumes, buckets, and backups; missing key rotation
- Missing logging: no flow logs, no audit trail, no retention policy
- Default VPC/network usage; no segmentation between environments
- Hardcoded state backends without locking or encryption
- Drift between IaC and reality (is anything managed by hand?)

## Containers and runtime
- Base image freshness and provenance; `latest` tags
- Running as root; missing read-only root filesystem; unnecessary capabilities
- Secrets in image layers or `ENV`
- Resource limits absent (a single pod can starve the node)
- Health/readiness probes that do not reflect actual health
- Image scanning in the pipeline and what happens when it fails

## Operations
- Backups: exist, encrypted, and **restore-tested** — an untested backup is a
  hypothesis
- Disaster recovery: RTO/RPO defined, runbook exists
- Monitoring and alerting on the failure modes this audit identified
- Log retention, PII in logs, access to logs
- On-call runbooks for the top failure modes
- Environment parity: does staging resemble production enough to catch anything?
