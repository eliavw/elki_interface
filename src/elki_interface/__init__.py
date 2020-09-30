# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound
from requests import get  # to make GET request


def _download_elki(
    url=None,
    filepath=None,
):

    # open in binary mode
    with open(filepath, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)
    return


try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version

    from .cte import ELKI_FILEPATH, ELKI_URL

    # download elki jar, if necessary
    if not ELKI_FILEPATH.exists():
        _download_elki(
            url=ELKI_URL,
            filepath=ELKI_FILEPATH,
        )

    # imports
    from .Hics import Hics

except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound
