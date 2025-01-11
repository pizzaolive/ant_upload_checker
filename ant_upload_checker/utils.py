def convert_bytes_to_gb(num_in_bytes: int) -> float:
    """
    Convert bytes to GB
    """
    num_in_gb = round((num_in_bytes / 1073741824), 2)

    return num_in_gb


def convert_milliseconds_to_minutes(num_in_ms: int) -> int:
    """
    Convert milliseconds to minutes
    """
    num_in_minutes = round(num_in_ms / 60000)

    return num_in_minutes


def convert_width_to_resolution(width: int) -> str:
    """
    Convert width of film into common resolution values
    """
    resolution_map = {3840: "2160p", 1920: "1080p", 1280: "720p", 720: "480p"}
    resolution = resolution_map.get(width, None)

    return resolution


def convert_video_codec_format(codec: str) -> str:
    """
    Convert codecs into codecs used by tracker
    """
    codec_map = {"AVC": "H264", "VC-1": "VC-1", "HEVC": "H265"}
    converted_codec = codec_map.get(codec, None)

    if converted_codec is None:
        pause = 1

    return converted_codec
