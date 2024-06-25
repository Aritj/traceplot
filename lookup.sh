#!/bin/bash

# Predefined list of DNS servers
# "9.9.9.9"         - Quad9
# "8.8.8.8"         - Google
# "1.1.1.1"         - Cloudflare
# "8.26.56.26"      - Comodo Secure DNS
# "103.86.96.100"   - NordVPN
# "216.146.35.35"   - Oracle
# "95.85.95.85"     - G-Core
# "64.6.64.6"       - Verisign
# "208.67.222.222"  - OpenDNS
# "45.90.28.190"    - Next DNS
PREDEFINED_DNS_SERVERS=("9.9.9.9" "8.8.8.8" "1.1.1.1" "8.26.56.26" "103.86.96.100" "216.146.35.35" "95.85.95.85" "64.6.64.6" "208.67.222.222" "45.90.28.190")

# Check for domain parameter
if [ -z "$1" ]; then
  echo "Usage: $0 <domain> [dns-server]"
  exit 1
fi

DOMAIN=$1
DNS_SERVER=${2:-}

# Function to perform forward lookup
lookup_a_records() {
  local server=$1
  local domain=$2
  dig -t a $domain @$server +short | grep -E "^[0-9.]+$"
}

# Function to perform reverse lookup
lookup_ptr_records() {
  local ip=$1
  dig -x $ip +short
}

# Array to store results
A_RECORDS=()
PTR_RECORDS=()

# Perform lookup against the given DNS server or predefined servers
if [ -n "$DNS_SERVER" ]; then
  A_RECORDS+=($(lookup_a_records $DNS_SERVER $DOMAIN))
else
  for SERVER in "${PREDEFINED_DNS_SERVERS[@]}"; do
    A_RECORDS+=($(lookup_a_records $SERVER $DOMAIN))
  done
fi

# Remove duplicate A-RECORDS
A_RECORDS=($(echo "${A_RECORDS[@]}" | tr ' ' '\n' | sort -u))

# Perform PTR lookups for each A-RECORD
for IP in "${A_RECORDS[@]}"; do
  PTR_RECORDS+=($(lookup_ptr_records $IP))
done

# Filter and echo the PTR results (e.g., removing duplicates)
FILTERED_PTR_RECORDS=($(echo "${PTR_RECORDS[@]}" | tr ' ' '\n' | sort -u))

# Print A-RECORDS and PTR-RECORDS in two columns
echo -e "A-RECORDS (IP addresses) for $DOMAIN:\tPTR-RECORDS (Reverse DNS) for $DOMAIN:"
for ((i = 0; i < ${#A_RECORDS[@]}; i++)); do
  printf "%-30s\t\t%s\n" "${A_RECORDS[$i]}" "${FILTERED_PTR_RECORDS[$i]}"
done
