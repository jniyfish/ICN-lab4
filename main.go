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
    snapshot_len int32  = 65536
    promiscuous  bool   = false
    err          error
    timeout      time.Duration = 0 * time.Second
    handle       *pcap.Handle
    filter       string =""
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
    
    fmt.Println("Insert BPF filter expression: ")
    fmt.Scanln(&filter)
    filter ="ip proto gre"
    fmt.Printf("filter: %s\n", filter)
    pnum:=1
    for true {
        handle, err = pcap.OpenLive(device, snapshot_len, promiscuous, timeout)
        err = handle.SetBPFFilter(filter)
        packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
        for packet := range packetSource.Packets() {
            // Process packet here
            fmt.Printf("\nPacket Num [%d]\n", pnum)
            pnum = pnum+1
            printPacketInfo(packet)
            handle.Close()
            break;
        }
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
        if byte[44] == 101 && byte[45] == 88 {
            isGre = 1
            fmt.Println("Next Layer Protocol: GRE")
        }
    }
    if isGre == 1 && src!="140.113.0.1"{
        
        if src == "140.114.0.1"{
            filter = "not host 140.114.0.1 and ip proto gre"
        } else if src == "140.115.0.1"{
            filter = "not host 140.115.0.1 and ip proto gre"
        } else if src == "140.114.0.1" && (filter == "not host 140.115.0.1 and ip proto gre") {
            filter = "not host (140.114.0.1 and 140.115.0.1) and ip proto gre"
        } else if src == "140.115.0.1" && (filter == "not host 140.114.0.1 and ip proto gre"){
            filter = "not host (140.114.0.1 and 140.115.0.1) and ip proto gre"
        }
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
        //encap:="encap"
        //fou:="fou"
        //esport:= "encap-sport"
        //edport:= "encap-dport"
        //port:="port"
        //ipproto:="ipproto"
        //greP:="47"
        
        cmd:=exec.Command(app, link, add, vx, typee, gretap, remote, src, local, dst)
        cmd.CombinedOutput()
        cmd=exec.Command(app, link, set, vx, up)
        cmd.CombinedOutput()
        cmd=exec.Command(app, link, set, vx, master, br0)
        cmd.CombinedOutput()
        fmt.Println("Tunnel finish")
        x = x+1
    }
}
