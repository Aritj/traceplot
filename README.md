# What is this project?
This is a small project I worked on for a weekend. This is planned to demonstrate the viability (or lack thereof) of using traceroute and geolocation of public IPs to track the flow of data across the internet.

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
Public IP (starting point): [WAN_IP]
1 : 192.168.0.1 skipped - can't geolocate RFC1918 IPs
2 : 10.116.33.1 skipped - can't geolocate RFC1918 IPs
3 : [WAN_IP]         - 14.3 ms -> 176.22.62.134    (Δkm:   195.3km | Δms:  14.3ms)
4 : 176.22.62.134    - 19.3 ms -> 83.88.12.12      (Δkm:     1.5km | Δms:   5.0ms)
5 : 83.88.12.12      - 12.7 ms -> 128.76.59.115    (Δkm:   182.5km | Δms:  -6.7ms)
6 : 128.76.59.115    - 22.3 ms -> 51.10.14.22      (Δkm:  1139.8km | Δms:   9.7ms)
7 : 51.10.14.22      - 33.3 ms -> 52.236.166.178   (Δkm:   432.3km | Δms:  11.0ms)
Total distance: 1951.33 km
```
### Traceroute plot
![plot_1](https://github.com/Aritj/traceplotter/assets/69643316/99a151cc-ae73-4dec-8590-173998dc0e38)
### Geolocation plot
![plot_2](https://github.com/Aritj/traceplotter/assets/69643316/6490498c-38d1-456f-afc2-0806e6365d14)

## Example output 2 (ns0.internet.fo):
### Terminal input
```bash
> python3 traceplot.py ns0.internet.fo
```
### Terminal output
```
Public IP (starting point): [WAN_IP]
1 : 192.168.0.1 skipped - can't geolocate RFC1918 IPs
2 : 10.116.33.1 skipped - can't geolocate RFC1918 IPs
3 : [WAN_IP]         - 18.0 ms -> 176.22.62.134    (Δkm:   195.3km | Δms:  18.0ms)
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
Public IP (starting point): [WAN_IP]
1 : 192.168.0.1 skipped - can't geolocate RFC1918 IPs
2 : 10.116.33.1 skipped - can't geolocate RFC1918 IPs
3 : [WAN_IP]         - 14.0 ms -> 176.22.62.132    (Δkm:   195.3km | Δms:  14.0ms)
4 : 176.22.62.132    - 14.7 ms -> 83.88.12.12      (Δkm:     1.5km | Δms:   0.7ms)
5 : 83.88.12.12      - 16.5 ms -> 128.76.59.115    (Δkm:   182.5km | Δms:   1.8ms)
6 : 128.76.59.115    - 20.3 ms -> 51.10.14.18      (Δkm:  1139.8km | Δms:   3.8ms)
7 : 51.10.14.18      - 269.5ms -> 104.44.33.99     (Δkm:  9219.1km | Δms: 249.2ms)
8 : 104.44.33.99     - 266.5ms -> 104.44.30.117    (Δkm:  9739.1km | Δms:  -3.0ms)
9 : 104.44.30.117    - 268.0ms -> 104.44.29.184    (Δkm: 10764.1km | Δms:   1.5ms)
10: 104.44.29.184    - 266.0ms -> 104.44.28.143    (Δkm:     0.0km | Δms:  -2.0ms)
11: 104.44.28.143    - 266.0ms -> 104.44.30.48     (Δkm:     0.0km | Δms:   0.0ms)
12: 104.44.30.48     - 267.5ms -> 104.44.30.123    (Δkm:     0.0km | Δms:   1.5ms)
13: 104.44.30.123    - 279.0ms -> 104.44.29.58     (Δkm: 12030.5km | Δms:  11.5ms)
14: 104.44.29.58     - 268.5ms -> 104.44.28.173    (Δkm:  8126.1km | Δms: -10.5ms)
15: 104.44.28.173    - 267.0ms -> 104.44.17.64     (Δkm:     0.0km | Δms:  -1.5ms)
16: 104.44.17.64     - 267.0ms -> 104.44.7.18      (Δkm: 16394.6km | Δms:   0.0ms)
17: 104.44.7.18      - 282.0ms -> 104.44.19.141    (Δkm: 21751.5km | Δms:  15.0ms)
18: 104.44.19.141    - 266.0ms -> 104.44.19.148    (Δkm:     0.0km | Δms: -16.0ms)
19: 104.44.19.148    - 267.0ms -> 104.44.7.143     (Δkm:  3951.3km | Δms:   1.0ms)
20: 104.44.7.143     - 271.5ms -> 104.44.11.114    (Δkm:     0.0km | Δms:   4.5ms)
21: 104.44.11.114    - 269.0ms -> 20.70.246.20     (Δkm:     5.8km | Δms:  -2.5ms)
Total distance: 93501.01 km
```
### Traceroute plot
![plot_5](https://github.com/Aritj/traceplotter/assets/69643316/5bf46d36-a574-4dc6-a482-fc66d1a49871)
### Geolocation plot
![plot_6](https://github.com/Aritj/traceplotter/assets/69643316/966dfd17-e738-47f2-82bf-1388165ef985)
