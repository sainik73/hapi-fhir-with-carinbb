# hapi-fhir-r4

Expanded README for the HAPI FHIR R4 server deployment used in this workspace.

## Project

- Lightweight local setup for HAPI FHIR R4 configured via `hapi.application.yaml`.
- PostgreSQL data is persisted under `postgres_data/`.

## Requirements

- Docker & Docker Compose (tested on Windows).
- Java (for building locally, optional if using provided Docker image).

## Quick start

1. Build and start services:

```bash
docker-compose up -d --build
```

2. Verify the server is reachable at:

   http://localhost:8080/fhir

3. View logs:

```bash
docker-compose logs -f
```

## Healthchecks

- Basic HTTP check (server should return 200):

```bash
curl -I http://localhost:8080/fhir
```

- Readiness/metadata endpoint:

```bash
curl http://localhost:8080/fhir/metadata
```

## Example FHIR requests

- Get CapabilityStatement:

```bash
curl http://localhost:8080/fhir/metadata
```

- Read a Patient (replace `<id>`):

```bash
curl http://localhost:8080/fhir/Patient/<id>
```

- Create a Patient (JSON example):

```bash
curl -X POST http://localhost:8080/fhir/Patient \
   -H "Content-Type: application/fhir+json" \
   -d '{"resourceType":"Patient","name":[{"family":"Doe","given":["Jane"]}],"gender":"female"}'
```

## Configuration

- Application config: `hapi.application.yaml` (server settings, datasource, IG installation).
- Database: Postgres is configured via `docker-compose.yml` and stores data in `postgres_data/`.

## Troubleshooting

- If the server fails to start, check the logs:

```bash
docker-compose logs -f
```

- Database connection issues:

  - Confirm Postgres container is running and listening on port `5432`.
  - Verify credentials in `hapi.application.yaml` match your DB settings.

- CARIN IG installation failures:
  - The IG install runs at startup; check logs for messages about fetching/installing the package.
  - Increase logging or enable IG upload options in `hapi.application.yaml` for more detail.

## License

This repository does not include an explicit license file. If you intend to publish or share this project, add a license (for example, the MIT license below).

MIT License

Copyright (c) YEAR Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Replace `YEAR` and `Your Name` as appropriate or add a different license file.

## Next steps

- Optionally add a `LICENSE` file with your chosen license.
- Add simple CI or a healthcheck script to validate the server on startup.

---

Generated and expanded by repository maintainer guidance.
