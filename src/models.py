from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Tuple
from typing_extensions import Self
from math import radians, sin, cos, asin, sqrt

class GeoLookupResponse:
    def __init__(
        self,
        fqdn: str,
        ip_type: str,
        ip_addr: (IPv4Address | IPv6Address),
        continent: str,
        continent_code: str,
        country: str,
        country_code: str,
        city: str,
        latitude: float,
        longitude: float,
        isp_asn: int,
        isp_name: str,
        org: str
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
            ip_addr: (IPv4Address | IPv6Address), 
            latencies: list[float],
            geo_info: Optional[GeoLookupResponse]
        ):
        self.fqdn = fqdn
        self.ip_addr = ip_addr
        self.latencies = latencies
        self.geo_info = geo_info

    def __repr__(self) -> str:
        return f"{self.fqdn} ({self.ip_addr}) {' '.join([f'{lat} ms' for lat in self.latencies])}"
    
    def get_coords(self) -> Optional[Tuple[float, float]]:
        if not self.geo_info:
            return None
        return (self.geo_info.latitude, self.geo_info.longitude)

    def avg_latency(self) -> float:
        return sum(self.latencies) / len(self.latencies)
    
    def calculate_latency(self, hop: Self) -> float:
        return self.avg_latency() - hop.avg_latency()
    
    def calculate_distance(self, hop: Self) -> Optional[float]:
        """Calculate the geographical distance between two points on the Earth.

        Args:
            hop: Hop to calculate the distance to.

        Returns:
            float: The geographical distance between the two hops in kilometers.
        """
        # Radius of Earth in kilometers. Use 3956 for miles
        EARTH_RADIUS_KM: int = 6378
        ADJUSTMENT_SCALAR: float = 1.2  # Account for non-straight lines.

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [*self.get_coords(), *hop.get_coords()])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2)
        c = 2 * asin(sqrt(a))

        return (c * EARTH_RADIUS_KM) * ADJUSTMENT_SCALAR

class Traceroute:
    hops: list[Hop] = []
    
    def add_hop(self, hop: Hop):
        self.hops.append(hop)
    
    def insert_hop(self, index: int, hop: Hop):
        self.hops.insert(index, hop)
        
    def remove_hop(self, hop: Hop):
        self.hops.remove(hop)
    
    def contains_ip(self, ip: (IPv4Address | IPv6Address)):
        return any([str(hop.ip_addr) == str(ip) for hop in self.hops])
    
    def __repr__(self) -> str:
        return "\n".join([f"{i:>2}  {hop}" for i, hop in enumerate(self.hops)])