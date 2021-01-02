VERSION = (0, 5, 14)


def get_version():
    "Return the version as a human-format string."
    return ".".join([str(i) for i in VERSION])
