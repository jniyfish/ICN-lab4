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
    net = Mininet(autoStaticArp=False)

    # Initialize objects dicts
    hosts, switches, routers = {}, {}, {}

    # Create Host, from h1 to h4
    h1 = net.addHost('h1',ip='10.0.0.1/8')
    h2 = net.addHost('h2',ip='10.0.0.2/8')
    h3 = net.addHost('h3',ip='10.0.1.1/8')
    h4 = net.addHost('h4',ip='10.0.1.2/8')
    # Create Switch s1
    for i in range(2):
        switch = net.addSwitch('s%d' % (i + 1), failMode='standalone')
        switches['s%d' % (i + 1)] = switch

    # Create Router, from r1 to r6
    r1 = net.addHost('r1', cls=Router)
    r2 = net.addHost('r2', cls=Router)
    gre1 = net.addHost('gre1', cls=Router)
    gre2 = net.addHost('gre2', cls=Router)
    # link pairs
    links = [('h1', 's1'), ('h2', 's1'),
             ('h3', 's2'), ('h4', 's2'),
             ('gre1', 's1'), ('gre1', 'r1'),
             ('gre2', 's2'), ('gre2', 'r2'),
             ('r1', 'r2')
            ]
    #create link
    for link in links:
        src, dst = link
        net.addLink(src, dst)

    net.start()

    # Configure network manually
    config(r1, r2, gre1, gre2, h1, h2, h3, h4)

    CLI(net)

    net.stop()

def config(r1, r2, gre1, gre2, h1, h2, h3, h4):

    # Hosts, Routers IP configuration
    r1.cmd('ifconfig r1-eth0 140.113.0.2/16')
    r1.cmd('ifconfig r1-eth1 20.0.0.1/8')

    r2.cmd('ifconfig r2-eth0 140.114.0.2/16')
    r2.cmd('ifconfig r2-eth1 20.0.0.2/8')

    gre1.cmd('ifconfig gre1-eth0 10.0.0.3/8')
    gre1.cmd('ifconfig gre1-eth1 140.113.0.1/16')

    gre2.cmd('ifconfig gre2-eth0 10.0.1.3/8')
    gre2.cmd('ifconfig gre2-eth1 140.114.0.1/16')

    # Host routing table configuration
    h1.cmd('route add default gw 10.0.0.3')
    h2.cmd('route add default gw 10.0.0.3')
    h3.cmd('route add default gw 10.0.1.3')
    h4.cmd('route add default gw 10.0.1.3')

    # Router routing table configuration
    r1.cmd('route add -net 140.113.0.0/16 gw 140.113.0.1')
    r1.cmd('route add -net 140.114.0.0/16 gw 20.0.0.2')

    r2.cmd('route add -net 140.114.0.0/16 gw 140.114.0.1')
    r2.cmd('route add -net 140.113.0.0/16 gw 20.0.0.1')

    gre1.cmd('ip route add 140.114.0.0/16 via 140.113.0.2')
    gre1.cmd('ip link add vx type gretap remote 140.114.0.1  \
    local 140.113.0.1 encap fou  encap-sport 65534 encap-dport 65535')
    gre1.cmd('ip link set vx up')
    gre1.cmd('ip link add br0 type bridge')
    gre1.cmd('ip link set gre1-eth0 master br0')
    gre1.cmd('ip link set vx master br0')
    gre1.cmd('ip link set br0 up')
    gre1.cmd('ip fou add port 65534 ipproto 47')

    gre2.cmd('ip route add 140.113.0.0/16 via 140.114.0.2')
    gre2.cmd('ip link add vx type gretap remote 140.113.0.1  \
    local 140.114.0.1 encap fou  encap-sport 65535 encap-dport 65534')
    gre2.cmd('ip link set vx up')
    gre2.cmd('ip link add br0 type bridge')
    gre2.cmd('ip link set gre2-eth0 master br0')
    gre2.cmd('ip link set vx master br0')
    gre2.cmd('ip link set br0 up')
    gre2.cmd('ip fou add port 65535 ipproto 47')


if __name__ == '__main__':
    topology()


