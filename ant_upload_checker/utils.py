import re


def convert_bytes_to_gb(num_in_bytes: int) -> float:
    """
    Convert bytes to GB
    """
    num_in_gb = round((num_in_bytes / 1073741824), 2)

    return num_in_gb


def convert_milliseconds_to_minutes(milliseconds: int | float | str) -> int:
    """
    Convert milliseconds to minutes
    """
    if type(milliseconds) is str:
        milliseconds = float(milliseconds)

    minutes = round(milliseconds / 60000)

    return minutes


def convert_width_to_resolution(width: int) -> str:
    """
    Convert width of film into common resolution values
    """
    resolution_map = {
        4096: "2160p",
        3840: "2160p",
        1920: "1080p",
        1280: "720p",
        720: "480p",
        640: "360p",
    }
    resolution = resolution_map.get(width, None)

    return resolution


def convert_video_codec_format(codec: str) -> str:
    """
    Convert codecs into codecs used by tracker
    """
    codec_map = {
        "AVC": "H264",
        "H.264": "H264",
        "x264": "H264",
        "H.265": "H265",
        "x265": "H265",
        "HEVC": "H265",
        "VC-1": "VC-1",
        "MPEG Video": "MPEG2",
        "MPEG-4 Visual": "MPEG4",
    }
    converted_codec = codec_map.get(codec, None)

    if not converted_codec:
        pause = 1

    if codec == "MPEG Video":
        pause = 1

    return converted_codec


def normalise_title(title: str) -> str:
    normalised_title = re.sub(r"[^\w\s]", "", title).lower()
    return normalised_title
