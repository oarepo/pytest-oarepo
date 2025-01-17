DEFAULT_RECORD_JSON = {
        "metadata": {
            "creators": [
                "Creator 1",
                "Creator 2",
            ],
            "contributors": ["Contributor 1"],
            "title": "blabla",
        },
        "files": {"enabled": False},
    }

DEFAULT_RECORD_WITH_WORKFLOW_JSON = {
    **DEFAULT_RECORD_JSON,
    "parent": {"workflow": "default"},
}
