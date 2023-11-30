XML_SCHEMA_COMPLEX_TYPE_LABEL = "complexType"
XML_SCHEMA_COMPLEX_CONTENT_LABEL = "complexContent"
XML_SCHEMA_EXTENSION_LABEL = "extension"
XML_SCHEMA_SEQUENCE_LABEL = "sequence"
XML_SCHEMA_ELEMENT_LABEL = "element"
XML_SCHEMA_ELEMENT_NAME_ATTR_LABEL = "name"
XML_SCHEMA_ELEMENT_NULLABLE_ATTR_LABEL = "nillable"
XML_SCHEMA_ELEMENT_TYPE_ATTR_LABEL = "type"

async def build_supported_operations(json_content):
    """
    :param json_content:
    :return:
    "hr:supportedOperations": [
         {
            "@type": "hr:Operation",
            "hydra:method": "GET",
            "hr:appendPath": "/within/{param0}",
            "hr:parameters": [
                {
                    "@type": "hr:OperationParameter",
                    "hr:variable": "param0",
                    "hr:requiredParameter": true,
                    "hydra:expects": "geojson:Geometry",
                    "hr:expectsSerialization": [
                        "text/plain",
                        "application/geo+json"
                    ]
                }
            ],
            "hydra:returnsHeader": [
                {
                    "hydra:headerName": "Content-Type",
                    "hydra:possibleValue": [
                        "application/geo+json",
                        "image/png"
                    ]
                }
            ],
            "hydra:expectsHeader": [
                {
                    "hydra:headerName": "Content-Type",
                    "hydra:possibleValue": [
                        "application/geo+json",
                        "image/png"
                    ]
                }
            ],
            "hydra:possibleStatus": [
                200
            ]
        },
        ...
    ]"""
    return {"hr:supportedOperations": []}

async def build_supported_properties(json_content):
    """
    :param json_content:
    :return:
    "hr:supportedProperties": [
        {
            "@type": "hydra:SupportedProperty",
            "hydra:property": "id_objeto",
            "hydra:required": true,
            "hydra:readable": true,
            "hydra:writable": false,
            "hr:isExternal": false
        },
        ...
    ]
    """
    supportedProperties = []
    vocab_prefix = await get_vocab_prefix(json_content)
    container_tag = await get_container_tag(json_content)
    properties = await get_properties(container_tag, json_content, vocab_prefix)
    for prop in properties:

        if not prop[f"@{XML_SCHEMA_ELEMENT_TYPE_ATTR_LABEL}"].startswith(vocab_prefix):
            continue
        supportedProperties.append({
            "@type": "hydra:SupportedProperty",
            "hydra:property": prop[f"@{XML_SCHEMA_ELEMENT_NAME_ATTR_LABEL}"],
            "hydra:required": not prop[f"@{XML_SCHEMA_ELEMENT_NULLABLE_ATTR_LABEL}"] == "true",
            "hydra:readable": True,
            "hydra:writable": False,
            "hr:isExternal": False
        })
    return {"hr:supportedProperties": supportedProperties}


async def get_properties(container_tag, json_content, vocab_prefix):
    return json_content[container_tag] \
        [f"{vocab_prefix}:{XML_SCHEMA_COMPLEX_TYPE_LABEL}"] \
        [f"{vocab_prefix}:{XML_SCHEMA_COMPLEX_CONTENT_LABEL}"] \
        [f"{vocab_prefix}:{XML_SCHEMA_EXTENSION_LABEL}"] \
        [f"{vocab_prefix}:{XML_SCHEMA_SEQUENCE_LABEL}"] \
        [f"{vocab_prefix}:{XML_SCHEMA_ELEMENT_LABEL}"]


async def build_context(json_content):
    """

    :param json_content:
    :return: {
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
        }
    }
    """
    context = {
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
            "FeatureCollection": "geojson:FeatureCollection",
            "features": {
                "@container": "@set",
                "@id": "geojson:features"
            }
        }
    }
    vocab_prefix = await get_vocab_prefix(json_content)
    vocab_ref = await get_vocab_ref(json_content)
    container_tag = await get_container_tag(json_content)
    properties = await get_properties(container_tag, json_content, vocab_prefix)

    for prop in properties:

        if not prop[f"@{XML_SCHEMA_ELEMENT_TYPE_ATTR_LABEL}"].startswith(vocab_prefix):
            continue

        try:
            term = {
                prop[f"@{XML_SCHEMA_ELEMENT_NAME_ATTR_LABEL}"]: convert_to_schema_org_term(prop[f"@{XML_SCHEMA_ELEMENT_TYPE_ATTR_LABEL}"].split(f"{vocab_prefix}:")[-1])
            }
        except KeyError:
            context["@context"][vocab_prefix] = vocab_ref

            term = {
                prop[f"@{XML_SCHEMA_ELEMENT_NAME_ATTR_LABEL}"]: prop[f"@{XML_SCHEMA_ELEMENT_TYPE_ATTR_LABEL}"]
            }

        context["@context"].update(term)
    return context

def convert_to_schema_org_term(xml_schema_term):
    d = {
        "int": "schema:Integer",
        "string": "schema:Text"
    }
    return d[xml_schema_term]

async def get_container_tag(json_content):
    container_tag = list(json_content.keys())[0]
    return container_tag

async def get_vocab_ref(json_content):
    container_tag = await get_container_tag(json_content)
    vocab_prefix = await get_vocab_prefix(json_content)
    return json_content[container_tag][f"@xmlns:{vocab_prefix}"]

async def get_vocab_prefix(json_content):
    container_tag = await get_container_tag(json_content)
    vocab_prefix = container_tag.split(":")[0]
    return vocab_prefix
