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

- fixtures
  - host - where the tests are running
  - link2testclient - helper function to convert links into format used by pytest test client
  - default_record_json - basic data for record creation without workflow
  - default_record_with_workflow_json - the same but with explicitly added default workflow
  - prepare_record_data - Function for merging input definitions into data passed to record service.
  - vocab_cf - initiates OARepo defined custom fields, expected to be used as autouse where needed
  - logged_client - wrapper ensuring the correct user sends an api requests
- functions
  - link2testclient - transforms resource link to form used by pytest test clients
  - is_valid_subdict - Checks whether dictionary is valid subdictionary and returns where they differ if not.
- records
  - draft_factory - Creates instance of a draft, additionally allows specifying 
  custom workflow, additional draft data, expand and other 
  keywords arguments for the record service. Example of use with custom workflow:
  ```python
  draft1 = draft_factory(user1.identity, custom_workflow="with_approve")
  ```
  - record_factory - the same for published records
  - record_with_files_factory - the same for published records with attached file
- users
  - a bunch of user fixtures
### The requests module contains
- fixtures
  - requests_service - Underlying requests service
  - requests_events_service - Underlying service for creating request events
  - oarepo_requests_service - OARepo requests service
  - role - Returns a group object that can be used as receiver of a request for example.
  - role_ui_serialization - Returns an expected ui serialization of the group object
  - events_resource_data - Default data for creating a request event.
  - request_type_additional_data - Function giving additional data if specific request type needs them
  - create_request - Base fixture for creating a request.
  - create_request_on_draft - Fixture for creating a request on a draft.
  ```python
      resp_request_create = create_request_on_draft(
        creator.identity, draft1_id, "publish_draft"
    )
  ```
  - create_request_on_record - Fixture for creating a request on a published record.
  - submit_request_on_draft - Fixture for creating and submitting request on a draft in one call.
  - submit_request_on_record - Fixture for creating and submitting request on a published record in one call.
  - submit_request - creates and submits specific request on a specific record
- classes
  - TestEventType - Custom generic EventType usable in tests.
  - UserGenerator - Permission generator primarily used to define specific user as recipient of a request.
- functions
  - get_request_type - Function returning dict representing serialized request type from serialized request types on record.
  - get_request_create_link - The same but returns create link.
### The communities module contains
- fixtures
  - community_inclusion_service - service for direct inclusion and exclusion of records from communities
  - community_records_service - service for communities related record creations 
  and searches
  - minimal_community - Default data used for creating a new community.
  - init_communities_cf - init oarepo specific custom fields including the 
  ones relevant for communities, expected to be used with autouse
  - community - Basic community.
  - community_owner - User fixture used as owner of the community fixture.
  - community_get_or_create - Function returning existing community or creating new one if one with the same slug doesn't exist.
- functions
  - invite - Adds user into a community in a specified role.
  - remove_member_from_community - Removes a user from a community.
  - set_community_workflow - Set default workflow of a community.
- records
  - draft_with_community_factory - Creates instance of a draft in specified community.
  - published_record_with_community_factory - Creates instance of a published record in specified community.


