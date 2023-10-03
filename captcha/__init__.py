VERSION = (0, 5, 19)


def get_version():
    "Return the version as a human-format string."
    return ".".join([str(i) for i in VERSION])
