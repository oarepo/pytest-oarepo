# pytest oarepo
Pytest fixtures and other test code for OARepo.

The module is divided into different parts for basic repositories, repositories with requests and repositories with communities.

### How to use:
For fixtures, add to your conftest.py following
```python
pytest_plugins = [
    "pytest_oarepo.requests.fixtures",
    "pytest_oarepo.records",
    "pytest_oarepo.fixtures",
    "pytest_oarepo.users",
]
```
Other code can be imported like everything else

### The basic package contains:
- constants
  - DEFAULT_RECORD_JSON - basic data for record creation without workflow
  - DEFAULT_RECORD_WITH_WORKFLOW_JSON - the same but with explicitly added default workflow
- fixtures
  - vocab_cf - initiates OARepo defined custom fields, expected to be used as autouse where needed
  - logged_client - wrapper ensuring the correct user sends an api request
- functions
  - link2testclient - transforms resource link to form used by pytest test clients
  - is_valid_subdict - checks whether dictionary is valid subdictionary and saves where they differ if not
- records
  - draft_factory - creates instance of a draft, additionally allows specifyong custom workflow, additional draft data, expand and other keywords arguments for the record service
  - record_factory - the same for published records
  - record_with_files_factory - the same for published records with attached file
- users
  - a bunch of user fixtures
### The requests module contains
- constants
  - EVENTS_RESOURCE_DATA = data for creation of basic request event 
- fixtures
  - requests_service - basic requests service
  - requests_events_service - basic service for creating request events
  - oarepo_requests_service - oarepo requests service
  - role - Returns a group object that can be used as receiver of a request for example.
  - role_ui_serialization - Returns an expected ui serialization of the group object
  - request_type_additional_data - function giving additional data if specific request type needs them
  - create_request - creates specific request on a specific record
  - submit_request - creates and submits specific request on a specific record
### The communities module contains
- fixtures
  - community_inclusion_service - service for direct inclusion and exclusion of records from communities
  - community_records_service - service for communities related record creations and searches
  - init_communities_cf - init oarepo specific custom fields including the ones relevant for communities, expected to be used with autouse


