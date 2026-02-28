from packaging.version import Version


def get_version(version=None):
    "Returns a PEP 440-compliant version number from VERSION."
    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # major = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|rc}N - for alpha, beta and rc releases

    major = get_major_version(version)

    sub = ""
    if version[3] != "final":
        mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
        sub = mapping[version[3]] + str(version[4])

    return str(major + sub)


def get_major_version(version=None):
    "Returns major version from VERSION."
    version = get_complete_version(version)
    parts = 3
    major = ".".join(str(x) for x in version[:parts])
    return major


def get_complete_version(version: str | Version | None = None):
    """
    Returns a tuple of the version of Core Arches.
    """
    if version is None:
        from arches import __version__ as version

    if isinstance(version, str):
        version = Version(version)

    if isinstance(version, Version):
        major = version.major
        minor = version.minor
        micro = version.micro
        if version.pre is not None:
            pre_type_mapping = {"a": "alpha", "b": "beta", "rc": "rc"}
            pre_type = pre_type_mapping.get(version.pre[0], version.pre[0])
            pre_num = version.pre[1]
        else:
            pre_type = "final"
            pre_num = 0
        version = (major, minor, micro, pre_type, pre_num)

    return version
