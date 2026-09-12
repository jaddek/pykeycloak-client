# Security Policy

## Supported versions

Security fixes are developed against the latest release on the default branch. Users should keep `pykeycloak-client` and its dependencies up to date.

## Reporting a vulnerability

Please do not report security vulnerabilities in public issues.

Report a vulnerability privately through the repository's GitHub security advisory workflow or contact the project maintainers through the private contact listed in the repository owner profile. Include:

- A clear description of the vulnerability and its impact.
- The affected version or commit.
- Reproduction steps or a minimal proof of concept.
- Any suggested mitigation, if available.

Please avoid including real Keycloak credentials, access tokens, client secrets, or personal data in reports. Replace them with sanitized placeholders.

## Response process

Maintainers will acknowledge a report as soon as practical, investigate the issue, and coordinate a fix and disclosure timeline with the reporter. Confirmed fixes are released through the normal tag-based release workflow.

## Secret-handling guidance

- Keep `.env`, `.env.local`, and other local environment files out of version control.
- Use `.env.example` only for sanitized configuration templates.
- Never include client secrets or access tokens in source code, tests, logs, issue reports, or pull requests.
- Run the repository's security checks before submitting changes:

```bash
make audit
make pre-commit
```
