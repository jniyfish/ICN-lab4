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
    h1 = net.addHost('h1',ip='10.0.0.1/8')
    h2 = net.addHost('h2',ip='10.0.0.2/8')
    h3 = net.addHost('h3',ip='10.0.0.3/8')
    h4 = net.addHost('h4',ip='10.0.0.4/8')
    h5 = net.addHost('h5',ip='10.0.1.1/8')
    h6 = net.addHost('h6',ip='10.0.1.2/8')
    
    # Create Switch s1
    s1 = net.addSwitch('s1', failMode='standalone')


    # Create Router, from r1 to r6
    r1 = net.addHost('r1', cls=Router)
    r2 = net.addHost('r2', cls=Router)
    r3 = net.addHost('r3', cls=Router)
    r4 = net.addHost('r4', cls=Router)
    r5 = net.addHost('r5', cls=Router)
    GW = net.addHost('GW', cls=Router)
    # link pairs
    links = [('h1', 'r1'), ('h2', 'r2'),('h3', 'r3'), ('h4', 'r4'),
             ('h5', 's1'), ('h6', 's1'),
             ('r1', 'r5'), ('r2', 'r5'),('r3', 'r5'), ('r4', 'r5'),
             ('GW', 'r5'), ('GW', 's1')
            ]
    #create link
    for link in links:
        src, dst = link
        net.addLink(src, dst)

    net.start()

    # Configure network manually
    config(r1, r2, r3, r4, r5, GW, h1, h2, h3, h4, h5, h6)
    CLI(net)
    pingall(h1, h2, h3, h4)
    net.stop()

def config(r1, r2, r3, r4, r5, GW, h1, h2, h3, h4, h5, h6):

    r1.cmd('ifconfig r1-eth0 10.0.0.5/8')
    r1.cmd('ifconfig r1-eth1 140.114.0.1/16')

    r2.cmd('ifconfig r2-eth0 10.0.0.6/8')
    r2.cmd('ifconfig r2-eth1 140.115.0.1/16')

    r3.cmd('ifconfig r3-eth0 10.0.0.7/8')
    r3.cmd('ifconfig r3-eth1 140.116.0.1/16')

    r4.cmd('ifconfig r4-eth0 10.0.0.8/8')
    r4.cmd('ifconfig r4-eth1 140.117.0.1/16')

    r5.cmd('ifconfig r5-eth0 140.114.0.2/16')
    r5.cmd('ifconfig r5-eth1 140.115.0.2/16')
    r5.cmd('ifconfig r5-eth2 140.116.0.2/16')
    r5.cmd('ifconfig r5-eth3 140.117.0.2/16')
    r5.cmd('ifconfig r5-eth4 140.113.0.2/16')

    GW.cmd('ifconfig GW-eth0 140.113.0.1/16')
    GW.cmd('ifconfig GW-eth1 10.0.0.100/8')

    h1.cmd('route add default gw 10.0.0.5')
    h2.cmd('route add default gw 10.0.0.6')
    h3.cmd('route add default gw 10.0.0.7')
    h4.cmd('route add default gw 10.0.0.8')

    h5.cmd('route add default gw 10.0.0.100')
    h6.cmd('route add default gw 10.0.0.100')

    r1.cmd('route add -net 140.113.0.0/16 gw 140.114.0.2')
    r2.cmd('route add -net 140.113.0.0/16 gw 140.115.0.2')
    r3.cmd('route add -net 140.113.0.0/16 gw 140.116.0.2')
    r4.cmd('route add -net 140.113.0.0/16 gw 140.117.0.2')

    GW.cmd('route add -net 140.114.0.0/16 gw 140.113.0.2')
    GW.cmd('route add -net 140.115.0.0/16 gw 140.113.0.2')
    GW.cmd('route add -net 140.116.0.0/16 gw 140.113.0.2')
    GW.cmd('route add -net 140.117.0.0/16 gw 140.113.0.2')
    
    #static gre on node GW
    #GW.cmd('ip link add br0 type bridge')
    #GW.cmd('ip link set GW-eth1 master br0');
    #GW.cmd('ip link set br0 up');
    #GW.cmd('ip link add gre1 type gretap remote 140.114.0.1 local 140.113.0.1 ')
    #GW.cmd('ip link set gre1 up')
    #GW.cmd('ip link set gre1 master br0');
    #GW.cmd('ip link add gre2 type gretap remote 140.115.0.1 local 140.113.0.1 ')
    #GW.cmd('ip link set gre2 up')
    #GW.cmd('ip link set gre2 master br0');
    #GW.cmd('ip link add gre3 type gretap remote 140.116.0.1 local 140.113.0.1 ')
    #GW.cmd('ip link set gre3 up')
    #GW.cmd('ip link set gre3 master br0');
    #GW.cmd('ip link add gre4 type gretap remote 140.117.0.1 local 140.113.0.1 ')
    #GW.cmd('ip link set gre4 up')
    #GW.cmd('ip link set gre4 master br0');

    r1.cmd('ip link add vx type gretap remote 140.113.0.1 local 140.114.0.1 ')
    r1.cmd('ip link set vx up')
    r1.cmd('ip link add br0 type bridge')
    r1.cmd('ip link set r1-eth0 master br0');
    r1.cmd('ip link set vx master br0');
    r1.cmd('ip link set br0 up');

    r2.cmd('ip link add vx type gretap remote 140.113.0.1 local 140.115.0.1')
    r2.cmd('ip link set vx up')
    r2.cmd('ip link add br0 type bridge')
    r2.cmd('ip link set r2-eth0 master br0');
    r2.cmd('ip link set vx master br0');
    r2.cmd('ip link set br0 up');

    r3.cmd('ip link add vx type gretap remote 140.113.0.1 local 140.116.0.1')
    r3.cmd('ip link set vx up')
    r3.cmd('ip link add br0 type bridge')
    r3.cmd('ip link set r3-eth0 master br0');
    r3.cmd('ip link set vx master br0');
    r3.cmd('ip link set br0 up');

    r4.cmd('ip link add vx type vxlan id 100 dstport 4789 remote 140.113.0.1 local 140.117.0.1 dev r4-eth1')
    r4.cmd('ip link set vx up')
    r4.cmd('ip link add br0 type bridge')
    r4.cmd('ip link set r4-eth0 master br0');
    r4.cmd('ip link set vx master br0');
    r4.cmd('ip link set br0 up');


if __name__ == '__main__':
    topology()

