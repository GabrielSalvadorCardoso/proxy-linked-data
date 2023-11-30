HTTP_SAFE_METHODS = ["GET", "HEAD", "OPTIONS"]
HTTP_ALLOW_HEADER = "Allow"

async def build_wfs_capabilities(wfs_entrypoint):
    CAPABILITIES_URL = f"{wfs_entrypoint}?service=wfs&version=1.1.0&request=GetCapabilities"
    return CAPABILITIES_URL

async def convert_to_hyper_resource_entrypoint(request, json_content):
    server_root_path = await get_server_root_path(request)
    entrypoint_content = {}
    for feature_collection in json_content["wfs:WFS_Capabilities"]["FeatureTypeList"]["FeatureType"]:
        # entrypoint_content[feature_collection["Title"]] # metadata
        entrypoint_content[feature_collection["Title"]] = f'{server_root_path}{request.path}/{feature_collection["Name"]}'
    return entrypoint_content

async def get_server_root_path(request):
    port = "" if request.server_port in [80, 443] else f":{request.server_port}"
    return f"{request.scheme}://{request.server_name}{port}"