import os
from sanic import Sanic
from environs import Env

from routes.entrypoint import setup_entrypoint_routes

OWS_SERVER = "https://geoservicos.ibge.gov.br/geoserver/CCAR/ows"
IBGE_BCIM_CAPITAL_URL = f"{OWS_SERVER}?service=WFS&version=1.0.0&request=GetFeature&typeName=CCAR:BCIM_Capital_P&maxFeatures=600000&outputFormat=application/json"



"""
# REFERENCE: https://docs.geoserver.org/main/en/user/services/wfs/reference.html
SERVIDOR (informado pelo cliente): https://geoservicos.ibge.gov.br
PATH (informado pelo cliente) /geoserver/CCAR/ows?
QUERY PARAMETERS: FIXO (para que seja possivel a conversao para REST, precisa ser chave/valor): service=WFS&
                  FIXO version=1.0.0&
                  FIXO (no caso de uma requisicao GET) request=GetFeature&
                  NOME DA CAMADA (informado pelo cliente) typeName=CCAR:BCIM_Capital_P&
                  PAGINAÇÃO: (o proxy decide se fara ou nao): maxFeatures=600000&
                  ACCEPT: outputFormat=application/json"

REQUISIÇÃO REST/HYPER RESOURCE VINDA DO CLIENTE
GET https://geoservicos.ibge.gov.br/geoserver/CCAR/ows
Accept: application/geo+json
"""

env = Env()
env.read_env(os.path.join(".env"))

app = Sanic.get_app(
    "ProxyLinkedData",
    force_create=True,
)

setup_entrypoint_routes(app)

if __name__ == "__main__":
    app.run(port=env.int("SERVER_PORT", 8003))