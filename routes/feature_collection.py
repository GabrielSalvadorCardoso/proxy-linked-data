from exceptions.HTTPNotFoundError import HTTPNotFoundError
from resources.entrypoint import get_entrypoint, get_entrypoint_context
from resources.feature_collection import get_feature_collection, get_feature_collection_context

def setup_feature_collection_routes(app):
    @app.get(r"/<wfs_entrypoint:(?P<wfs_entrypoint>https://.*|http://.*)>/<collection_name:str>")
    async def entrypoint_or_feature_collection(request, wfs_entrypoint, collection_name):
        try:
            entrypoint_response = await get_entrypoint(request, wfs_entrypoint)
        except HTTPNotFoundError:
            # http://127.0.0.1:8003/https://geoservicos.ibge.gov.br/geoserver/CCAR/ows/CCAR:BCIM_Capital_P
            return await get_entrypoint(request, f"{wfs_entrypoint}/{collection_name}")

        # http://127.0.0.1:8003/https://geoservicos.ibge.gov.br/geoserver/CCAR/ows
        return await get_feature_collection(request, wfs_entrypoint, collection_name)

    @app.options(r"/<wfs_entrypoint:(?P<wfs_entrypoint>https://.*|http://.*)>/<collection_name:str>")
    async def entrypoint_or_feature_collection_context(request, wfs_entrypoint, collection_name):
        try:
            # http://127.0.0.1:8003/https://geoservicos.ibge.gov.br/geoserver/CCAR/ows/CCAR:BCIM_Capital_Pd
            entrypoint_response = await get_entrypoint(request, wfs_entrypoint)
        except HTTPNotFoundError:
            # http://127.0.0.1:8003/https://geoservicos.ibge.gov.br/geoserver/CCAR/ows
            return await get_entrypoint_context(request, f"{wfs_entrypoint}/{collection_name}")
        return await get_feature_collection_context(request, wfs_entrypoint, collection_name)
