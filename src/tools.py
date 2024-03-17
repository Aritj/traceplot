from ipaddress import ip_address, IPv4Address, IPv6Address
from socket import gethostbyname, gethostname, error as socket_error
from requests import get
from typing import Optional, Union
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


def get_ip_from_fqdn(fqdn: str) -> Optional[Union[IPv4Address, IPv6Address]]:
    """Look up the IP address for a fully qualified domain name (FQDN).

    Args:
        fqdn (str): The fully qualified domain name.

    Returns:
        Optional[Union[IPv4Address, IPv6Address]]: The IPv4/v6 address or None if an error occurs.
    """
    # TODO: Improve error handling
    try:
        return ip_address(gethostbyname(fqdn))
    except socket_error:
        return None


def query_geolocation_info(
    ip: Union[IPv4Address, IPv6Address] = "",
) -> Optional[models.GeoLookupResponse]:
    """Query information about an IP address using an external API.

    Args:
        ip Union[IPv4Address, IPv6Address]: The IPv4/v6 address to geolocate.

    Returns:
        Optional[Response]: A response from the API service, otherwise .
    """
    # TODO: Improve error handling
    try:
        # TODO: Introduce mapper classes for different APIs
        return mappers.map_ipwho_response(get(f"http://ipwho.is/{ip}"))
    except Exception as e:
        return None


def get_host_ip() -> Optional[Union[IPv4Address, IPv6Address]]:
    # TODO: Improve error handling
    try:
        return ip_address(gethostbyname(gethostname()))
    except Exception as e:
        return None


def parse_windows_traceroute(traceroute_output: str) -> models.Traceroute:
    """Parse windows traceroute output into a dictionary mapping IP addresses to latencies.
    Args:
        traceroute_output (List[str]): The output from the traceroute command.
    Returns:
        OrderedDict: Mapping from IP addresses to latency lists.
    """
    # pattern = r"\s*(\d+)\s+(\d+\sms|\*)\s+(\d+\sms|\*)\s+(\d+\sms|\*)\s+((?:[a-zA-Z0-9.-]+)?\s*\[?([\d\.]+)\]?)"
    pattern = r"\s*(\d+)\s+(\d+\sms|\*)\s+(\d+\sms|\*)\s+(\d+\sms|\*)\s+([a-zA-Z0-9.-]*(?: \[[\d\.]+\])?)"
    matches: list[list[str]] = findall(pattern, traceroute_output)

    traceroute = models.Traceroute()
    for match in matches:
        print(match)
        _, lat1, lat2, lat3, fqdn_ip = match

        # Extracting and cleaning FQDN and IP
        if " [" in fqdn_ip:  # Checks if there is a DNS name and IP
            fqdn, ip = fqdn_ip.split(" [")
            ip = ip.rstrip("]")
        else:  # Case with no DNS name, only IP
            fqdn, ip = "", fqdn_ip

        latencies = [int(lat.rstrip(" ms")) for lat in [lat1, lat2, lat3] if lat != "*"]

        traceroute.add_hop(
            models.Hop(
                fqdn=fqdn,
                ip_addr=ip_address(ip),
                latencies=latencies,
                geo_info=query_geolocation_info(ip),
            )
        )

    return traceroute


def darwin_traceroute(traceroute_output: str) -> Optional[models.Traceroute]:
    # Regex pattern to extract the required information
    pattern = r"(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+(\d+\.\d+|\*)\s+ms\s+(\d+\.\d+|\*)\s+ms\s+(\d+\.\d+|\*)\s*ms*"

    # Return all matches in the traceroute text (may be None)
    matches: list[list[str]] = findall(pattern, traceroute_output)

    traceroute = models.Traceroute()
    for match in matches:
        fqdn, ip, lat1, lat2, lat3 = match

        traceroute.add_hop(
            models.Hop(
                fqdn=fqdn,
                ip_addr=ip_address(ip),
                latencies=[float(lat1), float(lat2), float(lat3)],
                geo_info=query_geolocation_info(ip),
            )
        )

    return traceroute
