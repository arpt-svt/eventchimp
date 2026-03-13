# REST API Best Practices

Guidelines for building and maintaining REST APIs in this project.

## URL Design
- Use nouns for resources, not verbs: `/events`, `/schedules`, `/reservations`.
- Use plural resource names consistently.
- Nest sub-resources to express relationships: `/events/{id}/attendees`.
- Keep URLs lowercase with hyphens for multi-word segments: `/custom-dates`.
- Limit nesting depth to two levels max.

## HTTP Methods
- `GET` — read (safe, idempotent). Never mutate state.
- `POST` — create a new resource.
- `PUT` — full replacement of an existing resource.
- `PATCH` — partial update of an existing resource.
- `DELETE` — remove a resource (idempotent).

## Status Codes
- `200 OK` — successful GET, PUT, PATCH, or DELETE.
- `201 Created` — successful POST that creates a resource. Include `Location` header.
- `204 No Content` — successful DELETE with no response body.
- `400 Bad Request` — malformed input or validation failure. Return field-level errors.
- `401 Unauthorized` — missing or invalid authentication.
- `403 Forbidden` — authenticated but insufficient permissions.
- `404 Not Found` — resource does not exist.
- `409 Conflict` — duplicate or conflicting state (e.g., double-booking).
- `422 Unprocessable Entity` — well-formed request but semantically invalid.
- `500 Internal Server Error` — unexpected server failure. Never expose internals.

## Request & Response Format
- Use JSON (`application/json`) for all request and response bodies.
- Use `snake_case` for field names to match Python/Django conventions.
- Always return a consistent envelope for errors:
  ```json
  {
    "error": "Short error code or message",
    "details": { "field_name": ["Specific validation error."] }
  }
  ```
- Return timestamps in ISO 8601 format (`2025-03-13T14:30:00Z`), stored in UTC.
- Use IANA timezone identifiers (e.g., `America/New_York`) when accepting timezone input.

## Pagination
- Use limit/offset pagination for list endpoints: `?limit=20&offset=0`.
- Return pagination metadata in the response:
  ```json
  {
    "count": 100,
    "next": "/events?limit=20&offset=20",
    "previous": null,
    "results": []
  }
  ```
- Default page size: 20. Maximum: 100.

## Filtering & Sorting
- Support filtering via query parameters: `?status=active&start_date=2025-01-01`.
- Support sorting with an `ordering` parameter: `?ordering=-created_at`.
- Validate all filter/sort fields. Reject unknown parameters with `400`.

## Versioning
- Prefer URL-based versioning (`/api/v1/`) when breaking changes are unavoidable.
- Avoid breaking changes wherever possible — add new fields, don't rename or remove existing ones.

## Authentication & Authorization
- Require authentication on all endpoints unless explicitly public.
- Use token-based auth (e.g., JWT or DRF token auth).
- Check object-level permissions, not just endpoint-level.
- Never expose user data belonging to other users without explicit authorization.

## Validation
- Validate at the serializer layer. Return all validation errors together, not one at a time.
- Use appropriate field types and constraints (e.g., `MinValueValidator`, custom validators).
- Sanitize all user input before database operations.

## Performance
- Use `select_related` / `prefetch_related` to avoid N+1 queries.
- Add database indexes on fields used in filters and ordering.
- Use pagination on all list endpoints — never return unbounded querysets.
- Cache read-heavy, rarely-changing endpoints where appropriate.

## Error Handling
- Catch exceptions at the view/middleware level. Never let raw tracebacks reach the client.
- Log server errors with enough context to debug (request path, user, payload summary).
- Return actionable error messages — tell the caller what to fix.

## Testing
- Write tests for every endpoint covering happy path, validation errors, and permission checks.
- Test with both authenticated and unauthenticated requests.
- Use Django's `APITestCase` or `APIClient` from DRF.
- Assert status codes, response structure, and database side effects.
