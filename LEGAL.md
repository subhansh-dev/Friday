# LEGAL.md — Friday Cybersecurity Module

## Purpose

Friday's cybersecurity module is designed for **authorized security testing of systems you own or have explicit written permission to test**. This includes:

- Security auditing your own source code (static analysis)
- Testing your own web applications and APIs
- Penetration testing with proper authorization
- Bug bounty programs with defined scope
- CTF (Capture The Flag) competitions
- Security research in controlled environments

## Restrictions

**You MUST NOT use Friday's cyber tools to:**

- Scan or attack systems you do not own or have authorization to test
- Access cloud metadata endpoints or internal infrastructure
- Perform unauthorized reconnaissance on third-party domains
- Exploit vulnerabilities on production systems without permission
- Conduct any activity that violates applicable laws

## Target Validation

Friday includes a **target guard** system that classifies targets:

- **Local targets** (localhost, private IPs) — always allowed, no authorization needed
- **External targets** — require explicit ownership confirmation via typed consent
- **Blocked targets** (cloud metadata) — never allowed

All target validation decisions are logged to an audit trail at `data/audit_log.json`.

## Legal Compliance

Laws governing unauthorized computer access include but are not limited to:

- **United States:** Computer Fraud and Abuse Act (CFAA), 18 U.S.C. § 1030
- **United Kingdom:** Computer Misuse Act 1990
- **European Union:** Directive 2013/40/EU
- **China:** Criminal Law Chapter VI Section 1 (Articles 285-287)
- **India:** Information Technology Act 2000, Section 43 & 66

Unauthorized access to computer systems is a criminal offense in most jurisdictions. Penalties include fines and imprisonment.

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. THE AUTHORS AND CONTRIBUTORS ARE NOT RESPONSIBLE FOR ANY MISUSE OF THIS SOFTWARE. By using Friday's cybersecurity features, you agree that:

1. You will only test systems you own or have written authorization to test
2. You understand and comply with all applicable laws
3. You accept full responsibility for your actions
4. The authors bear no liability for any damages resulting from use of this software

## For Security Professionals

If you are a licensed penetration tester or security researcher:

- Friday's tools are designed to complement, not replace, professional security testing
- Always obtain proper written authorization before testing
- Document your scope and methodology
- Follow responsible disclosure practices
- Maintain audit trails of all testing activity

## Reporting Misuse

If you become aware of Friday being used for unauthorized access, please report it to the repository maintainer.
