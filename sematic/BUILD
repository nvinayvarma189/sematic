sematic_py_lib(
    name = "init",
    srcs = ["__init__.py"],
    deps = [
        ":calculator",
        ":resolver",
        "//sematic/future_operators:init",
        "//sematic/resolvers:cloud_resolver",
        "//sematic/resolvers:local_resolver",
        "//sematic/resolvers:resource_requirements",
        "//sematic/resolvers:worker",
        "//sematic/types:casting",
        "//sematic/types:init",
    ],
)

sematic_py_lib(
    name = "config",
    srcs = ["config.py"],
    deps = [
        ":config_dir",
        ":user_settings",
    ],
)

sematic_py_lib(
    name = "config_dir",
    srcs = ["config_dir.py"],
    deps = [],
)

sematic_py_lib(
    name = "user_settings",
    srcs = ["user_settings.py"],
    deps = [
        ":config_dir",
        requirement("pyyaml"),
    ],
)

sematic_py_lib(
    name = "api_client",
    srcs = ["api_client.py"],
    deps = [
        ":config",
        "//sematic/db/models:artifact",
        "//sematic/db/models:edge",
        "//sematic/db/models:run",
        requirement("requests"),
    ],
)

sematic_py_lib(
    name = "abstract_calculator",
    srcs = ["abstract_calculator.py"],
    deps = [],
)

sematic_py_lib(
    name = "abstract_future",
    srcs = ["abstract_future.py"],
    deps = [
        ":abstract_calculator",
        "//sematic/resolvers:resource_requirements",
    ],
)

sematic_py_lib(
    name = "calculator",
    srcs = ["calculator.py"],
    deps = [
        ":abstract_calculator",
        ":future",
        "//sematic/resolvers:resource_requirements",
        "//sematic/types:casting",
        "//sematic/types:init",
        "//sematic/types:registry",
        "//sematic/types:type",
        "//sematic/utils:memoized_property",
    ],
)

sematic_py_lib(
    name = "future",
    srcs = ["future.py"],
    deps = [
        ":abstract_calculator",
        ":abstract_future",
        "//sematic:resolver",
        "//sematic/resolvers:local_resolver",
        "//sematic/resolvers:silent_resolver",
    ],
)

sematic_py_lib(
    name = "resolver",
    srcs = ["resolver.py"],
    deps = [
        ":abstract_future",
    ],
)

sematic_py_lib(
    name = "storage",
    srcs = ["storage.py"],
    deps = [
        ":user_settings",
        requirement("boto3"),
    ],
)

sematic_py_wheel(
    name = "wheel",
    author = "Sematic AI, Inc.",
    author_email = "emmanuel@sematic.ai",
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Visualization",
        "Typing :: Typed",
    ],
    description_file = "//:README.rst",
    distribution = "sematic",
    entry_points = {"console_scripts": ["sematic = sematic.cli.main:cli"]},
    homepage = "https://sematic.dev",
    license = "Apache License 2.0",
    platform = "any",
    python_requires = ">=3.9",
    python_tag = "py3",
    requires = [
        # Specifying this by hand because sematic_py_wheel doesn't know
        # how to fix versions
        "eventlet==0.30.2",
    ],
    version = "0.6.0",  #+{BUILD_TIMESTAMP}",
    visibility = ["//visibility:public"],
    deps = [
        "//sematic:init",
        "//sematic/cli:main_lib",
    ],
)
