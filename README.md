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

## Smoke tests

A set of sample CARIN Blue Button payloads is stored in `test/smoketest/` and can be executed with the provided scripts.

The smoke tests use explicit FHIR resource IDs and are run in dependency order so reference-based resources are created successfully.

### Create or update the smoke-test resources

Run all smoke tests from a Unix shell:

```bash
./test/run-smoketests.sh
```

Run the same smoke tests from Windows Command Prompt:

```bat
test\run-smoketests.bat
```

Delete all smoke-test resources in reverse dependency order:

```bash
./test/run-smoketests.sh delete
```

```bat
test\run-smoketests.bat delete
```

You can override the target FHIR server URL with:

```bash
BASE_URL=http://localhost:8080/fhir ./test/run-smoketests.sh
```

The scripts default to create/update mode (`PUT`) for the resource set, which makes rerunning them idempotent for the same payload IDs.

### Search-parameter validation

The project also includes a search-parameter validation workflow for the key CARIN BB resources. It inspects the live FHIR CapabilityStatement, validates the supported search parameters for Organization, Practitioner, Patient, RelatedPerson, Coverage, Encounter, Condition, and Observation, and executes a targeted search for each parameter against the local server.

Run the search-parameter tests from a Unix shell:

```bash
./test/run-search-parameter-tests.sh
```

Run the same validation from Windows Command Prompt:

```bat
test\run-search-parameter-tests.bat
```

The script writes a summary report in HTML format to:

```text
./test/search-parameter-report.html
```

The generated report includes total, passed, failed, and pass-rate metrics for each tested search parameter, and it can be opened in a web browser for review.

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

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Next steps

- Add simple CI or a healthcheck script to validate the server on startup.

---

Generated and expanded by repository maintainer guidance.
