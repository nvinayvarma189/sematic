pytest_test(
    name = "test_runs",
    srcs = ["test_runs.py"],
    deps = [
        "//sematic:calculator",
        "//sematic/api/tests:fixtures",
        "//sematic/db:queries",
        "//sematic/db/tests:fixtures",
        requirement("flask"),
    ],
)

pytest_test(
    name = "test_notes",
    srcs = ["test_notes.py"],
    deps = [
        "//sematic/api/tests:fixtures",
        "//sematic/db:queries",
        "//sematic/db/models:note",
        "//sematic/db/models:run",
        "//sematic/db/tests:fixtures",
        requirement("flask"),
        requirement("sqlalchemy"),
    ],
)
