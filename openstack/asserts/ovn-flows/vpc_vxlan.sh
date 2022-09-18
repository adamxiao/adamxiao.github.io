#!/bin/bash

########################################################################################
# 基于vxlan实现多租户网络隔离，最多支持4094个租户
# 1. 支持租户内部之间二层网络隔离；
# 2. 支持租户内部之间三层转发；
# 3. 支持租户访问外网；
# 4. 支持外部网络访问租户的内部网络
#
# 1. Create a virtual bridge on the host
# bash vpc_vxlan.sh 0
#
# 2. Create a vxlan tunnel between each host
# bash vpc_vxlan.sh 1 1 192.168.12.10 192.168.12.8
# bash vpc_vxlan.sh 1 1 192.168.12.10 192.168.12.9
#
# 3. Initialize basic flow rules on vxlan virtual bridge, including flow direction between vxlan tunnels
# bash vpc_vxlan.sh 2
#
# 4. Build the mapping relationship between vlan id and vni on the vxlan virtual bridge
# bash vpc_vxlan.sh 3 0x1b 6
#
# 5. add dhcp server
# bash vpc_vxlan.sh 4 abc1 6 192.168.12.2/24 192.168.12.1 192.168.12.3,192.168.12.254
#
# 6. Add route to subnet for forwarding
# bash vpc_vxlan.sh 5 tg12t 6 192.168.12.1/24
#
# 7. Create an external network
# bash vpc_vxlan.sh 6 qrouter-46f6429974c1 qg-511dd24a-a9 10.90.3.201/24 eth3 10.90.3.1
#
# 8. Set floating ip, support nat forwarding
# bash vpc_vxlan.sh 7 qrouter-46f6429974c1 qg-511dd24a-a9 10.90.3.213 182.152.10.8 24
#
########################################################################################

internal_bridge='br-int'
vxlan_bridge='br-tun'
external_bridge='br-ex'

vxlan_int_port='patch-int'
internal_tun_port='patch-tun'

prefix_key='vxlan_'

function print_usage()
{
    echo "create bridge, bash vpc_vxlan.sh 0"
    echo "create vxlan tunnel bash vpc_vxlan.sh 1 vxlan_name local_ip remote_ip"
    echo "Initialize flow table from tunnel, bash vpc_vxlan.sh 2"
    echo "Add subnet flow table rules, bash vpc_vxlan.sh 3 vni vlan_id"
    echo "Create DHCP server, bash vpc_vxlan.sh 4 dhcp_name tap_id dhcp_ip dhcp_gw dhcp_range"
    echo "Add route server, bash vpc_vxlan.sh 5 router_name tap_id gw_address"
    echo "Create an external network, bash vpc_vxlan.sh 6 router_name port_name port_ip physical_network_card physical_gate_way"
    echo "Set floating ip, support nat forwarding, bash vpc_vxlan.sh 7 router_name port_name float_ip vm_port_ip vm_port_ip_prex"
    echo "example:"
    echo "  bash vpc_vxlan.sh 1 vxlan0 192.168.12.8 192.168.12.9"
    echo "  bash vpc_vxlan.sh 2"
    echo "  bash vpc_vxlan.sh 3 0x1b 6"
    echo "  bash vpc_vxlan.sh 4 abc1 6 192.168.12.2/24 192.168.12.1 192.168.12.3,192.168.12.254"
    echo "  bash vpc_vxlan.sh 5 tg12t 6 192.168.12.1/24"
    echo "  bash vpc_vxlan.sh 6 qrouter-46f6429974c1 qg-511dd24a-a9 10.90.3.201/24 eth3 10.90.3.1"
    echo "  bash vpc_vxlan.sh 7 qrouter-46f6429974c1 qg-511dd24a-a9 10.90.3.213 182.152.10.8 24"
}

function set_flows_from_internal_vswitch()
{
    local vsport
    local result=""

    result=$(/usr/lib/ksvd/bin/ovs-ofctl show ${vxlan_bridge} | grep -w ${vxlan_int_port})
    if [ x"${result}" = x ]; then
        echo "failed to find vswitch port info by ${tapname}"
        exit 1
    fi

    vsport=$(echo ${result} | cut -d '(' -f 1 | sed 's/^ *//g')
    if [ x"${vsport}" = x ]; then
        echo "failed to get vsport by ${tapname}"
        exit 2
    fi

    echo "${vxlan_int_port}: ${vsport}"
    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=0,priority=1,in_port=${vsport} actions=resubmit(,2)"
	
    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=10,priority=1 actions=learn(table=20,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:OXM_OF_IN_PORT[]),output:${vsport}"

    return 0
}

function set_flows_from_vxlan_vswitch()
{
    local vsport
    local result=""

    result=$(/usr/lib/ksvd/bin/ovs-ofctl show ${vxlan_bridge} | grep ${prefix_key} | awk -F " " '{print $1}')
    if [ x"${result}" = x ]; then
        echo "failed to find vswitch port info by ${vxlan_bridge}"
        exit 1
    fi

    for tapport in ${result}; do
        vsport=$(echo ${tapport} | cut -d '(' -f 1 | sed 's/^ *//g')
        if [ x"${vsport}" = x ]; then
            echo "failed to get vsport by ${tapport}"
            exit 2
        fi

        # Process the data from the vxlan peer switch
        echo "vxlan_port: ${vsport}"
        /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=0,priority=1,in_port=${vsport} actions=resubmit(,4)"
    done

    return 0
}

function bridge_flows_init()
{
    # Process the data from the br-int switch
    set_flows_from_internal_vswitch
	
    # Process the data from the vxlan peer switch
    set_flows_from_vxlan_vswitch

    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=0,priority=0 actions=drop"

    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=2,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,20)"
    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=2,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,22)"

    # Each subnet corresponds to a different tag id and vni
    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=4,priority=0 actions=drop"

    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=20,priority=0 actions=resubmit(,22)"

    /usr/lib/ksvd/bin/ovs-ofctl add-flow ${vxlan_bridge} "table=22,priority=0 actions=drop"
}

function create_bridge()
{
    local isexist=""

    isexist=$(ovs-vsctl list-br | grep -w ${internal_bridge})
    if [ x"${isexist}" = x ]; then
        ovs-vsctl add-br ${internal_bridge}
    fi

    isexist=$(ovs-vsctl list-br | grep -w ${vxlan_bridge})
    if [ x"${isexist}" = x ]; then
        ovs-vsctl add-br ${vxlan_bridge}
    fi

    isexist=$(/usr/lib/ksvd/bin/ovs-ofctl show ${internal_bridge} | grep -w ${internal_tun_port})
    if [ x"${isexist}" = x ]; then
        ovs-vsctl add-port ${internal_bridge} ${internal_tun_port} -- set interface ${internal_tun_port} type=patch options:peer=${vxlan_int_port} -- add-port ${vxlan_bridge} ${vxlan_int_port} -- set interface ${vxlan_int_port} type=patch options:peer=${internal_tun_port}
    fi
}

function set_br_tun_flows()
{
    local outport=""
    local result=""

    result=$(/usr/lib/ksvd/bin/ovs-ofctl show ${vxlan_bridge} | grep ${prefix_key} | awk -F " " '{print $1}')
    if [ x"${result}" = x ]; then
        echo "failed to find vswitch port info by ${vxlan_bridge}"
        exit 1
    fi

    for tapport in ${result}; do
        vsport=$(echo ${tapport} | cut -d '(' -f 1 | sed 's/^ *//g')
        if [ x"${vsport}" = x ]; then
            echo "failed to get vsport by ${tapport}"
            exit 2
        fi

        outport=${outport}",output:${vsport}"
    done

    echo "outport: ${outport}"

    # Each subnet corresponds to a different tag id and vni
    /usr/lib/ksvd/bin/ovs-ofctl add-flow br-tun "table=4,priority=1,tun_id=${vni} actions=mod_vlan_vid:${vlan_id},resubmit(,10)"

    # Set the outbound direction of data from the br-int switch
    /usr/lib/ksvd/bin/ovs-ofctl add-flow br-tun "table=22,priority=1,dl_vlan=${vlan_id} actions=strip_vlan,load:${vni}->NXM_NX_TUN_ID[] ${outport}"
}

function create_vxlan()
{
    ovs-vsctl add-port ${vxlan_bridge} ${prefix_key}${tunnel_name} -- set interface ${prefix_key}${tunnel_name} type=vxlan option:local_ip=${local_ip} options:remote_ip=${remote_ip} option:in_key=flow option:out_key=flow option:df_default="true"
}

function create_external_network()
{
    local ovs_port="qg-${external_port}"
    local result=""

    result=$(ovs-vsctl list-br | grep -w ${external_bridge})
    if [ x"${result}" = x ]; then
        ovs-vsctl add-br ${external_bridge}
        ovs-vsctl add-port ${external_bridge} ${physical_network_card}
    fi

    ovs-vsctl add-port ${external_bridge} ${ovs_port} -- set interface ${ovs_port} type=internal
	
    ip link set ${ovs_port} netns ${router}
	
    ip netns exec ${router} ip addr add ${ip_prex} dev ${ovs_port}
    ip netns exec ${router} ip link set ${ovs_port} up

    # Important: Add a default physical gateway to the external network
    ip netns exec ${router} ip route add default via ${physical_gate_way} dev ${ovs_port}
}

function add_nat_forwarding()
{
    ip netns exec ${router} ip addr add ${float_ip}/32 dev ${external_port}

    ip netns exec ${router} iptables -t nat -A OUTPUT -d ${float_ip}/32  -j DNAT --to-destination ${vm_port_ip}
    ip netns exec ${router} iptables -t nat -A PREROUTING -d ${float_ip}/32 -j DNAT --to-destination ${vm_port_ip}

    # For SNAT functionality, all subnets are mapped to the same floating ip
    ip netns exec ${router} iptables -t nat -A POSTROUTING -s ${vm_port_ip}/${prex_mask} -j SNAT --to-source ${float_ip}

    # Important: Add a subnet route, going out from the specified port
    ip netns exec ${router} ip route add ${float_ip}/${prex_mask} via 0.0.0.0 dev ${external_port}
}

function create_server_dhcp()
{
    local conf_path="/var/lib/dnsmasq/qdhcp-${vlan_id}-${name}"
    local dhcp_netns_name="qdhcp-${vlan_id}-${name}"
    local ovs_port="dhcp-${vlan_id}-${name}"
    local lsexist=""
	
    lsexist=$(ip netns | grep -w ${dhcp_netns_name})
    if [ x"${lsexist}" != x ]; then
        echo "${dhcp_netns_name} had exist"
        exit 0
    fi

    ip netns add ${dhcp_netns_name}

    # The length of the ovs port name cannot exceed 15 bytes, otherwise the creation fails
    ovs-vsctl add-port ${internal_bridge} ${ovs_port} -- set interface ${ovs_port} type=internal
    ovs-vsctl set port ${ovs_port} tag=${vlan_id}

    ip link set ${ovs_port} netns ${dhcp_netns_name}

    # Set ip address for virtual network card
    ip netns exec ${dhcp_netns_name} ip addr add ${ip_prex} dev ${ovs_port}
    ip netns exec ${dhcp_netns_name} ip link set ${ovs_port} up
    ip netns exec ${dhcp_netns_name} ip link set lo up

    # Set route for dhcp server	
    ip netns exec ${dhcp_netns_name} ip route add default via ${gw_ip} dev ${ovs_port}
    #ip netns exec ${dhcp_netns_name} ip route add ${remote_ip} via 0.0.0.0 dev ${ovs_port}

    # Create dhcp server on the net name space
    mkdir -p ${conf_path}

    echo "no-hosts" >${conf_path}/default.conf
    echo "no-resolv" >>${conf_path}/default.conf
    echo "strict-order" >>${conf_path}/default.conf
    echo "except-interface=lo" >>${conf_path}/default.conf
    echo "bind-dynamic" >>${conf_path}/default.conf
    echo "interface=${ovs_port}" >>${conf_path}/default.conf
    echo "dhcp-no-override" >>${conf_path}/default.conf
    echo "dhcp-authoritative" >>${conf_path}/default.conf
    echo "dhcp-lease-max=253" >>${conf_path}/default.conf
    echo "dhcp-range=${dhcp_range}" >>${conf_path}/default.conf
    echo "pid-file=${conf_path}/pid" >>${conf_path}/default.conf
    echo "dhcp-hostsfile=${conf_path}/hostsfile" >>${conf_path}/default.conf
    echo "addn-hosts=${conf_path}/addnhosts" >>${conf_path}/default.conf
    echo "dhcp-leasefile=${conf_path}/leases" >>${conf_path}/default.conf

    # configure dns server
    echo "server=114.114.114.114" >>${conf_path}/default.conf
	
    ip netns exec ${dhcp_netns_name} /usr/sbin/dnsmasq --conf-file=${conf_path}/default.conf --leasefile-ro
}

function create_server_router()
{
    ip netns add qrouter-${name}
    ip netns exec qrouter-${name} ip link set lo up
}

function server_add_router()
{
    local ovs_port="qr-${vlan_id}-${name}"
    local lsexist=""

    lsexist=$(ip netns | grep -w qrouter-${name})
    if [ x"${lsexist}" = x ]; then
        create_server_router
    fi

    ovs-vsctl add-port ${internal_bridge} ${ovs_port} -- set interface ${ovs_port} type=internal
    ovs-vsctl set port ${ovs_port} tag=${vlan_id}
	
    ip link set ${ovs_port} netns qrouter-${name}
    
    ip netns exec qrouter-${name} ip addr add ${ip_prex} dev ${ovs_port}
    ip netns exec qrouter-${name} ip link set ${ovs_port} up

    # Important: Add a subnet route, going out from the specified port
    #ip netns exec qrouter-${name} ip route add ${ip_prex} via 0.0.0.0 dev ${ovs_port}
}

if [ $# -lt 1 ]; then
    print_usage
    exit 1
fi

action=$1

if [ $action -eq 0 ]; then
    create_bridge
elif [ $action -eq 1 ]; then
    if [ $# -ne 4 ]; then
        print_usage
        exit 1
    fi

    tunnel_name=$2
    local_ip=$3
    remote_ip=$4

    create_vxlan
elif [ $action -eq 2 ]; then
    bridge_flows_init
elif [ $action -eq 3 ]; then
    if [ $# -ne 3 ]; then
        print_usage
        exit 1
    fi

    vni=$2
    vlan_id=$3

    set_br_tun_flows
elif [ $action -eq 4 ]; then
    if [ $# -ne 6 ]; then
        print_usage
        exit 1
    fi

    name=$2
    vlan_id=$3
    ip_prex=$4
    gw_ip=$5
    dhcp_range=$6

    create_server_dhcp
elif [ $action -eq 5 ]; then
    if [ $# -ne 4 ]; then
        print_usage
        exit 1
    fi

    name=$2
    vlan_id=$3
    ip_prex=$4

    server_add_router
elif [ $action -eq 6 ]; then
    if [ $# -ne 6 ]; then
        print_usage
        exit 1
    fi

    router=$2
    external_port=$3
    ip_prex=$4
    physical_network_card=$5
    physical_gate_way=$6

    create_external_network
elif [ $action -eq 7 ]; then
    if [ $# -ne 6 ]; then
        print_usage
        exit 1
    fi

    router=$2
    external_port=$3
    float_ip=$4
    vm_port_ip=$5
    prex_mask=$6

    add_nat_forwarding
else
    print_usage
    exit 1
fi
