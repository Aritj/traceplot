import re
import sys
import socket
import subprocess
from collections import OrderedDict
import requests
import math
import platform
import ipaddress
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import networkx as nx  # Import NetworkX for plotting network graphs
import json
from typing import Optional, Tuple, Dict, List


def load_config() -> Dict[str, str]:
    """Load configuration from a JSON file.

    Returns:
        dict: Configuration data.

    Raises:
        SystemExit: If config.json file is not found or there is a JSON decoding error.
    """
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("config.json file not found.")
        sys.exit()
    except json.JSONDecodeError:
        print("Error decoding config.json.")
        sys.exit()


def avg(input_list: list[float]) -> float:
    """Returns the mean value of a list of numbers

    Args:
        input_list (list[float]): The list of numbers.

    Returns:
        float: The mean value.
    """
    return sum(input_list) / len(input_list)


def lookup_ip(fqdn: str) -> Optional[str]:
    """Look up the IP address for a fully qualified domain name (FQDN).

    Args:
        fqdn (str): The fully qualified domain name.

    Returns:
        Optional[str]: The IP address or None if an error occurs.
    """
    try:
        return socket.gethostbyname(fqdn)
    except socket.error:
        return None


def get_public_ip() -> ipaddress.IPv4Address:
    """Get the public IP address of the current machine.

    Returns:
        ipaddress.IPv4Address: The public IP address.
    """
    data = requests.get("https://api.ipify.org?format=json").json()
    return ipaddress.IPv4Address(data["ip"])


def parse_latency(latency_measurement: str) -> Optional[int]:
    """Parse latency measurement string and return the integer value.

    Args:
        latency_measurement (str): The latency measurement string.

    Returns:
        Optional[int]: The latency in milliseconds, or None if parsing fails.
    """
    try:
        return int(latency_measurement[:-2])  # Remove 'ms' and convert to integer
    except ValueError:
        return None


def parse_windows_traceroute(
    traceroute_output: List[str],
) -> OrderedDict[ipaddress.IPv4Address, List[int]]:
    """Parse windows traceroute output into a dictionary mapping IP addresses to latencies.

    Args:
        traceroute_output (List[str]): The output from the traceroute command.

    Returns:
        OrderedDict: Mapping from IP addresses to latency lists.
    """
    pattern = re.compile(
        r"\s*(\d+)\s+(\d+\sms|\*)\s+(\d+\sms|\*)\s+(\d+\sms|\*)\s+([\d\.]+)"
    )
    traceroute_dict: OrderedDict[ipaddress.IPv4Address, List[int]] = OrderedDict()

    for line in traceroute_output:
        match = pattern.match(line)
        if not match:
            continue  # Skip lines that do not match the pattern

        _, lat1, lat2, lat3, ip = match.groups()
        traceroute_dict[ipaddress.IPv4Address(ip)] = [
            parse_latency(lat) for lat in [lat1, lat2, lat3] if lat != "*"
        ]

    return traceroute_dict

def parse_darwin_traceroute(
    traceroute_output: List[str],
) -> OrderedDict[ipaddress.IPv4Address, List[int]]:
    """Parse MacOS (Darwin) traceroute output into a dictionary mapping IP addresses to latencies.

    Args:
        traceroute_output (List[str]): The output from the traceroute command.

    Returns:
        OrderedDict: Mapping from IP addresses to latency lists.
    """
    pattern = re.compile(r"^\s*(\d+)\s+([\d\.]+)\s+(\d+\.\d+|\*)\s+ms\s+(\d+\.\d+|\*)\s+ms\s+(\d+\.\d+|\*)\s+ms")
    traceroute_dict: OrderedDict[ipaddress.IPv4Address, List[int]] = OrderedDict()

    for line in traceroute_output:
        match = pattern.match(line)

        if not match:
            continue  # Skip lines that do not match the pattern

        _, ip, lat1, lat2, lat3 = match.groups()
        traceroute_dict[ipaddress.IPv4Address(ip)] = [
            float(lat) for lat in [lat1, lat2, lat3] if lat != "*"
        ]

    return traceroute_dict

def traceroute(ip: str) -> Dict[ipaddress.IPv4Address, List[int]]:
    """Perform a traceroute to the specified IP address and return the results.

    Args:
        ip (str): The IP address to traceroute to.

    Returns:
        dict: A dictionary mapping from IP addresses to latency lists.
    """
    os_traceroute_dict = {
        "windows": ["tracert", "-d", "-w", "1", ip],
        "darwin": ["traceroute", "-I", "-n", "-w1", ip]
    }

    hop_dict: Dict[ipaddress.IPv4Address, List[int]] = {}
    os_name: str = platform.system().lower()

    try:
        traceroute_output = subprocess.run(
            os_traceroute_dict[os_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )
        traceroute_lines = traceroute_output.stdout.split("\n")
    except subprocess.TimeoutExpired:
        print("Traceroute command timed out")
        return hop_dict

    if os_name == "windows":
        return parse_windows_traceroute(traceroute_lines)
    
    if os_name == "darwin":
        return parse_darwin_traceroute(traceroute_lines)

    # TODO: implement parsing for Linux/Mac
    print(f"{os_name} trace route parsing not implemented.")
    sys.exit()


def get_coordinates(API_KEY: str, ip: ipaddress.IPv4Address) -> Tuple[float, float]:
    """Get geographical coordinates for an IP address using an external API.

    Args:
        API_KEY (str): The API key for the IP geolocation service.
        ip (ipaddress.IPv4Address): The IP address to geolocate.

    Returns:
        tuple: A tuple containing the latitude and longitude.
    """
    response = requests.get(
        f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={str(ip)}"
    ).json()

    return round(float(response["latitude"]), 2), round(float(response["longitude"]), 2)


def calculate_distance(
    coord1: Tuple[float, float], coord2: Tuple[float, float]
) -> float:
    """Calculate the geographical distance between two points on the Earth.

    Args:
        coord1 (Tuple[float, float]): The first coordinate (latitude, longitude).
        coord2 (Tuple[float, float]): The second coordinate (latitude, longitude).

    Returns:
        float: The distance between the two points in kilometers.
    """
    # Radius of Earth in kilometers. Use 3956 for miles
    EARTH_RADIUS_KM: int = 6378
    ADJUSTMENT_SCALAR: float = 1.2  # Account for non-straight lines.

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [*coord1, *coord2])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return (c * EARTH_RADIUS_KM) * ADJUSTMENT_SCALAR


def plot_public_ips(
    hop_coords: Dict[ipaddress.IPv4Address, Tuple[float, float]]
) -> None:
    """Plot public IP addresses on a world map.

    Args:
        hop_coords (Dict[ipaddress.IPv4Address, Tuple[float, float]]): Dictionary mapping IP addresses to geographic coordinates.
    """
    projection = ccrs.PlateCarree()
    plt.figure(figsize=(15, 10))
    ax = plt.axes(projection=projection)
    ax.coastlines()

    # Determine the map's extent
    lats, lons = zip(*hop_coords.values())
    buffer = 10  # Add a buffer to the edges of the map
    ax.set_extent(
        [
            max(-180, min(lons) - buffer),
            min(180, max(lons) + buffer),
            max(-90, min(lats) - buffer),
            min(90, max(lats) + buffer),
        ],
        crs=projection,
    )

    # Plot hops with unique colors
    cmap = plt.get_cmap("viridis")
    for i, (hop, (lat, lon)) in enumerate(hop_coords.items()):
        ax.plot(
            lon,
            lat,
            "o",
            color=cmap(i / len(hop_coords)),
            markersize=10,
            transform=ccrs.Geodetic(),
            label=f"Hop {i + 1}",
        )

    # Connect hops with lines
    prev_hop = None
    for hop, (lat, lon) in hop_coords.items():
        if prev_hop:
            prev_lat, prev_lon = prev_hop
            ax.plot(
                [prev_lon, lon],
                [prev_lat, lat],
                "-",
                color="black",
                transform=ccrs.Geodetic(),
            )
        prev_hop = (lat, lon)

    ax.legend(hop_coords.keys())
    plt.title("Traceroute Hops (source: ipgeolocation.io)")
    plt.show()


def plot_network(hop_coords: Dict[ipaddress.IPv4Address, Tuple[float, float]]) -> None:
    """Plot a network graph of traceroute hops.

    Args:
        hop_coords (Dict[ipaddress.IPv4Address, Tuple[float, float]]): Dictionary mapping IP addresses to geographic coordinates.
    """
    # Create a new directed graph
    G = nx.DiGraph()
    hops = list(hop_coords.keys())

    # Add nodes with the hop number as the node label
    for i, hop in enumerate(hops, start=1):
        G.add_node(i, label=str(hop))

    # Add edges between sequential hops
    for i in range(1, len(hops)):
        G.add_edge(i, i + 1)

    # Set up the plot layout
    pos = nx.spring_layout(G, seed=42)  # For consistent layout between runs
    plt.figure(figsize=(10, 5))
    plt.title("Logical Network Architecture from Traceroute")

    # Draw the network
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=["red" if hop.is_private else "green" for hop in hops],
        node_size=2000,
        edge_color="k",
        linewidths=1,
        font_size=12,
        arrows=True,
        arrowsize=20,
    )

    # Draw node labels (IP addresses)
    label_pos = {key: [value[0], value[1] + 0.1] for key, value in pos.items()}
    labels = nx.get_node_attributes(G, "label")
    nx.draw_networkx_labels(G, label_pos, labels, font_size=10)

    # Create a custom legend
    private_legend = plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Private (RFC1918) IPs",
        markersize=10,
        markerfacecolor="red",
        linestyle="None",
    )
    public_legend = plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Public IPs",
        markersize=10,
        markerfacecolor="green",
        linestyle="None",
    )
    plt.legend(handles=[private_legend, public_legend], loc="upper right")

    plt.axis("off")  # Turn off the axis
    plt.show()


def main(target: str) -> None:
    """Main function to perform traceroute and visualize the results.

    Args:
        target (str): IP address or domain to traceroute to.
    """
    config = load_config()
    API_KEY = config.get("API_KEY")
    if not API_KEY:
        print("API key not found in config.json.")
        sys.exit()
    target_ip = lookup_ip(target) if not target.replace(".", "").isdigit() else target
    if not target_ip:
        print("Invalid target IP or domain.")
        return

    host_ip: ipaddress.IPv4Address = ipaddress.IPv4Address(
        socket.gethostbyname(socket.gethostname())
    )
    public_ip: ipaddress.IPv4Address = get_public_ip()
    public_ip_coordinates: tuple[float, float] = get_coordinates(API_KEY, public_ip)

    if host_ip != public_ip:
        print(f"Public IP (geolocation starting point): {public_ip} | Behind NAT")
    else:
        print(f"Public IP (geolocation starting point): {public_ip}")

    traceroute_hops: dict[ipaddress.IPv4Address, list[int]] = traceroute(target)
    public_hop_coords: OrderedDict[ipaddress.IPv4Address, tuple[float, float]] = (
        OrderedDict({public_ip: public_ip_coordinates})
    )

    total_distance: int = 0
    prev_latency: float = 0.0
    prev_hop: ipaddress.IPv4Address = host_ip
    prev_coords = public_ip_coordinates
    for i, hop in enumerate(traceroute_hops, start=1):
        avg_latency = avg(traceroute_hops[hop])

        if hop.is_private:
            print(
                f"{i:<2}: {str(prev_hop):<16} - {round(avg_latency, 1):<5}ms -> {str(hop):<16} (Δkm: {'N/A':^7}km | Δms: {round(avg_latency - prev_latency, 1):>5}ms) - can't geolocate private IPs."
            )

        if hop.is_global:
            hop_coords = get_coordinates(API_KEY, hop)
            distance = calculate_distance(prev_coords, hop_coords)
            print(
                f"{i:<2}: {str(prev_hop):<16} - {round(avg_latency, 1):<5}ms -> {str(hop):<16} (Δkm: {round(distance, 1):>7}km | Δms: {round(avg_latency - prev_latency, 1):>5}ms)"
            )
            public_hop_coords.update({hop: hop_coords})
            total_distance += distance
            prev_coords = hop_coords

        prev_latency = avg_latency
        prev_hop = hop

    print(f"Total distance: {round(total_distance, 2)} km")

    plot_network(traceroute_hops)
    plot_public_ips(public_hop_coords)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [IP address or domain]")
    else:
        main(sys.argv[1])
