package main

import (
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"strings"
)

type IPStatus struct {
	IP     string
	Status bool
	Info   string
}

func checkPing(ip string, channel chan *IPStatus) {
	s := &IPStatus{}
	defer func() { channel <- s }()
	out, err := exec.Command("ping", "-i", "0.05", "-c", "200", "-q", ip).Output()
	if err != nil {
		fmt.Println(err.Error())
		s.IP = ip
		s.Status = false
		s.Info = err.Error()
		return
	}
	o := strings.Split(string(out), "\n")
	s.IP = ip
	s.Status = true
	info := strings.Split(o[len(o)-3], ",")[2]
	s.Info = strings.TrimSpace(info)
	if s.Info != "0% packet loss" {
		s.Status = false
	}
}

func main() {
	runtime.GOMAXPROCS(10)
	channel := make(chan *IPStatus)
	number := len(os.Args)
	status := true
	var message string
	for _, ip := range os.Args[1:] {
		go checkPing(ip, channel)
	}
L:
	for {
		select {
		case data := <-channel:
			number -= 1
			if !data.Status && status {
				status = false
				message += fmt.Sprintf("%s %s,", data.IP, data.Info)
			}
			if number == 1 {
				break L
			}
		}
	}
	message = strings.TrimSuffix(message, ",")
	if !status {
		fmt.Printf("status=Failed, %s\n", message)
	} else {
		fmt.Printf("status=OK, all ips ping success")
	}
}
