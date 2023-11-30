from resources.entrypoint import get_entrypoint, get_entrypoint_context

# http://127.0.0.1:8003/https://geoservicos.ibge.gov.br/geoserver/CCAR/ows
def setup_entrypoint_routes(app):
    @app.get(r"/<wfs_entrypoint:(?P<wfs_entrypoint>https://.*|http://.*)>")
    async def entrypoint(request, wfs_entrypoint):
        return await get_entrypoint(request, wfs_entrypoint)

    @app.options(r"/<wfs_entrypoint:(?P<wfs_entrypoint>https://.*|http://.*)>")
    async def entrypoint_context(request, wfs_entrypoint):
        return await get_entrypoint_context(request, wfs_entrypoint)