from typing import Union


def safe_name(id: Union[str, int], unsafe_name: str) -> str:
    """
    Remove unsafe characters from Canvas object names. It's common for course and assignment titles
    to contain spaces, slashes, colons, etc. Also, prepend the ID so that two items with the same name
    don't conflict.
    :param id: Object ID
    :param unsafe_name: Object name, possibly containing illegal characters
    :return: Safe version of the unsafe name with "{ID}_" prepended
    """
    return f"{id}_{unsafe_name.lower().strip().replace(' ', '_').replace('/', '-').replace(':', '').replace('?', '')}"
