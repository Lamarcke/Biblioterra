from fastapi import APIRouter, Depends, Response, Request
from models.response_models import MetadataResponse, IndexesResponse
from models.query_models import ValidTopics
from functions.metadata_functions import get_cover, get_metadata
from functions.search_index_functions import get_search_index

router = APIRouter(
    prefix="/v1"
)


@router.get("/cover/{md5}", tags=["metadata"])
async def get_cover_by_md5(md5: str, response: Response):
    """
    Gets a cover link using the file's md5.  <br>
    It's recommended to use search's md5 values, because they are valid md5 that you know are in Libgen database.  <br>
    Returns 429 error code if a user exceeds the 1 request / second limit. <br>
    Requests are cached for 2 weeks by default. If it's cached, the "Cached" header will be true.
    """

    results_handler = await get_cover(md5)
    results = results_handler[0]
    response.headers["Cached"] = results_handler[1]
    return results


@router.get("/metadata/{topic}/{md5}", tags=["metadata"], response_model=MetadataResponse)
async def get_metadata_by_md5_and_topic(topic: ValidTopics, md5: str, request: Request, response: Response):
    """
    Given a valid topic and a md5, searches for a file's direct download links and description. <br>
    These values are retrived from Librarylol. <br>
    Rate-limits for this endpoint are severe because this is their main download provider. <br>
    Returns 429 error code if a user exceeds the 1 request / second limit. <br>
    Requests are cached for 72 hours by default. If it's cached, the "Cached" header will be true.
    """

    metadata_handler = await get_metadata(topic, md5)
    response.headers["Cached"] = metadata_handler[1]
    metadata_results: tuple = metadata_handler[0]
    # get_metadata returns a tuple with the download links and description.
    results = {
        "download_links": metadata_results[0],
        "description": metadata_results[1],
    }
    return results


@router.get("/indexes/{topic}", tags=["metadata"])
async def get_search_indexes(topic: ValidTopics):
    """
    Returns all saved search indexes as a list.
    :return: list
    """
    indexes = await get_search_index(topic)
    return {"indexes": indexes}
