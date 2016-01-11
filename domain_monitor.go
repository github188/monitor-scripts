package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math"
	"net/http"
	"os"
	"sync"
	"time"
)

var (
	urlAvailableUrl = "http://tsdb2.wandoulabs.com:4242/api/query?start=%s&end=%s&m=sum:url.availability%%7Bdomain=*,path=*%%7D&o=&yrange=%%5B0:%%5D&wxh=1349x735"
	reponseTimeUrl  = "http://tsdb2.wandoulabs.com:4242/api/query?start=%s&end=%s&m=sum:url.responsetime%%7Bdomain=*,path=*%%7D&o=&yrange=%%5B0:%%5D&wxh=1349x735"
	qpsUrl          = "http://tsdb2.wandoulabs.com:4242/api/query?start=%s&end=%s&m=sum:url.qps%%7Bdomain=*,path=*%%7D&o=&yrange=%%5B0:%%5D&wxh=1349x735"
	bandWithUrl     = "http://tsdb2.wandoulabs.com:4242/api/query?start=%s&end=%s&m=sum:url.bandwidth%%7Bdomain=*,path=*%%7D&o=&yrange=%%5B0:%%5D&wxh=1349x735"
	wg              sync.WaitGroup
	totalDomain     = make(map[string]int)
)

type DataStruct struct {
	Metric string             `json:"metric"`
	Tags   map[string]string  `json:"tags"`
	Dps    map[string]float64 `json:"dps"`
}

func getDomainData(start string, stop string, url string) map[string]float64 {
	dataUrl := fmt.Sprintf(url, start, stop)
	resp, err := http.Get(dataUrl)
	if err != nil {
		fmt.Printf("STATUS=Failed, %s, %#v", err.Error(), resp)
		os.Exit(1)
	}

	var v []DataStruct
	body, err := ioutil.ReadAll(resp.Body)
	err = json.Unmarshal(body, &v)
	if err != nil {
		fmt.Printf("STATUS=Failed, %s, %#v", err.Error(), string(body))
		os.Exit(1)
	}

	domainAvailable := map[string]float64{}
	for _, z := range v {
		domain := z.Tags["domain"]
		path := z.Tags["path"]
		domain = fmt.Sprintf("%s%s", domain, path)
		var available float64 = 0
		for _, tmp := range z.Dps {
			available += tmp
		}
		averageAvailable := available / float64(len(z.Dps))
		if math.IsNaN(averageAvailable) {
			domainAvailable[domain] = float64(0.0)
		} else {
			domainAvailable[domain] = averageAvailable
		}
	}
	return domainAvailable

}

func getTimeFormat(t time.Time) string {
	y := t.Year()
	m := int(t.Month())
	d := t.Day()
	H := t.Hour()
	M := t.Minute()
	return fmt.Sprintf("%v/%02v/%02v-%02v:%02v:00", y, m, d, H, M)
}

func AvailableAlarm() {
	defer wg.Done()
	cmpMessage := ""
	current := time.Now()
	passed1 := current.Add(-3 * 60 * time.Second)
	passed2 := current.Add(-3*60*time.Second - 10*60*time.Second)
	stop := getTimeFormat(passed1)
	start := getTimeFormat(passed2)
	domainAvailable1 := getDomainData(start, stop, urlAvailableUrl)

	passed3 := current.Add(-3*60*time.Second - 1440*60*time.Second)
	passed4 := current.Add(-3*60*time.Second - 1440*60*time.Second - 10*60*time.Second)
	stop2 := getTimeFormat(passed3)
	start2 := getTimeFormat(passed4)
	domainAvailable2 := getDomainData(start2, stop2, urlAvailableUrl)
	for domain, ava1 := range domainAvailable1 {
		if _, small := totalDomain[domain]; !small {
			continue
		}
		if ava2, ok := domainAvailable2[domain]; ok {
			c := ava2 - ava1
			if c > float64(5) && 0 < ava2 {
				cmpMessage += fmt.Sprintf("%s: 现在%.3f 昨天%.3f, 降低%.3f, ", domain, ava1, ava2, c)
			} else if c > float64(1) && float64(99) < ava2 {
				cmpMessage += fmt.Sprintf("%s: 现在%.3f 昨天%.3f, 降低%.3f, ", domain, ava1, ava2, c)
			} else if c > float64(0.1) && float64(99.9) < ava2 {
				cmpMessage += fmt.Sprintf("%s: 现在%.3f 昨天%.3f, 降低%.3f, ", domain, ava1, ava2, c)
			}
		}
	}
	if cmpMessage != "" {
		fmt.Printf("UP_RATE = False,%s\n", cmpMessage)
	} else {
		fmt.Println("UP_RATE = OK, 所有域名可用率正常")
	}
}

func ReponseAlarm() {
	defer wg.Done()
	var cmpMessage string
	current := time.Now()
	passed1 := current.Add(-3 * 60 * time.Second)
	passed2 := current.Add(-3*60*time.Second - 10*60*time.Second)
	stop := getTimeFormat(passed1)
	start := getTimeFormat(passed2)
	domainAvailable1 := getDomainData(start, stop, reponseTimeUrl)

	passed3 := current.Add(-3*60*time.Second - 1440*60*time.Second)
	passed4 := current.Add(-3*60*time.Second - 1440*60*time.Second - 10*60*time.Second)
	stop2 := getTimeFormat(passed3)
	start2 := getTimeFormat(passed4)
	domainAvailable2 := getDomainData(start2, stop2, reponseTimeUrl)
	for domain, resp1 := range domainAvailable1 {
		if _, small := totalDomain[domain]; !small {
			continue
		}
		if resp2, ok := domainAvailable2[domain]; ok && resp1-resp2 > float64(resp2) && resp2 > 50 {
			cmpMessage += fmt.Sprintf("%s: 现在%.3f 昨天%.3f, ", domain, resp1, resp2)

		}
	}
	if cmpMessage != "" {
		fmt.Printf("RESP_TIME = False,%s\n", cmpMessage)
	} else {
		fmt.Println("RESP_TIME = OK, 所有域名响应时间正常")
	}
}

func BandWidthAlarm() {
	defer wg.Done()
	var cmpMessage string
	var currentData, yesterdayData float64
	current := time.Now()
	passed1 := current.Add(-3 * 60 * time.Second)
	passed2 := current.Add(-3*60*time.Second - 10*60*time.Second)
	stop := getTimeFormat(passed1)
	start := getTimeFormat(passed2)
	domainAvailable1 := getDomainData(start, stop, bandWithUrl)

	passed3 := current.Add(-3*60*time.Second - 1440*60*time.Second)
	passed4 := current.Add(-3*60*time.Second - 1440*60*time.Second - 10*60*time.Second)
	stop2 := getTimeFormat(passed3)
	start2 := getTimeFormat(passed4)
	domainAvailable2 := getDomainData(start2, stop2, bandWithUrl)
	for domain, band1 := range domainAvailable1 {
		if _, small := totalDomain[domain]; !small {
			continue
		}
		if band2, ok := domainAvailable2[domain]; ok {
			currentData += band1 * 8
			yesterdayData += band2 * 8
		}
	}
	fmt.Print(cmpMessage)
	fmt.Printf("|%-45s|Current BandWidth:%-15.4f|Yesterday BandWidth:%-15.4f|difference:%-15.4f|\n", "Total BandWidth", currentData, yesterdayData, currentData-yesterdayData)

}

func QpsAlarm() {
	defer wg.Done()
	var cmpMessage string
	current := time.Now()
	passed1 := current.Add(-3 * 60 * time.Second)
	passed2 := current.Add(-3*60*time.Second - 10*60*time.Second)
	stop := getTimeFormat(passed1)
	start := getTimeFormat(passed2)
	domainAvailable1 := getDomainData(start, stop, qpsUrl)

	passed3 := current.Add(-3*60*time.Second - 1440*60*time.Second)
	passed4 := current.Add(-3*60*time.Second - 1440*60*time.Second - 10*60*time.Second)
	stop2 := getTimeFormat(passed3)
	start2 := getTimeFormat(passed4)
	domainAvailable2 := getDomainData(start2, stop2, qpsUrl)
	for domain, qps1 := range domainAvailable1 {
		if _, small := totalDomain[domain]; !small {
			continue
		}
		if qps2, ok := domainAvailable2[domain]; ok {
			cmpMessage += fmt.Sprintf("|%-45s|Current Qps:%-15.4f|Yesterday QPS:%-15.4f|Difference:%-15.4f|\n", domain, qps1, qps2, qps1-qps2)
		}
	}
}

func main() {
	if length := len(os.Args); length > 0 {
		for _, item := range os.Args[1:] {
			totalDomain[item] = 1
		}
	} else {
		os.Exit(0)
	}
	wg.Add(2)
	//go QpsAlarm()
	go AvailableAlarm()
	go ReponseAlarm()
	//go BandWidthAlarm()
	wg.Wait()
}
