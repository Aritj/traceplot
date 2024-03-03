# What is this project?
This is a small project I worked on for a weekend. 

This is planned to demonstrate the viability (or lack thereof) of using traceroute and geolocation of public IPs to track the flow of data across the internet.

The IP Geolocation service used is [ipgeolocation](https://ipgeolocation.io/). 
> [!NOTE]
> The distance between two geolocated IPs is calculated as a straight line between both locations multiplied by a roughly "guess-timated" scalar value of 20%, to mimic the real-world pathways of internet data, which often deviate significantly from straight lines.

## Running Traceplot
Using FQDN:
```bash
> python3 traceplot.py dtu.dk
```
Using IP:
```bash
> python3 traceplot.py 8.8.8.8
```

## Example output 1 (dtu.dk):
### Terminal input
```bash
> python3 traceplot.py dtu.dk
```
### Terminal output
```
Public IP (geolocation starting point): [Public_IP] | Behind NAT
1 : 192.168.0.50     - 4.0  ms -> 192.168.0.1      (Δkm:   N/A  km | Δms:   4.0ms) - can't geolocate private IPs.
2 : 192.168.0.1      - 19.3 ms -> 10.116.33.1      (Δkm:   N/A  km | Δms:  15.3ms) - can't geolocate private IPs.
3 : 10.116.33.1      - 11.3 ms -> 176.22.62.134    (Δkm:   195.3km | Δms:  -8.0ms)
4 : 176.22.62.134    - 13.3 ms -> 83.88.12.12      (Δkm:     1.5km | Δms:   2.0ms)
5 : 83.88.12.12      - 13.3 ms -> 128.76.59.115    (Δkm:   182.5km | Δms:   0.0ms)
6 : 128.76.59.115    - 17.5 ms -> 51.10.14.22      (Δkm:  1139.8km | Δms:   4.2ms)
7 : 51.10.14.22      - 28.7 ms -> 52.236.166.178   (Δkm:   432.3km | Δms:  11.2ms)
Total distance: 1951.33 km
```
### Traceroute plot
![plot_9](https://github.com/Aritj/traceplotter/assets/69643316/06a56e6d-1d15-42e7-816e-9395268e32ee)
### Geolocation plot
![plot_10](https://github.com/Aritj/traceplotter/assets/69643316/b1e1047b-2965-4d09-9663-fbacf2078481)


## Example output 2 (ns0.internet.fo):
### Terminal input
```bash
> python3 traceplot.py ns0.internet.fo
```
### Terminal output
```
Public IP (geolocation starting point): [Public_IP] | Behind NAT
1 : 192.168.0.50     - 4.7  ms -> 192.168.0.1      (Δkm:   N/A  km | Δms:   4.7ms) - skipped - can't geolocate RFC1918 IPs
2 : 192.168.0.1      - 16.3 ms -> 10.116.33.1      (Δkm:   N/A  km | Δms:  11.7ms) - skipped - can't geolocate RFC1918 IPs
3 : 10.116.33.1      - 18.0 ms -> 176.22.62.134    (Δkm:   195.3km | Δms:   1.7ms)
4 : 176.22.62.134    - 18.3 ms -> 83.88.3.113      (Δkm:   159.0km | Δms:   0.3ms)
5 : 83.88.3.113      - 15.0 ms -> 176.22.253.118   (Δkm:    36.6km | Δms:  -3.3ms)
6 : 176.22.253.118   - 61.0 ms -> 193.34.104.38    (Δkm:  1574.0km | Δms:  46.0ms)
7 : 193.34.104.38    - 60.0 ms -> 81.18.224.2      (Δkm:     0.0km | Δms:  -1.0ms)
Total distance: 1964.84 km
```
### Traceroute plot
![plot_3](https://github.com/Aritj/traceplotter/assets/69643316/5d10eb00-c133-4122-8440-fc77039c4ed0)
### Geolocation plot
![plot_4](https://github.com/Aritj/traceplotter/assets/69643316/eb245d62-77e2-4cbb-bb73-9e3fc4b01d76)

## Example output 3 (microsoft.com):
### Terminal input
```bash
> python3 traceplot.py microsoft.com
```
### Terminal output
```
Public IP (geolocation starting point): [Public_IP] | Behind NAT
1 : 192.168.0.50     - 4.0  ms -> 192.168.0.1      (Δkm:   N/A  km | Δms:   4.0ms) - can't geolocate private IPs.
2 : 192.168.0.1      - 20.3 ms -> 10.116.33.1      (Δkm:   N/A  km | Δms:  16.3ms) - can't geolocate private IPs.
3 : 10.116.33.1      - 13.0 ms -> 176.22.62.134    (Δkm:   195.3km | Δms:  -7.3ms)
4 : 176.22.62.134    - 12.7 ms -> 83.88.12.15      (Δkm:     1.5km | Δms:  -0.3ms)
5 : 83.88.12.15      - 13.7 ms -> 128.76.59.115    (Δkm:   182.5km | Δms:   1.0ms)
6 : 128.76.59.115    - 16.0 ms -> 51.10.14.22      (Δkm:  1139.8km | Δms:   2.3ms)
7 : 51.10.14.22      - 110.7ms -> 20.231.239.246   (Δkm:  7124.3km | Δms:  94.7ms)
Total distance: 8643.31 km
```
### Traceroute plot
![plot_7](https://github.com/Aritj/traceplotter/assets/69643316/7d017756-fb63-46d7-ae20-0e8ac392fd76)
### Geolocation plot
![plot_8](https://github.com/Aritj/traceplotter/assets/69643316/c24ebfa2-54f3-4a3d-bb43-64a275d10a03)
