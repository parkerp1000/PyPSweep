import ipaddress
import platform
import subprocess
import concurrent.futures
import socket

def init_ip_range():
    init_ip_start = input('Starting IP: ')
    init_ip_end = input('Ending IP: ')
    
    try:
        ip_list = ip_range(init_ip_start, init_ip_end)
        print("IP Range:", ip_list)
        return ip_list
    except ValueError as e:
        print(f"Error: {e}")
        return []

def ip_range(start_ip, end_ip):
    # Convert IP addresses to integer
    start_ip_int = int(ipaddress.IPv4Address(start_ip))
    end_ip_int = int(ipaddress.IPv4Address(end_ip))
    
    # Ensure start_ip is less than or equal to end_ip
    if start_ip_int > end_ip_int:
        raise ValueError("Starting IP should be less than or equal to Ending IP")
    
    # Generate the range of IPs
    ip_list = [str(ipaddress.IPv4Address(ip)) for ip in range(start_ip_int, end_ip_int + 1)]
    
    return ip_list

def ping_ip(ip):
    # Determine the ping command based on the OS
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        reachable = True
    except subprocess.CalledProcessError:
        reachable = False
    
    # Attempt to resolve hostname
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        hostname = "Not available"
    
    return ip, reachable, hostname

def ping_all_ips(ip_list):
    results = []
    
    # Define a function to ping an IP, resolve hostname and store the result
    def ping_and_store(ip):
        result = ping_ip(ip)
        results.append(result)
    
    # Use ThreadPoolExecutor to ping IPs concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        executor.map(ping_and_store, ip_list)
    
    return results

# Example usage
ip_list = init_ip_range()
if ip_list:
    results = ping_all_ips(ip_list)

    # Sort results by IP address
    sorted_results = sorted(results, key=lambda x: int(ipaddress.IPv4Address(x[0])))
    
    print(f"{'IP':<15}{'Reachable':<15}{'Hostname':<30}")
    print("=" * 60)
    for ip, reachable, hostname in sorted_results:
        print(f"{ip:<15} {str(reachable):<15} {hostname:<30}")
