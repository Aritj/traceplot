# Import 
import sys

import src.tools as tools
import src.models as models
import src.plots as plots

def main(target:str ) -> None:
    """Main function to perform traceroute and visualize the results.

    Args:
        target (str): IP address or domain to traceroute to.
    """
    target_ip = tools.resolve_to_ip(target)

    if not target_ip:
        print("Invalid target IP or domain.")
        return
        
    target_ip_info = tools.query_geolocation_info(target_ip)

    trace: models.Traceroute = tools.trace(str(target_ip))

    if trace.is_empty():
        print("An issue arose during the traceroute.")
        return
    
    plots.plot_network(trace)
    
    # If the target IP doesn't reply to trace route, append it to the end
    if not trace.contains_ip(target_ip):
        trace.add_hop(
            models.Hop(
                fqdn=target_ip_info.fqdn,
                ip_addr=target_ip,
                latencies=trace.hops[-1].latencies,
                geo_info=target_ip_info,
            )
        )
    
    public_hops = tools.convert_to_public_hops(trace)
    tools.print_info(public_hops)
    plots.plot_public_ips(public_hops)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [IP address or domain]")
    else:
        main(sys.argv[1])