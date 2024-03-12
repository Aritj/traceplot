from ipaddress import ip_address, IPv4Address, IPv6Address
from socket import gethostbyname, gethostname, error as socket_error
from requests import get, Response
from typing import Optional
from re import findall
from platform import system

import src.models as models
import src.mappers as mappers

def get_os_name() -> str:
    """Calls platform.system().
    
    Returns:
        str: Returns the OS name as a string, such as 'Linux', 'Darwin', 'Java', 'Windows'.
    """
    return system()

def get_ip_from_fqdn(fqdn: str) -> Optional[(IPv4Address | IPv6Address)]:
    """Look up the IP address for a fully qualified domain name (FQDN).

    Args:
        fqdn (str): The fully qualified domain name.

    Returns:
        Optional[(IPv4Address | IPv6Address)]: The IPv4/v6 address or None if an error occurs.
    """
    # TODO: Improve error handling
    try:
        return ip_address(gethostbyname(fqdn))
    except socket_error:
        return None

def query_geolocation_info(ip: (IPv4Address | IPv6Address)) -> Optional[models.GeoLookupResponse]:
    """Query information about an IP address using an external API.

    Args:
        ip (IPv4Address | IPv6Address): The IPv4/v6 address to geolocate.

    Returns:
        Optional[Response]: A response from the API service, otherwise .
    """
    # TODO: Improve error handling
    try:
        # TODO: Introduce mapper classes for different APIs
        return mappers.map_ipwho_response(get(f"http://ipwho.is/{ip}"))
    except Exception as e:
        return None

def get_host_ip() -> Optional[(IPv4Address | IPv6Address)]:
    # TODO: Improve error handling
    try:
        return ip_address(gethostbyname(gethostname()))
    except Exception as e:
        return None

def get_public_ip() -> Optional[(IPv4Address | IPv6Address)]:
    """Get the public IP address of the current machine.

    Returns:
        Optional[(IPv4Address | IPv6Address)]: The public IPv4/v6 address, or None.
    """
    # TODO: Improve error handling
    try:
        return ip_address(get("https://api.ipify.org?format=json").json()["ip"])
    except Exception as e:
        return None
    
def parse_windows_traceroute(traceroute_text: str) -> Optional[models.Traceroute]:
    # TODO: re-do windows parsing.
    pass

def darwin_traceroute(traceroute_text: str) -> Optional[models.Traceroute]:
    # Regex pattern to extract the required information
    pattern = r"(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+(\d+\.\d+|\*)\s+ms\s+(\d+\.\d+|\*)\s+ms\s+(\d+\.\d+|\*)\s*ms*"
    
    # Return all matches in the traceroute text (may be None)
    return convert_to_model(findall(pattern, traceroute_text))

def convert_to_model(parsed_traceroute: list[str]) -> Optional[models.Traceroute]:
    traceroute = models.Traceroute()
    
    for hop in parsed_traceroute:
        fqdn, ip, lat1, lat2, lat3 = hop
        
        traceroute.add_hop(models.Hop(
            fqdn = fqdn,
            ip_addr = ip_address(ip),
            latencies = [float(lat1), float(lat2), float(lat3)],
            geo_info = query_geolocation_info(ip)
        ))
    
    return traceroute