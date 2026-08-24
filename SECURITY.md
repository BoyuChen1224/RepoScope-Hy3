# Security policy

RepoScope processes untrusted repository content and sends selected evidence excerpts to a configured
Hy3-compatible endpoint. It must not be exposed directly to the public Internet without authentication,
rate limits, network egress controls, and a deployment-specific review.

## Report a vulnerability

Do not open a public issue containing exploit details or secrets. Send a private report through the
repository owner's GitHub profile contact channel. Include affected version, reproduction steps, impact,
and suggested remediation when available.

## Security properties

- Only configured public HTTPS Git hosts are accepted.
- URL credentials, custom ports, local paths, and arbitrary hostnames fail closed.
- Child processes use argument arrays and never invoke a shell.
- Symlinks and generated dependency directories are excluded from evidence collection.
- Clone duration, repository size, and model context are bounded.
- Repository content is evidence, never a trusted instruction source.
- API keys remain server-side and are excluded by `.gitignore`.
- Model output is schema-validated and escaped before browser rendering.

## Known boundaries

- Static secret-pattern scanning is not a complete security scan.
- A missing file is not proof that a policy or control does not exist elsewhere.
- The semantic judge uses the same model family by default and may share generator biases.
- Temporary repository deletion is best-effort after analysis; hardened deployments should use
  isolated ephemeral workers.

