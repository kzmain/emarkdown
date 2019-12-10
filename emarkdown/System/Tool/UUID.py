import uuid

prefix = "emddme"
suffix = "emddme"


def get_new_uuid():
    return prefix + str(uuid.uuid4()) + suffix


def get_regx_uuid():
    return r"%s(([0-9]|[a-z]){8}-)(([0-9]|[a-z]){4}-){3}(([0-9]|[a-z]){12})%s" % (prefix, suffix)


def get_regx_paragraph():
    return r"^(?!((\n)?^%s(([0-9]|[a-z]){8}-)(([0-9]|[a-z]){4}-){3}(([0-9]|[a-z]){12})%s$))((\n)?(.+))+" \
           % (prefix, suffix)
