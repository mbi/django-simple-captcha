VERSION = (0, 3, 7)


def get_version(svn=False):
    "Returns the version as a human-format string."
    return '.'.join([str(i) for i in VERSION])
