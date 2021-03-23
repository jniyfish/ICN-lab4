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

    # Create Host, from h1 to h8
    h1 = net.addHost('h1',ip='140.114.44.44/16')
    h2 = net.addHost('h2',ip='140.115.55.55/16')
    h3 = net.addHost('h3',ip='140.113.33.33/16')
    
    # Create Router, from r1 to r6
    r1 = net.addHost('r1', cls=Router)
    r2 = net.addHost('r2', cls=Router)
    r3 = net.addHost('r3', cls=Router)
    GW = net.addHost('GW', cls=Router)
    # link pairs
    links = [('h1', 'r1'), ('h2', 'r2'),
             ('r1', 'r3'), ('r2', 'r3'),
             ('GW', 'r3'), ('GW', 'h3')
            ]
    #create link
    for link in links:
        src, dst = link
        net.addLink(src, dst)

    net.start()

    # Configure network manually
    config(r1, r2, r3, GW, h1, h2, h3)
    CLI(net)
    net.stop()

def config(r1, r2, r3, GW, h1, h2, h3):

    r1.cmd('ifconfig r1-eth0 10.0.0.5/8')
    r1.cmd('ifconfig r1-eth1 140.114.0.1/16')

    r2.cmd('ifconfig r2-eth0 10.0.0.6/8')
    r2.cmd('ifconfig r2-eth1 140.115.0.1/16')

    r3.cmd('ifconfig r3-eth0 140.114.0.2/16')
    r3.cmd('ifconfig r3-eth1 140.115.0.2/16')
    r3.cmd('ifconfig r3-eth2 140.113.0.2/16')

    GW.cmd('ifconfig GW-eth0 140.113.0.1/16')

    h1.cmd('ip route add default dev h1-eth0')
    h2.cmd('ip route add default dev h2-eth0')
    h3.cmd('ip route add default dev h3-eth0')

    r1.cmd('route add -net 140.113.0.0/16 gw 140.114.0.2')
    r2.cmd('route add -net 140.113.0.0/16 gw 140.115.0.2')

    GW.cmd('route add -net 140.114.0.0/16 gw 140.113.0.2')
    GW.cmd('route add -net 140.115.0.0/16 gw 140.113.0.2')
    
    GW.cmd('ip link add br0 type bridge')
    GW.cmd('brctl addif br0 GW-eth1')
    GW.cmd('ip link set br0 up')

    r1.cmd('ip link add GRE type gretap remote 140.113.0.1 local 140.114.0.1')
    r1.cmd('ip link set GRE up')
    r1.cmd('ip link add br0 type bridge')
    r1.cmd('brctl addif br0 r1-eth0')
    r1.cmd('brctl addif br0 GRE')
    r1.cmd('ip link set br0 up')
    r1.cmd('ip fou add port 12345 ipproto 47')

    r2.cmd('ip link add GRE type gretap remote 140.113.0.1 local 140.115.0.1')
    r2.cmd('ip link set GRE up')
    r2.cmd('ip link add br0 type bridge')
    r2.cmd('brctl addif br0 r2-eth0')
    r2.cmd('brctl addif br0 GRE')
    r2.cmd('ip link set br0 up');
    r2.cmd('ip fou add port 22222 ipproto 47')

if __name__ == '__main__':
    topology()


