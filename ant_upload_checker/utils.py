def convert_bytes_to_gb(num_in_bytes: int) -> float:
    """
    Convert bytes to GB
    """
    num_in_gb = round((num_in_bytes / 1073741824), 2)

    return num_in_gb
