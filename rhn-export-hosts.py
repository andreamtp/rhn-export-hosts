#!/usr/bin/python
# ~-~ encoding: utf-8 ~-~
#
# This file is rhn-export-hosts .
# Copyright (C) 2013-2018 Andrea Perotti <aperotti@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import xmlrpclib
import string

# Url of your Sat5/Spacewalk
# RHN has been decommissioned by Red Hat long long time ago
URL = "https://localhost/rpc/api"
user = ""
pswd = ""

client = xmlrpclib.Server(URL, verbose=0)
session = client.auth.login(user, pswd)
# ALL Hosts
listHosts = client.system.listUserSystems(session)

# Just Virtual Hosts running on a recognized hypervisor
# listHosts = client.system.listVirtualHosts(session)

# Just Physical Hosts
#listHosts = client.system.listPhysicalSystems(session)

# We'll use it to store systems info
hosts = []

for host in listHosts:
        system_id = host.get("id")
        name = host.get("name")
        last_checkin = host.get("last_checkin")
        hosts.append([system_id,name,last_checkin])

# close connection to avoid timeout: hosts id are already collected
client.auth.logout(session)

# add few more details to those bare ids
for host in hosts:
	client = xmlrpclib.Server(URL, verbose=0)
	session = client.auth.login(user, pswd)

	# network info
	network = client.system.getNetwork(session, int(host[0]))
	hostname = network.get("hostname")
	ip = network.get("ip")

	host.insert(2, hostname)
	host.insert(3, ip.strip())	
	
	# CPU info
	cpu = client.system.getCpu(session, int(host[0]))
	count_cpu = cpu.get("count")
	count_socket = cpu.get("socket_count")

	host.insert(4, count_cpu)
	host.insert(5, count_socket)


	# detailed info
	details = client.system.getDetails(session, int(host[0]))
	base_entitlement = details.get("base_entitlement")
	description_raw = details.get("description")	

	description_slim = description_raw.splitlines()[2:]

	description = dict(line.split(':') for line in description_slim)
	for key in description:
		description[key] = description[key].strip()

	#print description_raw
	#print description_slim
	#print description
	#print len(description)

	host.insert(6, description['CPU Arch'])
	host.insert(7, description['Release'])
	host.insert(8, base_entitlement)
	# not always present
        if "virtualization" in description[key]:
            host.insert(9, description['virtualization'])
	
	# entitlement info already provided by getDetails
	#entitlement_label = client.system.getEntitlements(session, int(host[0]))
	#print entitlement_label
	#host.insert(7, entitlement_label[0])
	
	line = str(host)
	print line

	#with open('lista_host_pro.txt', 'a') as f:
        #        write_line = f.write(line + "\n")
	#f.close()

	client.auth.logout(session)

#print range(len(listHosts))
#print hosts
print len(hosts)
