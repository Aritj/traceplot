from ipaddress import ip_address, IPv4Address, IPv6Address
from socket import gethostbyname, gethostname, getnameinfo, error as socket_error
from requests import get
from typing import Optional, Union
from functools import reduce
from icmplib import traceroute

import src.models as models
import src.mappers as mappers

def resolve_to_ip(input: str) -> Optional[Union[IPv4Address, IPv6Address]]:
    """
    Takes a string input and checks if it is an IP address or a FQDN (Fully Qualified Domain Name).
    If it is a FQDN, it converts it to an IP address. If it is already an IP address or if the FQDN
    cannot be resolved, it returns None.

    Args:
        input_str (str): The input string which could be an IP address or a FQDN.

    Returns:
        Optional[Union[IPv4Address, IPv6Address]]: The IP address if the input is a valid IP or
        a resolved FQDN, otherwise None.
    """
    # ip_address() will attempt to parse a string or integer - we don't want that.
    if input.isdigit():
        return None

    # Check if input_str is already an IP address
    try:
        # This will raise a ValueError if input_str is not a valid IP address
        return ip_address(input)
    except ValueError:
        # input_str is not an IP address, so we'll assume it's a FQDN
        pass

    # Resolve the FQDN to an IP address
    try:
        return ip_address(gethostbyname(input))
    except socket_error:
        return None


def query_geolocation_info(
    ip: Union[IPv4Address, IPv6Address] = "",
) -> Optional[models.GeoLookupResponse]:
    """Query information about an IP address using an external API.

    Args:
        ip Union[IPv4Address, IPv6Address]: The IPv4 or IPv6 address to geolocate.

    Returns:
        Optional[models.GeoLookupResponse]: A GeoLookupResponse mapped response from the API service, otherwise None.
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


def trace(target_ip: str):
    traceroute_result = traceroute(target_ip, count=10, interval=0.05, timeout=1, first_hop=1, max_hops=30, fast=False)
    trace = models.Traceroute()
    
    for hop in traceroute_result:
        trace.add_hop(
            models.Hop(
                fqdn=getnameinfo((hop.address, 0), 0)[0],
                ip_addr=ip_address(hop.address),
                latencies=hop.rtts,
                geo_info=query_geolocation_info(hop.address),
            )
        )
            
    return trace

def print_info(trace: models.Traceroute) -> None:
    total_distance: int = 0
        
    prev_hop = None
    
    for hop in filter(lambda hop: hop.ip_addr.is_global, trace.hops):
        if not prev_hop:
            prev_hop = hop
        total_distance += hop.distance(prev_hop)
  
    print(f"{trace}")

    c_in_fiber_optics: float =  (2/3) * 299_792.458 #  km/s
    final_latency: float = trace.hops[-1].avg_latency()
    latency_in_seconds: float = final_latency/1000

    print(models.bcolors.WARNING)
    print(f"Total latency:\t\t{round(final_latency, 2):>8} ms")
    print(f"Total distance:\t\t{round(total_distance, 2):>8} km")
    print(f"Calculated distance:\t{round(latency_in_seconds*c_in_fiber_optics,2):>8} km")
    print(models.bcolors.ENDC)

def partition(l, p):
    """
    Partition a list based on a predicate function.

    This function splits a list `l` into two lists: one for elements that satisfy 
    the predicate `p`, and one for elements that do not.

    Parameters:
    l (list): The list to be partitioned.
    p (function): A predicate function that returns True or False for an element of the list.

    Returns:
    tuple: A tuple containing two lists:
        - The first list contains elements that satisfy the predicate `p`.
        - The second list contains elements that do not satisfy the predicate `p`.

    Example:
    >>> partition([1, 2, 3, 4], lambda x: x % 2 == 0)
    ([2, 4], [1, 3])
    """
    return reduce(lambda x, y: x[not p(y)].append(y) or x, l, ([], []))

def convert_to_public_hops(trace: models.Traceroute) -> models.Traceroute:
    public_ip_info = query_geolocation_info()

    # Remove RFC1918 IPs
    public, private = partition(trace.hops, lambda hop: hop.ip_addr.is_global)
    
    public.insert(0, models.Hop(
        fqdn=f"{public_ip_info.fqdn} (Public IP)",
        ip_addr=public_ip_info.ip_addr,
        latencies=private[-1].latencies,
        geo_info=public_ip_info,
    ))
    
    return models.Traceroute(public)

