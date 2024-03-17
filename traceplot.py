import sys
import subprocess

import src.tools as tools
import src.models as models
import src.plots as plots


def execute_traceroute(ip: str) -> models.Traceroute:
    """Perform a traceroute to the specified IP address and return the results.

    Args:
        ip (str): The IP address to traceroute to.

    Returns:
        dict: A dictionary mapping from IP addresses to latency lists.
    """
    os_name: str = tools.get_os_name().lower()
    os_traceroute_dict = {
        "windows": {
            "handler": tools.parse_windows_traceroute,
            "arguments": ["tracert", "-w", "1", ip],
            # TODO: implement with DNS names
        },
        "darwin": {
            "handler": tools.darwin_traceroute,
            "arguments": ["traceroute", "-I", "-w1", ip],
        },
        # TODO: Implement 'Java' and 'Linux'
    }

    if os_name not in os_traceroute_dict.keys():
        print(f"{os_name.capitalize()} trace route parsing not implemented.")
        sys.exit()

    try:
        traceroute_output = subprocess.run(
            os_traceroute_dict[os_name]["arguments"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )

        return os_traceroute_dict[os_name]["handler"](traceroute_output.stdout)
    except subprocess.TimeoutExpired:
        print("Traceroute command timed out")
        sys.exit()


def main(target: str) -> None:
    """Main function to perform traceroute and visualize the results.

    Args:
        target (str): IP address or domain to traceroute to.
    """
    target_ip = (
        tools.get_ip_from_fqdn(target)
        if not target.replace(".", "").isdigit()
        else target
    )

    if not target_ip:
        print("Invalid target IP or domain.")
        return

    public_ip_info = tools.query_geolocation_info()
    target_ip_info = tools.query_geolocation_info(target_ip)

    trace = execute_traceroute(target)

    if trace.is_empty():
        print("An issue arose during the traceroute.")
        sys.exit()

    trace.print_info()

    # If the target IP doesn't reply to trace route, append it to the end
    if not trace.contains_ip(target_ip):
        trace.add_hop(
            models.Hop(
                fqdn=target_ip_info.fqdn,
                ip_addr=target_ip,
                latencies=None,
                geo_info=target_ip_info,
            )
        )

    plots.plot_network(trace)

    # Remove RFC1918 IPs
    private_hops = [hop for hop in trace.hops if hop.ip_addr.is_private]
    [trace.hops.remove(hop) for hop in private_hops]

    # Include public IP as the "first hop" in the plot
    trace.insert_hop(
        0,
        models.Hop(
            fqdn=public_ip_info.fqdn,
            ip_addr=public_ip_info.ip_addr,
            latencies=private_hops[0].latencies,
            geo_info=public_ip_info,
        ),
    )

    plots.plot_public_ips(trace)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [IP address or domain]")
    else:
        main(sys.argv[1])
