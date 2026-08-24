# Docker runtime validation

Validation date: 2026-08-24 (Asia/Shanghai)

This record documents a live Docker Desktop run, rather than inferring runtime behavior from a
successful Compose parse.

## Environment and build

- Docker Desktop: 4.76.0
- Docker Engine: 29.5.2, Linux/amd64
- Compose service: `reposcope`
- Image: `reposcope-hy3-reposcope:latest`
- Build result: success from `python:3.12-slim`, including Git and application dependencies
- Published port: `8000:8000`

The running container reported `User=reposcope`, `ReadonlyRootfs=true`, `CapDrop=["ALL"]`,
`SecurityOpt=["no-new-privileges:true"]`, and state `running`.

## Runtime checks

1. `GET /api/health` returned `{"status":"ok","version":"0.1.0"}`.
2. `GET /` returned the RepoScope Hy3 application page.
3. `GET /openapi.json` exposed the expected inspect, generate, deterministic-evaluate, and
   semantic-judge routes.
4. `POST /api/repositories/inspect` cloned the public RepoScope repository from inside the
   read-only container, using its `/tmp` tmpfs. It fixed commit
   `cbac872c00cf5481f594d7c2101de0ed5be27caa`, collected 60 files / 1,848,360 bytes, and returned
   no warnings.
5. `POST /api/reports/generate` made a real Hy3 request through the container. The accepted report
   contained 4 claims, 3 risks, and 3 recommendations with decision `conditional`.
6. `POST /api/evaluations/evaluate` returned 100/A with zero hard failures.

No API key or environment value was printed or stored in this report.

## Defect found and closed

The first live generation returned useful content under non-schema field names (`findings` and
`goal`) and was correctly rejected with HTTP 502. The client now makes one constrained repair
attempt after a schema-validation failure, asking Hy3 to use the exact versioned field names. The
repaired response still passes the unchanged Pydantic schema; a second invalid response still
fails closed. A regression test covers this behavior.

After the change, Ruff passed, all 13 tests passed, the image rebuilt successfully, and the complete
container inspection-generation-evaluation flow passed as described above.
