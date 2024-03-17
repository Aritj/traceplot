import src.models as models
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import networkx as nx  # Import NetworkX for plotting network graphs


def plot_network(trace: models.Traceroute) -> None:
    """Plot a network graph of traceroute hops.

    Args:
        hop_coords (Dict[ipaddress.IPv4Address, Tuple[float, float]]): Dictionary mapping IP addresses to geographic coordinates.
    """
    # Create a new directed graph
    G = nx.DiGraph()
    hops = [f"{hop.fqdn} ({hop.ip_addr})" for hop in trace.hops]

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
        node_color=["green" if hop.ip_addr.is_global else "red" for hop in trace.hops],
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


def plot_public_ips(trace: models.Traceroute) -> None:
    """Plot public IP addresses on a world map.

    Args:
        hop_coords (Dict[ipaddress.IPv4Address, Tuple[float, float]]): Dictionary mapping IP addresses to geographic coordinates.
    """
    projection = ccrs.PlateCarree()
    plt.figure(figsize=(15, 10))
    ax: ccrs.mpl.geoaxes.GeoAxes = plt.axes(projection=projection)
    ax.coastlines()
    # Determine the map's extent
    lats, lons = zip(*[hop.get_coords() for hop in trace.hops])
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
    for i, hop in enumerate(trace.hops):
        ax.plot(
            float(hop.geo_info.longitude),
            float(hop.geo_info.latitude),
            "o",
            color=cmap(i / len(trace.hops)),
            markersize=10,
            transform=ccrs.Geodetic(),
            label=f"Hop {i + 1}",
        )

    # Connect hops with lines
    prev_hop = None
    for hop in trace.hops:
        if prev_hop:
            prev_lat, prev_lon = prev_hop
            ax.plot(
                [prev_lon, hop.geo_info.longitude],
                [prev_lat, hop.geo_info.latitude],
                "-",
                color="black",
                transform=ccrs.Geodetic(),
            )
        prev_hop = hop.get_coords()

    ax.legend(
        [
            f"{i+1}: {hop.fqdn} ({hop.ip_addr}) ({hop.geo_info.country_code} - {hop.geo_info.isp_name})"
            for i, hop in enumerate(trace.hops)
        ]
    )
    plt.title("Traceroute Hops (source: ipwho.is)")
    plt.show()
