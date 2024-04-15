import pandas as pd
from pprint import pprint
import socket
import warnings
import datetime


def get_ip_by_hostname(domainlist: list, hostnamelist: list) -> pd.DataFrame:
    """
    Input: Corporate domain list (domainlist) and a hostname list (hostnamelist).
    Output: Pandas Dataframe with all fqdns resolved (hostnames+domain).
    """

    # Create a new list that will store many other lists inside it. Each new list inside 'all_fqdns'
    # refer to a specific host. Inside each list will have all possible combinations of the refereed hostname with
    # all possible domains.
    global resolv_ip, data_temp
    all_fqdns = []

    # For every hostname on the list hostnamelist, concatenate it with all possible domains and put this set of
    # possibilities in the all_fqdns list.
    for h in hostnamelist:

        # Create a list that will conain all fqdns of this hostname.
        host_fqdns = []

        # For each domain in the domainlist
        for d in domainlist:
            # Change the hostname (h) to lowercase and concatenate it with the domain (d).
            fqdn = h.lower() + '.' + d
            # Add fqdn (hostname+domain) to this host fqdns.
            host_fqdns.append(fqdn)

        all_fqdns.append(host_fqdns)

    # Resolve all fqdns of 'all_fqdns' list and add them to the list 'data'.
    data = []

    for all_host_fqdns in all_fqdns:
        data_temp = []

        host = all_host_fqdns[0].split('.')[0]
        data_temp.append(host)
        # For each fqnd of this host, try to resolve the ip address.
        for host_fqdn in all_host_fqdns:
            try:
                resolv_ip = socket.gethostbyname(host_fqdn)
            # If the resolution retuns an error, consider the result as 'None'.
            except socket.gaierror:
                resolv_ip = None
            finally:
                print(f'{host_fqdn} = {resolv_ip}')
                data_temp.append(resolv_ip)

        # Add the list with the resolved ips to the 'data' list.
    data.append(data_temp)

    # Create a list that will work as the dataframe header. The first column should be 'Hostname' to match
    # resolved fqdns with their domains.
    columns = []
    for d in domainlist:
        if d in domainlist[0]:
            columns.append('Hostname')
            columns.append(d)
        else:
            columns.append(d)

    # Create a Pandas Dataframe that will have one column for each domain and hostnames with their resolved ips by line.
    final_df = pd.DataFrame(data, columns=columns)
    final_df.set_index('Hostname', inplace=True)

    return final_df


# This function will return the IP address, domain and FQDN based on the provided hostname.
def ip_fqdn_by_hostname(domainlist, hostname):

    hostname = hostname.lower()
    found = 0
    d_result = {hostname: []}
    for d in domainlist:
        if hostname == "#n/d":
            continue
        final = hostname + '.' + d
        try:
            pprint(f'Checking: {final}')
            ip = socket.gethostbyname(final)
            domain = d
        except:
            continue
        else:
            found = 1
            d_result[hostname].append([ip, hostname + '.' + domain])
    if found == 0:
        d_result[hostname].append([0, 0])
    return d_result


warnings.filterwarnings('ignore')

# Import the Excel file with hostnames
FILENAME = 'myhosts.xlsx'
hostnames = pd.read_excel(FILENAME)

# All domains list
domains = ['autdomain1.biz', 'autdomain2.biz', 'branch1.aut.mydomain.biz', 'domainaut.biz', 'mydomain.biz',
           'mydomain-net.biz', 'mysubdomain.com.br', 'mydomain.com.br', 'businessunit.mydomain.com.br',
           'branch1-bu.mydomain.com.br', 'subdomain1.mydomain.com.br', 'domain3.biz', 'branch-03.mydomain.com.br',
           'mydomain.com', 'mydomain.com.co', 'mydomain.com.py', 'subdomain-domain.biz']

now = datetime.datetime.now()
now = now.strftime("%d-%m-%Y-%H-%M-%S")

hosts = []
# Get the first column of pandas dataframe. Change column name if needed.
for h in hostnames['FIRST_COLUMN']:
    hosts.append(h)

df = get_ip_by_hostname(domains, hosts)

# Create json
df.to_json(f"ips-{now}.json", index=True)
df.to_excel(f"ips-{now}.xlsx", index=True)
