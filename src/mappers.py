from requests import Response
from ipaddress import ip_address
import src.models as models


def map_ipwho_response(ipwho_response: Response):
    data = ipwho_response.json()

    return models.GeoLookupResponse(
        fqdn=data["connection"]["domain"],
        ip_type=data["type"],
        ip_addr=ip_address(data["ip"]),
        continent=data["continent"],
        continent_code=data["continent_code"],
        country=data["country"],
        country_code=data["country_code"],
        city=data["city"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        isp_asn=data["connection"]["asn"],
        isp_name=data["connection"]["isp"],
        org=data["connection"]["org"],
    )
