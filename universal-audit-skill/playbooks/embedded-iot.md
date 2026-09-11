# Playbook — Embedded / IoT / Edge

Standards: IEC 62443 (industrial), CWE Top 25 memory-safety entries, SEI CERT C/C++,
MISRA where safety-critical, EU CRA (products with digital elements), ISO/IEC 5055.

## Memory and language safety
- Buffer overflow: every `memcpy`, `strcpy`, `sprintf`, array index derived from
  input, and every length field taken from the wire
- Off-by-one on ring buffers and DMA descriptors
- Use-after-free and double-free on error paths
- Integer overflow in size arithmetic before allocation
- Sign/unsigned confusion in length and index handling
- Endianness assumptions in protocol parsing
- Stack depth in ISRs and deep call chains; stack canaries and MPU usage
- Unchecked return values from allocation and I/O

## Concurrency and real-time
- ISR-to-task communication: correct primitives, no blocking in an ISR
- Shared state without volatile/atomics/critical sections
- Priority inversion; missing priority inheritance
- Watchdog: fed by a task that can hang, or fed unconditionally from a timer
  (which defeats the point)
- Deadline misses on the control loop; worst-case execution time considered
- Time base: overflow of tick counters, monotonic vs wall clock

## Boot, update, and recovery
- Secure boot chain and signature verification
- A/B or fail-safe update with rollback; what happens on power loss mid-update
- Recovery from a corrupted filesystem or config
- Factory reset completeness (does it clear credentials?)
- Provisioning: how does the device get its identity, and can it be cloned?

## Storage and configuration
- Flash wear from frequent writes; write amplification on logs
- Config integrity: checksum or signature, atomic write, safe defaults on corruption
- Credentials in flash unencrypted; shared per-fleet keys
- Debug interfaces (UART, JTAG/SWD) left enabled in production

## Communications
- Custom protocols: authentication, integrity, replay protection, sequence handling
- Behaviour with an unreachable server: bounded retry, no reconnect storm across
  the fleet, jitter to avoid thundering herd
- Network handover, DNS failure, captive portals, long outages
- TLS on a constrained device: cert validation actually enabled, time source for
  validity checks, cert rotation strategy
- Fail-safe state on communication loss — this is usually the highest-severity
  question in the whole audit

## Physical and operational safety
- Can a software fault leave an actuator, transmitter, heater, or motor energized?
- Is there a hardware or independent-timer fail-safe, or does safety depend on the
  application logic that just crashed?
- Startup state after a power cycle: safe, or resumed-as-before?
- Operator feedback: does the UI ever show a state that differs from the physical
  state? (Misleading operational status is a Critical-class finding.)
- Emergency stop path and its independence from the main control path

## Fleet and lifecycle
- Remote diagnostics and log retrieval, with consent and redaction
- Version inventory and staged rollout
- Support period and update commitment (CRA expects this to be defined)
- SBOM for firmware, including the toolchain and third-party stacks
