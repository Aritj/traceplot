from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Tuple, Union
from typing_extensions import Self
from math import radians, sin, cos, asin, sqrt


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
        latencies: list[float],
        geo_info: Optional[GeoLookupResponse],
    ):
        self.fqdn = fqdn
        self.ip_addr = ip_addr
        self.latencies = latencies
        self.geo_info = geo_info

    def __repr__(self) -> str:
        return f"{self.fqdn:<40} ({str(self.ip_addr):>15}) {' '.join([f'{lat:>10} ms' for lat in self.latencies])}"

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
        if not hop:
            return 0

        # Radius of Earth in kilometers. Use 3956 for miles
        EARTH_RADIUS_KM: int = 6378
        ADJUSTMENT_SCALAR: float = 1.2  # Account for non-straight lines.

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [*self.get_coords(), *hop.get_coords()])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
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

    def is_empty(self) -> bool:
        return len(self.hops) == 0

    def print_info(self):
        total_distance: int = 0
        prev_latency: float = 0.0

        print_len = 80

        print(f"+{'-'* print_len}+")
        prev_hop = None
        for hop in self.hops:
            avg_latency = hop.avg_latency()

            if not prev_hop:
                prev_hop = hop
                continue

            if all([hop.ip_addr.is_global, prev_hop.ip_addr.is_global]):
                distance = hop.calculate_distance(prev_hop)
                delta_latency = avg_latency - prev_latency
                print(
                    f"| {str(prev_hop.ip_addr):<16} - {round(avg_latency, 1):<5}ms -> {str(hop.ip_addr):<16} (Δkm: {round(distance, 1):>7}km | Δms: {round(delta_latency, 1):>5}ms) |"
                )
                total_distance += distance
            else:
                print(
                    f"| {str(prev_hop.ip_addr):<16} - {round(avg_latency, 1):<5}ms -> {str(hop.ip_addr):<16} (Δkm: {'N/A':^7}km | Δms: {round(avg_latency - prev_latency, 1):>5}ms) | {bcolors.WARNING} RFC1918 IPs not geolocatable. {bcolors.ENDC}"
                )

            prev_latency = avg_latency
            prev_hop = hop
        print(f"+{'-' * print_len}+")
        print(f"Total distance:\t{round(total_distance, 2):>7} km")
        print(f"Total latency:\t{round(prev_latency, 1):>7} ms")

    def contains_ip(self, ip: Union[IPv4Address, IPv6Address]):
        return any([str(hop.ip_addr) == str(ip) for hop in self.hops])

    def __repr__(self) -> str:
        return "\n".join([f"{i:>2}  {hop}" for i, hop in enumerate(self.hops)])
