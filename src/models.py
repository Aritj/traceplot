from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Tuple, Union
from typing_extensions import Self, List
from math import radians, sin, cos, asin, sqrt

import json

class bcolors:
    # https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class GeoLookupResponse:
    def __init__(
        self,
        fqdn: str,
        ip_type: str,
        ip_addr: Union[IPv4Address, IPv6Address],
        continent: str,
        continent_code: str,
        country: str,
        country_code: str,
        city: str,
        latitude: float,
        longitude: float,
        isp_asn: int,
        isp_name: str,
        org: str,
    ):
        self.fqdn = fqdn
        self.ip_type = ip_type
        self.ip_addr = ip_addr
        self.continent = continent
        self.continent_code = continent_code
        self.country = country
        self.country_code = country_code
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.isp_asn = isp_asn
        self.isp_name = isp_name
        self.org = org


class Hop:
    def __init__(
        self,
        fqdn: str,
        ip_addr: Union[IPv4Address, IPv6Address],
        latencies: List[float],
        geo_info: Optional[GeoLookupResponse],
    ):
        self.fqdn = fqdn
        self.ip_addr = ip_addr
        self.latencies = latencies
        self.geo_info = geo_info

    def get_coords(self) -> Optional[Tuple[float, float]]:
        if not self.geo_info:
            return None
        return (self.geo_info.latitude, self.geo_info.longitude)
    
    def min_latency(self, ndigits = 2) -> float:
        return round(min(self.latencies), ndigits)

    def avg_latency(self, ndigits = 2) -> float:
        return round(sum(self.latencies) / len(self.latencies), ndigits)
    
    def max_latency(self, ndigits = 2) -> float:
        return round(max(self.latencies), ndigits)

    def calculate_latency(self, hop: Self, ndigits = 2) -> float:
        return round(self.avg_latency() - hop.avg_latency(), ndigits)

    def distance(self, hop: Self) -> Optional[float]:
        """Calculate the geographical distance between two points on the Earth.

        Args:
            hop: Hop to calculate the distance to.

        Returns:
            float: The geographical distance between the two hops in kilometers.
        """
        if not hop:
            return 0

        # Radius of Earth in kilometers
        EARTH_RADIUS_KM: int = 6378
        ADJUSTMENT_SCALAR: float = 1.2  # assuming non-straight lines

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [*self.get_coords(), *hop.get_coords()])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        haversine_term = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        
        return (2 * asin(sqrt(haversine_term)) * EARTH_RADIUS_KM) * ADJUSTMENT_SCALAR


class Traceroute:
    hops: List[Hop] = []
    
    def toJSON(self):
        return dict(self.hops)

    def add_hop(self, hop: Hop):
        self.hops.append(hop)

    def insert_hop(self, index: int, hop: Hop):
        self.hops.insert(index, hop)

    def remove_hop(self, hop: Hop):
        self.hops.remove(hop)

    def is_empty(self) -> bool:
        return len(self.hops) == 0

    def contains_ip(self, ip: Union[IPv4Address, IPv6Address]):
        return any([str(hop.ip_addr) == str(ip) for hop in self.hops])

    def __init__(self, hops: List[Hop] = []) -> None:
        self.hops = hops

    def __repr__(self) -> str:
        trace: str = f"Hop {'FQDN (IP)':<68} Latency  (count)"
        
        for i, hop in enumerate(self.hops):
            trace += f"\n{i:>3} {hop.fqdn:<50} {f'({str(hop.ip_addr)})':>17} {round(hop.avg_latency(),2):>5} ms (n={len(hop.latencies)})"

        return trace
