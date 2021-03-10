package main



import (
    "fmt"
    "github.com/google/gopacket"
    "github.com/google/gopacket/layers"
    "github.com/google/gopacket/pcap"
    "log"
    "time"
    "os/exec"
    "strconv"
)

var (
    snapshot_len int32  = 1024
    promiscuous  bool   = false
    err          error
    timeout      time.Duration = 0 * time.Second
    handle       *pcap.Handle
    x = 1
)

func main() {
    //find device
    devices, err := pcap.FindAllDevs()
    device :=""
    //print device
    num := 0
    for _, device := range devices {
        fmt.Printf("%d Name: %s\n", num,device.Name)
        num = num  +1
    }
    //choose device
    chs :=-1
    fmt.Scanf("%d", &chs)
    device = devices[chs].Name
    fmt.Printf("Start listening at $%s\n", device)
    // Open device
    handle, err = pcap.OpenLive(device, snapshot_len, promiscuous, timeout)
    if err != nil {log.Fatal(err) }
    defer handle.Close()

    // Use the handle as a packet source to process all packets
    packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
    pnum:=1
    for packet := range packetSource.Packets() {
        // Process packet here
        fmt.Printf("\nPacket Num [%d]\n", pnum)
        pnum = pnum+1
        printPacketInfo(packet)
    }
}

func printPacketInfo(packet gopacket.Packet) {
    // Let's see if the packet is an ethernet packet
    src := ""
    dst := ""
    str := ""
    sport := 0
    dport := 0
    isGre := 0
    byte :=  packet.Data()

    ethernetLayer := packet.Layer(layers.LayerTypeEthernet)
    if ethernetLayer != nil {
        ethernetPacket, _ := ethernetLayer.(*layers.Ethernet)
        fmt.Println("Source MAC: ", ethernetPacket.SrcMAC)
        fmt.Println("Destination MAC: ", ethernetPacket.DstMAC)
        fmt.Println("Ethernet type: ", ethernetPacket.EthernetType)
    }
    ipLayer := packet.Layer(layers.LayerTypeIPv4)
    if ipLayer != nil {
        ip, _ := ipLayer.(*layers.IPv4)
        src = ip.SrcIP.String()
        dst = ip.DstIP.String()
        fmt.Printf("Src IP %s\n", src)
        fmt.Printf("Dst IP %s\n", dst)
    }

    // Let's see if the packet is UDP
    udpLayer := packet.Layer(layers.LayerTypeUDP)
    if udpLayer != nil {
        udp, _ := udpLayer.(*layers.UDP)
        fmt.Println("Protocol: UDP")
        fmt.Sscanf(udp.SrcPort.String(),"%d(%s",&sport,&str)
        fmt.Sscanf(udp.DstPort.String(),"%d(%s",&dport,&str)
        fmt.Printf("UDP Src port %s\n", strconv.Itoa(sport))
        fmt.Printf("UDP Dst port %s\n", strconv.Itoa(dport))
    }

    vxlanLayer := packet.Layer(layers.LayerTypeVXLAN)
    if vxlanLayer != nil {
        vxlan, _ := vxlanLayer.(*layers.VXLAN)
        fmt.Printf("VNI = %d\n", vxlan.VNI)
    }

    greLayer := packet.Layer(layers.LayerTypeGRE)
    if greLayer != nil {
        isGre = 1
        fmt.Println("Next Layer Protocol: GRE")
        fmt.Println("%d",isGre)
    }
    if len(byte) >= 46 {
        //fmt.Println(byte)
        //fmt.Println(byte[44])
        //fmt.Println(byte[45])
        if byte[44] == 101 && byte[45] == 88 {
            isGre = 1
            fmt.Println("Next Layer Protocol: GRE")
        }
    }
    if isGre == 1 && src!="140.113.0.1"{
        vx:= "gre_iface" + strconv.Itoa(x)
        app:= "ip"
        link:="link"
        add:= "add"
        set:= "set"
        up:= "up"
        typee:= "type"
        gretap:= "gretap"
        remote:= "remote"
        local:="local"
        master:="master"
        br0:="br0"
        encap:="encap"
        fou:="fou"
        esport:= "encap-sport"
        edport:= "encap-dport"
        port:="port"
        ipproto:="ipproto"
        greP:="47"
        
        cmd:=exec.Command(app, link, add, vx, typee, gretap, remote, src, local, dst, encap, fou, esport, strconv.Itoa(dport), edport, strconv.Itoa(sport))
        cmd.CombinedOutput()
        cmd=exec.Command(app, link, set, vx, up)
        cmd.CombinedOutput()
        cmd=exec.Command(app, link, set, vx, master, br0)
        cmd.CombinedOutput()
        cmd=exec.Command(app, fou, add, port, strconv.Itoa(dport), ipproto, greP)
        cmd.CombinedOutput()
        fmt.Println("Tunnel finish")
        x = x+1
    }
}
