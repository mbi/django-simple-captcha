VERSION = (0, 5, 17)


def get_version():
    "Return the version as a human-format string."
    return ".".join([str(i) for i in VERSION])
