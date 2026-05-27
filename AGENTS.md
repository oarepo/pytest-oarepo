# AGENTS.md — pytest-oarepo

> This file is written for AI coding agents. It describes every public fixture,
> function, class, and extension point in `pytest-oarepo` so that agents can
> write correct `conftest.py` files and tests without guessing.

---

## Table of contents

1. [What this library does](#1-what-this-library-does)
2. [Installation and dependency summary](#2-installation-and-dependency-summary)
3. [How to wire pytest plugins in conftest.py](#3-how-to-wire-pytest-plugins-in-conftest-py)
4. [What the consuming project MUST supply](#4-what-the-consuming-project-must-supply)
5. [Module: pytest_oarepo.fixtures](#5-module-pytest_oarepo-fixtures)
6. [Module: pytest_oarepo.users](#6-module-pytest_oarepo-users)
7. [Module: pytest_oarepo.records](#7-module-pytest_oarepo-records)
8. [Module: pytest_oarepo.files](#8-module-pytest_oarepo-files)
9. [Module: pytest_oarepo.roles](#9-module-pytest_oarepo-roles)
10. [Module: pytest_oarepo.requests.fixtures](#10-module-pytest_oarepo-requests-fixtures)
11. [Module: pytest_oarepo.vocabularies.fixtures](#11-module-pytest_oarepo-vocabularies-fixtures)
12. [Module: pytest_oarepo.communities.fixtures](#12-module-pytest_oarepo-communities-fixtures)
13. [Module: pytest_oarepo.communities.records](#13-module-pytest_oarepo-communities-records)
14. [Module: pytest_oarepo.ui.fixtures](#14-module-pytest_oarepo-ui-fixtures)
15. [Importable classes and functions (not fixtures)](#15-importable-classes-and-functions-not-fixtures)
16. [Fixture dependency graph](#16-fixture-dependency-graph)
17. [Common conftest.py patterns](#17-common-conftest-py-patterns)
18. [Overriding default fixtures](#18-overriding-default-fixtures)
19. [Gotchas and non-obvious behaviour](#19-gotchas-and-non-obvious-behaviour)

---

## 1. What this library does

`pytest-oarepo` provides **pytest fixtures and helpers for testing
[OARepo](https://github.com/oarepo) applications**, which are built on top of
InvenioRDM. It covers:

- Application factory and baseline config
- Pre-built test users and roles
- Record / draft / file creation helpers
- Request (workflow step) creation and submission helpers
- Community creation helpers
- Vocabulary bootstrapping helpers
- UI webpack mock (avoids compiling assets during tests)
- Permission generators for use in test workflow configs

The library does **not** provide a record service or a JSON schema — those
come from the application under test.

---

## 2. Installation and dependency summary

```toml
# pyproject.toml of the consuming project
[project]
dependencies = [
    "pytest-oarepo>=3.0.0,<4.0.0",
]
```

Key transitive dependencies (resolved automatically):

| Package | Version range |
|---|---|
| `oarepo[rdm,tests]` | `>=14,<15` |
| `invenio-app` | `>=3,<4` |
| `invenio-communities` | `>=25,<26` |
| `invenio-drafts-resources` | `>=8,<9` |
| `invenio-search` | `>=3,<4` |
| `pytest-invenio` | `>=4,<5` |
| `deepmerge` | any |

Python **3.14** only (as specified in the library's `requires-python`).

---

## 3. How to wire pytest plugins in conftest.py

Add a top-level `pytest_plugins` list to `conftest.py`. Each string is a
dotted module path that pytest will import as a plugin.

### Minimal setup (records without workflows)

```python
pytest_plugins = [
    "pytest_oarepo.fixtures",   # app_config, logged_client, prepare_record_data, …
    "pytest_oarepo.users",      # users, password, user_with_administration_rights, …
    "pytest_oarepo.records",    # draft_factory, record_factory, record_with_files_factory
    "pytest_oarepo.files",      # upload_file, file_metadata
]
```

### With requests/workflows

```python
pytest_plugins = [
    "pytest_oarepo.requests.fixtures",  # create_request_on_draft, submit_request_on_draft, …
    "pytest_oarepo.records",
    "pytest_oarepo.fixtures",
    "pytest_oarepo.users",
    "pytest_oarepo.files",
    "pytest_oarepo.roles",
]
```

### With vocabularies

```python
pytest_plugins = [
    ...
    "pytest_oarepo.vocabularies.fixtures",  # resourcetypes_rt, resourcetype_dataset
]
```

### With communities

```python
pytest_plugins = [
    ...
    # communities fixtures live in the communities sub-package,
    # they are NOT loaded by default
    "pytest_oarepo.communities.fixtures",   # community, community_owner, invite, …
    "pytest_oarepo.communities.records",    # draft_with_community_factory, …
]
```

### With UI (mocked webpack)

```python
pytest_plugins = [
    ...
    "pytest_oarepo.ui.fixtures",  # overrides app_config with mock manifest loader
]
```

> **Note:** `pytest_oarepo.fixtures` already declares
> `pytest_plugins = ["pytest_oarepo.users"]` internally, so you do not need
> to list `pytest_oarepo.users` separately when `pytest_oarepo.fixtures` is
> present — but it is harmless to include it explicitly.

---

## 4. What the consuming project MUST supply

These fixtures are **required** by `pytest-oarepo` but are **not defined**
inside this library. The consuming project's `conftest.py` must define them.

| Fixture name | Expected type | Used by |
|---|---|---|
| `record_service` | `invenio_drafts_resources.services.RecordService` | `draft_factory`, `record_factory`, `record_with_files_factory`, `create_request`, `draft_with_community_factory`, `published_record_with_community_factory` |
| `base_model_schema` | `str` (JSON schema URI, e.g. `"https://example.org/schema.json"`) | `draft_with_community_factory` (community records only) |

Minimal example:

```python
# tests/conftest.py  (consuming project)
import pytest
from myapp.proxies import current_myapp_service

@pytest.fixture
def record_service():
    return current_myapp_service

@pytest.fixture
def base_model_schema():
    return "local://mymodel/mymodel-1.0.0.json"
```

---

## 5. Module: pytest_oarepo.fixtures

Load with: `"pytest_oarepo.fixtures"`

### Fixtures

#### `create_app` — scope: `module`

```python
def create_app(instance_path: str, entry_points) -> Callable[..., Flask]
```

Returns `invenio_app.factory.create_api`. Standard pytest-invenio hook.
Override this in your `conftest.py` if you need a UI app instead of an API app.

---

#### `host`

```python
def host() -> str  # "https://127.0.0.1:5000/"
```

Base URL used by `link2testclient` and `role_ui_serialization`.
Override if you run on a different host.

---

#### `link2testclient`

```python
def link2testclient(host: str) -> Callable[[str, bool], str]
```

Converts a full resource link into a relative path suitable for the Flask
test client.

```python
# usage
path = link2testclient("https://127.0.0.1:5000/api/records/abc123")
# → "/records/abc123"

path_ui = link2testclient("https://127.0.0.1:5000/records/abc123", ui=True)
# → "/records/abc123"
```

Parameter `ui=False` strips `/api/` prefix (API path); `ui=True` strips just
the host (UI path).

---

#### `default_record_json`

```python
def default_record_json() -> dict
```

Returns:

```python
{
    "metadata": {
        "creators": ["Creator 1", "Creator 2"],
        "contributors": ["Contributor 1"],
        "title": "blabla",
    },
    "files": {"enabled": False},
}
```

Override this fixture in your `conftest.py` if your model has different
required fields.

---

#### `default_record_with_workflow_json`

```python
def default_record_with_workflow_json(default_record_json) -> dict
```

Same as `default_record_json` plus `parent.workflow = "default"`.

---

#### `prepare_record_data`

```python
def prepare_record_data(default_record_json) -> PrepareRecordDataFn
```

Returns a callable with signature:

```python
def _merge_record_data(
    custom_data: dict | None = None,       # replaces default_record_json entirely
    custom_workflow: str | None = None,    # overrides workflow in parent.workflow
    additional_data: dict | None = None,   # deep-merged on top of the base data
    add_default_workflow: bool = True,     # set False to omit workflow (e.g. community)
) -> dict
```

Used internally by `draft_factory` and `record_factory`. You can also call
it directly in tests to build record data without creating a record.

---

#### `logged_client`

```python
def logged_client(client: FlaskClient) -> Callable[[UserFixtureBase], LoggedClient]
```

Factory that wraps the standard Flask test client. The returned `LoggedClient`
re-authenticates the specified user before every HTTP call.

```python
def test_something(logged_client, users):
    client = logged_client(users[0])
    resp = client.get("/api/records/")
    assert resp.status_code == 200
```

`LoggedClient` supports `.get()`, `.post()`, `.put()`, `.delete()`.

---

#### `identity_simple`

```python
def identity_simple(users: list[UserFixtureBase]) -> Identity
```

Returns a `flask_principal.Identity` for `users[0]` with needs:
- `UserNeed(users[0].id)`
- `Need(method="system_role", value="any_user")`
- `Need(method="system_role", value="authenticated_user")`

---

#### `app_config` — scope: `module`

```python
def app_config(app_config: dict) -> dict
```

Extends the pytest-invenio `app_config` with these keys:

| Key | Value |
|---|---|
| `JSONSCHEMAS_HOST` | `"localhost"` |
| `RECORDS_REFRESOLVER_CLS` | `"invenio_records.resolver.InvenioRefResolver"` |
| `RECORDS_REFRESOLVER_STORE` | `"invenio_jsonschemas.proxies.current_refresolver_store"` |
| `RATELIMIT_AUTHENTICATED_USER` | `"200 per second"` |
| `CACHE_TYPE` | `"SimpleCache"` |
| `CACHE_DEFAULT_TIMEOUT` | `300` |
| `FILES_REST_STORAGE_CLASS_LIST` | `{"L": "Local", "F": "Fetch", "R": "Remote"}` |
| `FILES_REST_DEFAULT_STORAGE_CLASS` | `"L"` |

To add your own config keys, override in your `conftest.py`:

```python
@pytest.fixture(scope="module")
def app_config(app_config):
    app_config = super_app_config(app_config)  # if chaining
    app_config["MY_KEY"] = "value"
    return app_config
```

---

#### `model_types` — scope: `session`

```python
def model_types() -> dict
```

Returns a session-scoped dict describing the `Metadata` model type used in
tests (with `title`, `creators`, `contributors` fields). Intended as a shared
reference for oarepo model generation helpers.

---

## 6. Module: pytest_oarepo.users

Load with: `"pytest_oarepo.users"` (also loaded automatically by
`pytest_oarepo.fixtures`).

### Fixtures

#### `password`

```python
def password() -> str
```

A random base64-encoded 16-byte password. Shared across all user fixtures
within one test session. Override if you need a deterministic password.

---

#### `users`

```python
def users(app, db, UserFixture, password) -> list[UserFixtureBase]
```

Creates and indexes **5 pre-built users**:

| Index | Email | Username | Locale | Timezone | Notes |
|---|---|---|---|---|---|
| 0 | `user1@example.org` | — | `en` | default | no username |
| 1 | `user2@example.org` | `beetlesmasher` | `en` | default | |
| 2 | `user3@example.org` | `beetlesmasherXXL` | `en` | default | full_name "Maxipes Fik" |
| 3 | `user4@example.org` | `african` | `en` | `Africa/Dakar` | no DST |
| 4 | `user5@example.org` | `mexican` | `en` | `America/Mexico_City` | |

All users are `active=True`, `confirmed=True`, affiliated with `"CERN"`,
visibility `"public"`. After creation, the user index is refreshed.

> **Idempotent**: if a user with the same email already exists in the DB, the
> fixture reuses it rather than raising an `IntegrityError`.

---

#### `user_with_cs_locale`

```python
def user_with_cs_locale(app, db, UserFixture, password) -> UserFixtureBase
```

Creates `pat@mat.cz` (username `patmat`, full_name `"patmat"`, locale `"cs"`).
Use when testing locale-dependent behaviour.

---

#### `user_with_administration_rights`

```python
def user_with_administration_rights(app, db, UserFixture, password) -> UserFixtureBase
```

Creates `admin@example.org` and grants it `administration-access` via
`invenio_access.ActionUsers`.

---

## 7. Module: pytest_oarepo.records

Load with: `"pytest_oarepo.records"`

All three factory fixtures require `record_service` to be defined by the
consuming project (see [Section 4](#4-what-the-consuming-project-must-supply)).

### Fixtures

#### `draft_factory`

```python
def draft_factory(record_service, prepare_record_data) -> CreateRecordFn
```

Returns a callable:

```python
def draft(
    identity: Identity,
    custom_data: dict | None = None,       # replaces default_record_json entirely
    additional_data: dict | None = None,   # deep-merged on top
    custom_workflow: str | None = None,    # overrides parent.workflow
    expand: bool = False,
    **service_kwargs,
) -> dict  # record.to_dict()
```

Logs a warning (does not raise) if the service returns draft errors.

```python
# Example
def test_create_draft(draft_factory, users):
    draft = draft_factory(users[0].identity)
    assert draft["id"]

def test_draft_custom_workflow(draft_factory, users):
    draft = draft_factory(users[0].identity, custom_workflow="with_approve")
    assert draft["parent"]["workflow"]["id"] == "with_approve"
```

---

#### `record_factory`

```python
def record_factory(record_service, draft_factory) -> CreateRecordFn
```

Same signature as `draft_factory`. Creates a draft and then publishes it using
`system_identity` (not the caller's identity).

```python
def test_published(record_factory, users):
    rec = record_factory(users[0].identity)
    assert rec["status"] == "published"
```

---

#### `record_with_files_factory`

```python
def record_with_files_factory(
    record_service,
    draft_factory,
    default_record_with_workflow_json,
    upload_file,
) -> CreateRecordWithFilesFn
```

Callable signature:

```python
def record(
    identity: Identity,
    custom_data: dict | None = None,
    additional_data: dict | None = None,
    custom_workflow: str | None = None,
    expand: bool = False,
    file_name: str = "test.pdf",               # kept for API parity, not used
    custom_file_metadata: dict | None = None,  # kept for API parity, not used
    **service_kwargs,
) -> dict
```

Automatically sets `files.enabled = True` in the draft data if the default
record JSON has `files.enabled` set. Uses `record_service._draft_files` as
the file service.

---

## 8. Module: pytest_oarepo.files

Load with: `"pytest_oarepo.files"`

### Fixtures

#### `file_metadata`

```python
def file_metadata() -> dict  # {"title": "Test file"}
```

Override to add custom default file metadata.

---

#### `upload_file`

```python
def upload_file(file_metadata) -> UploadFileFn
```

Returns a callable:

```python
def _upload_file(
    identity: Identity,
    record_id: str,
    files_service: FileService,    # usually record_service._draft_files
    file_name: str = "test.pdf",
    custom_file_metadata: dict | None = None,
) -> FileItem
```

Uploads 8 bytes (`b"testfile"`) with the given filename. Steps:
`init_files` → `set_file_content` → `commit_file`.

```python
def test_upload(users, draft_factory, record_service, upload_file):
    draft = draft_factory(users[0].identity, additional_data={"files": {"enabled": True}})
    upload_file(users[0].identity, draft["id"], record_service._draft_files)
```

---

## 9. Module: pytest_oarepo.roles

Load with: `"pytest_oarepo.roles"`

### Fixtures

#### `roles`

```python
def roles(db) -> list[Role]
```

Creates a single `Role` with `id="it-dep"`, `name="it-dep"`,
`description="IT Department"`, `is_managed=False`. Returns `[role]`.

---

#### `add_user_in_role`

```python
def add_user_in_role(db) -> Callable[[UserFixtureBase, Role | str], None]
```

Adds a user to a role. Pass either a `Role` object or a role name string.
If a string is given, it tries to look up the group via `current_groups_service`;
if not found, it creates a bare `Role`.

```python
def test_role(users, roles, add_user_in_role):
    add_user_in_role(users[0], roles[0])
```

---

#### `role_ui_serialization`

```python
def role_ui_serialization(host) -> dict
```

Returns the expected UI-serialized form of the `it-dep` role:

```python
{
    "label": "it-dep",
    "links": {
        "avatar": "https://127.0.0.1:5000/api/groups/it-dep/avatar.svg",
        "self":   "https://127.0.0.1:5000/api/groups/it-dep",
    },
    "reference": {"group": "it-dep"},
    "type": "group",
}
```

---

#### `role_with_administration_rights`

```python
def role_with_administration_rights(app, db) -> Role
```

Creates `admin` role with `administration-access` action via
`invenio_access.ActionRoles`.

---

## 10. Module: pytest_oarepo.requests.fixtures

Load with: `"pytest_oarepo.requests.fixtures"`

Requires: `record_service` from the consuming project.

### Fixtures

#### `requests_service`

```python
def requests_service() -> RequestsService
```

Returns `oarepo_requests.proxies.current_requests_service`.

---

#### `requests_events_service`

```python
def requests_events_service()
```

Returns `invenio_requests.proxies.current_events_service`.

---

#### `events_resource_data`

```python
def events_resource_data() -> dict
```

```python
{
    "payload": {
        "content": "This is an event.",
        "format": "html",   # RequestEventFormat.HTML.value
    }
}
```

---

#### `request_type_additional_data`

```python
def request_type_additional_data() -> dict
```

Default:

```python
{"publish_draft": {"payload": {"version": "1.0"}}}
```

Override this fixture to add required payload data for custom request types:

```python
@pytest.fixture
def request_type_additional_data():
    return {
        "publish_draft": {"payload": {"version": "1.0"}},
        "my_custom_type": {"payload": {"reason": "testing"}},
    }
```

The `create_request` fixture merges this data into `additional_data` when the
request type key is found.

---

#### `create_request`

```python
def create_request(
    request_type_additional_data,
    record_service,
    requests_service,
) -> CreateRequestFn
```

Low-level factory. Callable:

```python
def _create_request(
    identity: Identity,
    id_: str,
    request_type: str,
    topic_read_method: Literal["read", "read_draft"],
    additional_data: dict | None = None,
    expand: bool = False,
    **request_kwargs,
) -> RequestItem
```

Reads the topic (draft or published record) with `system_identity`, then calls
`requests_service.create(...)`.

---

#### `create_request_on_draft`

```python
def create_request_on_draft(create_request) -> CreateRequestOnTopicFn
```

Callable:

```python
def _create(
    identity: Identity,
    topic_id: str,
    request_type: str,
    additional_data: dict | None = None,
    expand: bool = False,
    **request_kwargs,
) -> RequestItem
```

Calls `create_request` with `topic_read_method="read_draft"`.

```python
resp = create_request_on_draft(users[0].identity, draft["id"], "publish_draft")
assert resp["type"] == "publish_draft"
```

---

#### `create_request_on_record`

Same as `create_request_on_draft` but uses `topic_read_method="read"` (for
published records).

---

#### `submit_request_on_draft`

```python
def submit_request_on_draft(
    create_request_on_draft,
    requests_service,
) -> SubmitRequestFn
```

Creates **and submits** a request in one call:

```python
def _submit_request(
    identity: Identity,
    topic_id: str,
    request_type: str,
    create_additional_data: dict | None = None,
    submit_additional_data: dict | None = None,
    expand: bool = False,
) -> RequestItem
```

```python
submitted = submit_request_on_draft(users[0].identity, draft["id"], "publish_draft")
assert submitted["status"] == "submitted"
```

---

#### `submit_request_on_record`

Same as `submit_request_on_draft` but for published records.

---

## 11. Module: pytest_oarepo.vocabularies.fixtures

Load with: `"pytest_oarepo.vocabularies.fixtures"`

### Fixtures

#### `resourcetypes_rt`

```python
def resourcetypes_rt(app, db) -> VocabularyType
```

Idempotent — returns existing `VocabularyType` with `id="resourcetypes"` or
creates it with `pid_type="v-rt"`.

---

#### `resourcetype_dataset`

```python
def resourcetype_dataset(app, db, resourcetypes_rt) -> Vocabulary
```

Idempotent — returns or creates the `("resourcetypes", "dataset")` vocabulary
entry with English title `"Dataset"`.

---

## 12. Module: pytest_oarepo.communities.fixtures

Load with: `"pytest_oarepo.communities.fixtures"` (not in default set — must
be listed explicitly).

### Fixtures

#### `minimal_community`

```python
def minimal_community() -> dict
```

```python
{
    "access": {"visibility": "public", "record_policy": "open"},
    "slug": "public",
    "metadata": {"title": "My Community"},
}
```

Override to customize the default community shape.

---

#### `init_communities_cf`

```python
def init_communities_cf(app, cache) -> None
```

Invokes the `create_communities_custom_field` CLI command and refreshes the
community index. Use as `autouse=True` in modules that need community custom
fields:

```python
@pytest.fixture(autouse=True)
def setup_cf(init_communities_cf):
    pass
```

---

#### `community_owner`

```python
def community_owner(UserFixture, app, db, password) -> UserFixtureBase
```

Creates `community_owner@inveniosoftware.org` with `locale="en"`.

---

#### `community`

```python
def community(app, community_owner, community_get_or_create_in_default_workflow) -> Community
```

A single community with `slug="public"`, `workflow="default"`,
`allowed_workflows=["default"]`.

---

#### `communities`

```python
def communities(app, community_owner, community_get_or_create_in_default_workflow) -> dict[str, Community]
```

Returns `{"aaa": <Community>, "bbb": <Community>}` — two communities for tests
that need multiple communities.

---

#### `community_get_or_create`

```python
def community_get_or_create(minimal_community) -> CommunityGetOrCreateFn
```

Callable:

```python
def _get_or_create(
    community_owner: UserFixtureBase,
    slug: str | None = None,
    community_dict: dict | None = None,
    workflow: str | None = None,
    allowed_workflows: list[str] | None = None,
) -> Community
```

Tries `Community.pid.resolve(slug)` first; creates a new community only if
not found. **Idempotent** by slug.

```python
c = community_get_or_create(
    community_owner,
    slug="my-community",
    workflow="custom_workflow",
    allowed_workflows=["custom_workflow", "default"],
)
```

---

#### `community_get_or_create_in_default_workflow`

```python
def community_get_or_create_in_default_workflow(
    community_get_or_create,
) -> CommunityGetOrCreateWithoutWorkflowArgsFn
```

Simplified wrapper that always uses `workflow="default"` and
`allowed_workflows=["default"]`:

```python
def _get_or_create(
    community_owner: UserFixtureBase,
    slug: str | None = None,
    community_dict: dict | None = None,
) -> Community
```

---

#### `invite`

```python
def invite() -> Callable[[UserFixtureBase, str, str], None]
```

Adds a user to a community with a given role. Re-indexes users and resets
the user's identity cache afterwards.

```python
invite(users[0], community._id, "reader")
invite(users[1], community._id, "manager")
```

Valid roles depend on the InvenioRDM communities configuration
(`"reader"`, `"curator"`, `"manager"`, `"owner"`).

---

## 13. Module: pytest_oarepo.communities.records

Load with: `"pytest_oarepo.communities.records"` (not in default set).

Both fixtures require `record_service` and `base_model_schema` from the
consuming project.

### Fixtures

#### `draft_with_community_factory`

```python
def draft_with_community_factory(
    record_service,
    base_model_schema,
    prepare_record_data,
) -> CreateCommunityRecordFn
```

Callable:

```python
def record(
    identity: Identity,
    community_id: str,
    model_schema: str | None = None,    # defaults to base_model_schema
    custom_data: dict | None = None,
    additional_data: dict | None = None,
    custom_workflow: str | None = None,
    expand: bool = False,
    **service_kwargs,
) -> dict
```

Sets `parent.communities.default = community_id`. Does **not** add
`parent.workflow` automatically (the community provides the default workflow).

---

#### `published_record_with_community_factory`

```python
def published_record_with_community_factory(
    record_service,
    draft_with_community_factory,
) -> CreateCommunityRecordFn
```

Same signature as `draft_with_community_factory`. Creates a draft in the
community and immediately publishes it with `system_identity`.

---

## 14. Module: pytest_oarepo.ui.fixtures

Load with: `"pytest_oarepo.ui.fixtures"`

### Fixtures

#### `app_config` — scope: `module`

Extends `app_config` with:

| Key | Value |
|---|---|
| `IIIF_FORMATS` | `["jpg", "png"]` |
| `APP_RDM_RECORD_THUMBNAIL_SIZES` | `[500]` |
| `WEBPACKEXT_MANIFEST_LOADER` | `MockManifestLoader` |

The `MockManifestLoader` returns `MockJinjaManifest` which does not read any
files from disk — every `manifest["key"]` or `manifest.key` returns a dummy
`JinjaManifestEntry`. This lets UI tests run without building assets.

---

## 15. Importable classes and functions (not fixtures)

### `pytest_oarepo.functions`

```python
from pytest_oarepo.functions import is_valid_subdict, clear_babel_context
```

#### `is_valid_subdict(subdict, dict_) -> bool`

Returns `True` if every key in `subdict` exists in `dict_` with the same
value (recursively). Extra keys in `dict_` are allowed.

```python
assert is_valid_subdict({"a": 1}, {"a": 1, "b": 2})  # True
assert not is_valid_subdict({"a": 9}, {"a": 1})       # False
```

#### `clear_babel_context() -> None`

Resets the `flask_babel` context stored in `g`. Safe to call even when
`flask_babel` is not installed (no-op).

---

### `pytest_oarepo.requests.functions`

```python
from pytest_oarepo.requests.functions import get_request_type, get_request_create_link
```

#### `get_request_type(request_types_json, request_type) -> dict | None`

Given the list of request-type dicts serialized on a record (from
`record["expanded"]["request_types"]` or similar), returns the entry whose
`type_id` matches `request_type`, or `None`.

#### `get_request_create_link(request_types_json, request_type) -> str`

Same as above, but returns `entry["links"]["actions"]["create"]`. Raises
`ValueError` if the type is not found.

```python
link = get_request_create_link(record["expanded"]["request_types"], "publish_draft")
resp = logged_client.post(link2testclient(link), json={})
```

---

### `pytest_oarepo.communities.functions`

```python
from pytest_oarepo.communities.functions import (
    remove_member_from_community,
    set_community_workflow,
)
```

#### `remove_member_from_community(user_id: str, community_id: str) -> None`

Removes a user from a community using `system_identity`.

#### `set_community_workflow(community_id: str, workflow: str = "default") -> None`

Updates a community's `custom_fields.workflow` using `system_identity`. Use
in tests that need to switch a community's workflow mid-test.

---

### `pytest_oarepo.permission_generators`

Plain permission generators (without `RecipientGeneratorMixin`). Use in
non-workflow permission policies or for `needs()` / `excludes()` checks.

```python
from pytest_oarepo.permission_generators import (
    SystemUserGenerator,
    UserGenerator,
    CSLocaleUserGenerator,
    UserExcluded,
    Administration,
)
```

| Class | `needs()` | `excludes()` | Notes |
|---|---|---|---|
| `SystemUserGenerator` | `[UserNeed("system")]` | — | |
| `UserGenerator(email)` | `[UserNeed(user.id)]` | — | looks up by email at call time |
| `CSLocaleUserGenerator` | `[UserNeed(cs_user.id)]` | — | finds first user with `locale=="cs"` |
| `UserExcluded(email)` | — | `[UserNeed(user.id)]` | denies specific user |
| `Administration` | `[ActionNeed("administration")]` | — | also returns `match_all` query filter |

---

### `pytest_oarepo.workflows.permission_generators`

Same generators but with `RecipientGeneratorMixin`, needed when these
generators are used as **receivers** (i.e. `recipients` list) in an OARepo
workflow request definition.

```python
from pytest_oarepo.workflows.permission_generators import (
    SystemUserGenerator,
    UserGenerator,
    CSLocaleUserGenerator,
)
```

Each class adds `reference_receivers(...)` returning a list of
`{"user": "<id>"}` dicts.

---

### `pytest_oarepo.workflows.events`

```python
from pytest_oarepo.workflows.events import TestEventType
```

`TestEventType` is a `CommentEventType` subclass with `type_id = "T"`. Register
it in your workflow's event types list when testing custom event handling.

---

### `pytest_oarepo.ui.classes`

```python
from pytest_oarepo.ui.classes import MockJinjaManifest, MockManifestLoader
```

Use `MockManifestLoader` directly in `app_config["WEBPACKEXT_MANIFEST_LOADER"]`
if you need the UI mock without loading the full `pytest_oarepo.ui.fixtures`
plugin.

---

## 16. Fixture dependency graph

```
pytest-invenio
  └── app, db, UserFixture, client, cache   (provided by pytest-invenio)

pytest_oarepo.fixtures
  ├── create_app               ← (none)
  ├── host                     ← (none)
  ├── link2testclient          ← host
  ├── default_record_json      ← (none)
  ├── default_record_with_workflow_json ← default_record_json
  ├── prepare_record_data      ← default_record_json
  ├── logged_client            ← client
  ├── identity_simple          ← users
  ├── app_config               ← app_config (pytest-invenio)
  └── model_types              ← (none)

pytest_oarepo.users
  ├── password                 ← (none)
  ├── users                    ← app, db, UserFixture, password
  ├── user_with_cs_locale      ← app, db, UserFixture, password
  └── user_with_administration_rights ← app, db, UserFixture, password

pytest_oarepo.files
  ├── file_metadata            ← (none)
  └── upload_file              ← file_metadata

pytest_oarepo.records                   [requires: record_service from consumer]
  ├── draft_factory            ← record_service, prepare_record_data
  ├── record_factory           ← record_service, draft_factory
  └── record_with_files_factory ← record_service, draft_factory,
                                   default_record_with_workflow_json, upload_file

pytest_oarepo.roles
  ├── roles                    ← db
  ├── add_user_in_role         ← db
  ├── role_ui_serialization    ← host
  └── role_with_administration_rights ← app, db

pytest_oarepo.requests.fixtures         [requires: record_service from consumer]
  ├── requests_service         ← (none)
  ├── requests_events_service  ← (none)
  ├── events_resource_data     ← (none)
  ├── request_type_additional_data ← (none)
  ├── create_request           ← request_type_additional_data, record_service, requests_service
  ├── create_request_on_draft  ← create_request
  ├── create_request_on_record ← create_request
  ├── submit_request_on_draft  ← create_request_on_draft, requests_service
  └── submit_request_on_record ← create_request_on_record, requests_service

pytest_oarepo.vocabularies.fixtures
  ├── resourcetypes_rt         ← app, db
  └── resourcetype_dataset     ← app, db, resourcetypes_rt

pytest_oarepo.communities.fixtures      [requires: password from users module]
  ├── minimal_community        ← (none)
  ├── init_communities_cf      ← app, cache
  ├── community_owner          ← UserFixture, app, db, password
  ├── community                ← app, community_owner, community_get_or_create_in_default_workflow
  ├── communities              ← app, community_owner, community_get_or_create_in_default_workflow
  ├── community_get_or_create  ← minimal_community
  ├── community_get_or_create_in_default_workflow ← community_get_or_create
  └── invite                   ← (none)

pytest_oarepo.communities.records       [requires: record_service, base_model_schema from consumer]
  ├── draft_with_community_factory ← record_service, base_model_schema, prepare_record_data
  └── published_record_with_community_factory ← record_service, draft_with_community_factory

pytest_oarepo.ui.fixtures
  └── app_config               ← app_config (pytest-invenio)
```

---

## 17. Common conftest.py patterns

### Pattern A — API tests for a record model with workflows

```python
# tests/conftest.py
import pytest
from myapp.proxies import current_myrecords_service

pytest_plugins = [
    "pytest_oarepo.requests.fixtures",
    "pytest_oarepo.records",
    "pytest_oarepo.fixtures",
    "pytest_oarepo.users",
    "pytest_oarepo.files",
    "pytest_oarepo.roles",
]

@pytest.fixture(scope="module")
def record_service():
    return current_myrecords_service

@pytest.fixture(scope="module")
def app_config(app_config):
    app_config["OAREPO_WORKFLOWS"] = {
        "default": MyDefaultWorkflow(),
    }
    return app_config
```

### Pattern B — Community-based records

```python
pytest_plugins = [
    "pytest_oarepo.fixtures",
    "pytest_oarepo.users",
    "pytest_oarepo.records",
    "pytest_oarepo.files",
    "pytest_oarepo.communities.fixtures",
    "pytest_oarepo.communities.records",
]

@pytest.fixture
def record_service():
    return current_myrecords_service

@pytest.fixture
def base_model_schema():
    return "local://mymodel/mymodel-1.0.0.json"

@pytest.fixture(autouse=True)
def setup_communities_cf(init_communities_cf):
    pass
```

### Pattern C — Overriding record data for a custom model

```python
@pytest.fixture
def default_record_json():
    """Override: our model uses 'title' at top-level, not inside metadata."""
    return {
        "title": "Test record",
        "files": {"enabled": False},
    }
```

### Pattern D — Custom request type with extra payload

```python
@pytest.fixture
def request_type_additional_data():
    return {
        "publish_draft": {"payload": {"version": "1.0"}},
        "request_changes": {"payload": {"message": "Please fix abstract"}},
    }
```

---

## 18. Overriding default fixtures

The following fixtures are the most commonly overridden in consuming projects:

| Fixture | Why you would override it |
|---|---|
| `default_record_json` | Your model has different required fields |
| `app_config` | Add application-specific config (workflows, feature flags, …) |
| `request_type_additional_data` | Your custom request types need payload data |
| `file_metadata` | Custom default file metadata |
| `minimal_community` | Custom community shape |
| `host` | Different test host/port |
| `password` | Deterministic password for snapshot testing |

When overriding `app_config`, always call `super()` by accepting the
`app_config` parameter (pytest fixture chaining):

```python
@pytest.fixture(scope="module")
def app_config(app_config):          # receives the pytest-oarepo version
    app_config["MY_SETTING"] = True  # extend it
    return app_config
```

---

## 19. Gotchas and non-obvious behaviour

1. **`record_service` is not optional.** Every record/request/community record
   fixture depends on it. If you see `fixture 'record_service' not found`,
   define it in your `conftest.py`.

2. **`record_factory` publishes with `system_identity`**, not the caller's
   identity. This means post-publish permission checks are not tested by
   `record_factory` itself.

3. **`prepare_record_data` adds `parent.workflow = "default"` by default.**
   Pass `add_default_workflow=False` when creating records in a community
   (the community provides the workflow). `draft_with_community_factory` does
   this automatically.

4. **`LoggedClient` re-logs the user on every call.** This is intentional to
   keep tests hermetic, but it means the session is refreshed before every
   GET/POST/PUT/DELETE.

5. **User index must be fresh.** `users` and `community_owner` call
   `_index_users()` after creation. If you create users manually without using
   these fixtures, call `_index_users()` yourself:
   ```python
   from pytest_oarepo.functions import _index_users
   _index_users()
   ```

6. **`community_get_or_create` is idempotent by slug.** It will not raise if a
   community with the same slug exists. This is safe to call across test
   sessions that share a database.

7. **`init_communities_cf` must run before any test that uses community custom
   fields** (e.g. `community.custom_fields.workflow`). Mark it as `autouse=True`
   or list it as a direct fixture dependency.

8. **`roles` fixture creates a group called `it-dep`**, not a user role. It
   uses `current_datastore.create_role` with `is_managed=False`. Do not
   confuse it with Invenio's system roles.

9. **`request_type_additional_data` is merged into every matching request
   creation call.** If your request type shares a key with one in the default
   dict (`publish_draft`), override the entire fixture to avoid unintended
   merges.

10. **`draft_factory` logs warnings but does not raise on draft errors.** Always
    check `draft["errors"]` in tests that exercise validation paths.

11. **Workflow permission generators in `pytest_oarepo.workflows.permission_generators`
    differ from those in `pytest_oarepo.permission_generators`**: the `workflows`
    variants mix in `RecipientGeneratorMixin` and implement `reference_receivers`.
    Use the `workflows` variants when the generator is placed in a `recipients`
    list inside an `oarepo-workflows` workflow definition.

12. **`base_model_schema` is only required for community record factories.**
    Plain `draft_factory` / `record_factory` do not need it.

13. **`user_with_administration_rights` creates a separate `admin@example.org`
    user**, distinct from the 5 users in the `users` fixture. The `users`
    fixture itself does not grant any special permissions.
