#! /usr/bin/python

import time

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Switch
from mininet.cli import CLI

class Router(Node):
    "Node with Linux Router Function"
    
    def config(self, **params):
        super(Router, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')
    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(Router, self).terminate()

def topology():
    net = Mininet(autoStaticArp=True)

    # Initialize objects dicts
    hosts, switches, routers = {}, {}, {}

    # Create Host, from h1 to h4
    h1 = net.addHost('h1',ip='140.113.20.1/24')
    h2 = net.addHost('h2',ip='140.114.20.1/24')
    # Create Switch s1
    for i in range(2):
        switch = net.addSwitch('s%d' % (i + 1), failMode='standalone')
        switches['s%d' % (i + 1)] = switch

    # Create Router, from r1 to r6
    r1 = net.addHost('r1', cls=Router)
    r2 = net.addHost('r2', cls=Router)
    GW1 = net.addHost('GW1', cls=Router)
    GW2 = net.addHost('GW2', cls=Router)
    # link pairs
    links = [('h1', 's1'), ('h2', 's2'),
             ('GW1', 's1'), ('GW1', 'r1'),
             ('GW2', 's2'), ('GW2', 'r2'),
             ('r1', 'r2')
            ]
    #create link
    for link in links:
        src, dst = link
        net.addLink(src, dst)

    net.start()

    # Configure network manually
    config(r1, r2, GW1, GW2, h1, h2)

    CLI(net)

    net.stop()

def config(r1, r2, GW1, GW2, h1, h2):

    # Hosts, Routers IP configuration
    r1.cmd('ifconfig r1-eth0 140.113.0.2/16')
    r1.cmd('ifconfig r1-eth1 20.0.0.1/8')

    r2.cmd('ifconfig r2-eth0 140.114.0.2/16')
    r2.cmd('ifconfig r2-eth1 20.0.0.2/8')

    #GW1.cmd('ifconfig GW1-eth0 140.113.20.15/24')
    GW1.cmd('ifconfig GW1-eth1 140.113.0.1/16')

    #GW2.cmd('ifconfig GW2-eth0 140.114.20.15/24')
    GW2.cmd('ifconfig GW2-eth1 140.114.0.1/16')

    # Host routing table configuration
    h1.cmd('ip route add default dev h1-eth0')
    h2.cmd('ip route add default dev h2-eth0')

    # Router routing table configuration
    r1.cmd('route add -net 140.113.0.0/16 gw 140.113.0.1')
    r1.cmd('route add -net 140.114.0.0/16 gw 20.0.0.2')

    r2.cmd('route add -net 140.114.0.0/16 gw 140.114.0.1')
    r2.cmd('route add -net 140.113.0.0/16 gw 20.0.0.1')

    GW1.cmd('ip route add 140.114.0.0/16 via 140.113.0.2')
    GW2.cmd('ip route add 140.113.0.0/16 via 140.114.0.2')

    GW1.cmd('ip link add GRE type gretap remote 140.114.0.1 local 140.113.0.1')
    GW1.cmd('ip link set GRE up')
    GW1.cmd('ip link add br0 type bridge')
    GW1.cmd('brctl addif br0 GW1-eth0')
    GW1.cmd('brctl addif br0 GRE')
    GW1.cmd('ip link set br0 up')

    GW2.cmd('ip link add GRE type gretap remote 140.113.0.1 local 140.114.0.1')
    GW2.cmd('ip link set GRE up')
    GW2.cmd('ip link add br0 type bridge')
    GW2.cmd('brctl addif br0 GW2-eth0')
    GW2.cmd('brctl addif br0 GRE')
    GW2.cmd('ip link set br0 up')
    



if __name__ == '__main__':
    topology()


