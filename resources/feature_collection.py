import aiohttp
import xmltodict
from sanic import response

from hyper_resource_utils.utils import get_vocab_prefix, build_supported_operations, build_context
from hyper_resource_utils.utils import build_supported_properties

A = "https://geoservicos.ibge.gov.br/geoserver/CCAR/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=CCAR%3ABCIM_Capital_P&maxFeatures=600000&outputFormat=application%2Fjson"
async def build_feature_collection_url(wfs_entrypoint:str, collection_name:str, maxFeatures=600000) -> str:
    return f"{wfs_entrypoint}?service=WFS&version=1.0.0&request=GetFeature&typeName={collection_name}&maxFeatures={maxFeatures}&outputFormat=application/json"

# https://docs.geoserver.org/main/en/user/services/wfs/reference.html#describefeaturetype
async def build_feature_collection_description_url(wfs_entrypoint:str, collection_name:str) -> str:
    return f"{wfs_entrypoint}?service=wfs&version=2.0.0&request=DescribeFeatureType&typeNames={collection_name}"

async def get_feature_collection(request, wfs_entrypoint, collection_name):
    async with aiohttp.ClientSession() as session:
        # url = await build_wfs_capabilities(wfs_entrypoint)
        # async with session.get(url) as origin_response:
            # content = await origin_response.text()
            # json_content = xmltodict.parse(content)
            # entrypoint_content = await convert_to_hyper_resource_entrypoint(request, json_content)

        feature_collection_url = await build_feature_collection_url(wfs_entrypoint, collection_name)
        async with session.get(feature_collection_url) as origin_response:
            json_content = await origin_response.json()
            return response.json(json_content)

"""
{
    "@context": {
        "geojson": "https://purl.org/geojson/vocab#",
        "Feature": "geojson:Feature",
        "coordinates": {
            "@container": "@list",
            "@id": "geojson:coordinates"
        },
        "type": "@type",
        "id": "@id",
        "geometry": "geojson:geometry",
        "properties": "geojson:properties",
        "hr": "http://hyper-resource.org/core",
        "schema": "http://schema.org/",
        "Point": "geojson:Point",
        "nome": "schema:Text",
        "nomeabrev": "schema:Text",
        "geometriaaproximada": "schema:Text",
        "tipocapital": "schema:Text",
        "id_produtor": "schema:Integer",
        "id_elementoprodutor": "schema:Integer",
        "cd_insumo_orgao": "schema:Integer",
        "nr_insumo_mes": "schema:Integer",
        "nr_insumo_ano": "schema:Integer",
        "tx_insumo_documento": "schema:Text",
        "FeatureCollection": "geojson:FeatureCollection",
        "features": {
            "@container": "@set",
            "@id": "geojson:features"
        }
    },
"""

XML_SCHEMA_REF = "http://www.w3.org/2001/XMLSchema#"


async def get_vocab(json_content):
    vocab_prefix = await get_vocab_prefix(json_content)
    return json_content[f"@xmlns:{vocab_prefix}"] + "#"

# https://docs.geoserver.org/2.23.x/en/user/services/wfs/schemamapping.html
# Geoserver usas XML Schema by default

# https://metadados.inde.gov.br/geonetwork/srv/por/csw?service=CSW&version=2.0.2&request=GetRecordById&elementSetName=full&outputSchema=csw:IsoRecord&id=9accb45f-23f2-488c-9ff7-1acdbf514376
async def get_feature_collection_context(request, wfs_entrypoint, collection_name):
    url = await build_feature_collection_description_url(wfs_entrypoint, collection_name)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as origin_response:
            xml_content = await origin_response.text()
            json_content = xmltodict.parse(xml_content)
            context_content = {}
            acontexts = await build_context(json_content)
            supported_properties = await build_supported_properties(json_content)
            supported_operations = await build_supported_operations(json_content)
            context_content.update(acontexts)
            context_content.update(supported_properties)
            context_content.update(supported_operations)
            context_content.update({"@type": "FeatureCollection"})
            return response.json(context_content)