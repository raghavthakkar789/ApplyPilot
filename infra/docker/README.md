# Docker infrastructure

Service-specific Dockerfiles live with each service. `compose.yaml` at the
repository root is the canonical M1 runtime interface. Only the web service is
published by default at `127.0.0.1:3000`. Lint and tests use the unpublished
Compose `test` profile (`web-test`, `api-test`, `worker-test`), not the
production runner images.
