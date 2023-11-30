import aiohttp
import xmltodict
from sanic import response

from exceptions.HTTPNotFoundError import HTTPNotFoundError
from utils.http_utils import HTTP_ALLOW_HEADER, HTTP_SAFE_METHODS, build_wfs_capabilities, \
    convert_to_hyper_resource_entrypoint, get_server_root_path


# https://docs.geoserver.org/main/en/user/services/wfs/reference.html#getcapabilities

async def get_accept_entry_point_header() -> dict[str, str]:
    d = {}
    d[HTTP_ALLOW_HEADER] = ", ".join(HTTP_SAFE_METHODS)
    return d

async def convert_to_hyper_resource_entrypoint_context(request, json_context):

    entrypoint_context = {"@context": {
        "schema": "https://schema.org/",
        "geojson": "https://purl.org/geojson/vocab#"
    }}
    for feature_collection in json_context["wfs:WFS_Capabilities"]["FeatureTypeList"]["FeatureType"]:
        entrypoint_context["@context"].update({feature_collection["Title"]: {
            "@id": "geojson:FeatureCollection",
            "@type": "@id"
        }})
    return entrypoint_context

async def get_entrypoint_context(request, wfs_entrypoint):
    async with aiohttp.ClientSession() as session:
        url = await build_wfs_capabilities(wfs_entrypoint)
        async with session.get(url) as origin_response:
            content = await origin_response.text()
            json_content = xmltodict.parse(content)
            entrypoint_content = await convert_to_hyper_resource_entrypoint_context(request, json_content)
            return response.json(entrypoint_content)

async def get_entrypoint(request, wfs_entrypoint):
    async with aiohttp.ClientSession() as session:
        url = await build_wfs_capabilities(wfs_entrypoint)
        async with session.get(url) as origin_response:
            if origin_response.status == 404:
                raise HTTPNotFoundError
            content = await origin_response.text()
            json_content = xmltodict.parse(content)

            entrypoint_content = await convert_to_hyper_resource_entrypoint(request, json_content)
            headers = await get_entry_point_header(request, wfs_entrypoint)
            return response.json(entrypoint_content, headers=headers)

async def get_entry_point_header(request, wfs_entrypoint):
    _headers = await get_link_entry_point_header(request, wfs_entrypoint)
    d = await get_accept_entry_point_header()
    _headers.update(d)
    return _headers

async def get_link_entry_point_header(request, wfs_entrypoint):
    base_iri = await get_server_root_path(request)
    return {
        'Access-Control-Expose-Headers': 'Link',
        'Link': #f"<{base_iri}>; rel=\"https://schema.org/EntryPoint\", "
                f"<{base_iri}/{wfs_entrypoint}.jsonld>; rel=\"http://www.w3.org/ns/json-ld#context\"; type=\"application/ld+json\""
    }