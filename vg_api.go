package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"sync"
	"time"
)

// Reference imports to suppress errors if they are not otherwise used.
var (
	_ sync.WaitGroup
	_ = fmt.Errorf("%s", "ingore")
	_ = http.NewServeMux()
)

var (
	wg sync.WaitGroup
)

type InternalData struct {
	Data []interface{} `json:"data"`
	Name string        `json:"name"`
}

func getTimeFormat(t time.Time) string {
	y := t.Year()
	m := int(t.Month())
	d := t.Day()
	H := t.Hour()
	M := t.Minute()
	return fmt.Sprintf("%v/%02v/%02v-%02v:%02v:00", y, m, d, H, M)
}

func checkTSDB(s string) {
	defer wg.Done()
	current := time.Now()
	originUrl := "http://loki.hy01.internal.wandoujia.com/tsdb/api/query?type=http&m=avg:%s&start=%s&end=%s"
	startTime := current.Add(-3 * 60 * time.Second)
	stopTime := current.Add(-3*60*time.Second - 10*60*time.Second)
	stopTSDBTime := getTimeFormat(startTime)
	startTSDBTime := getTimeFormat(stopTime)
	realUrl := fmt.Sprintf(originUrl, s, startTSDBTime, stopTSDBTime)

	resp, err := http.Get(realUrl)
	if err != nil {
		fmt.Printf("STATUS=Failed, %s, %#v", err.Error(), resp)
		os.Exit(1)
	}
	v := make(map[string][]InternalData)
	body, err := ioutil.ReadAll(resp.Body)
	err = json.Unmarshal(body, &v)
	if err != nil {
		fmt.Printf("STATUS=Failed, %s, %+v", err.Error(), string(body))
		os.Exit(1)
	}
	for _, item := range v["data"] {
		total := float64(0)
		for i := 1; i <= 5; i++ {
			realData := item.Data[len(item.Data)-i].([]interface{})
			total += realData[1].(float64)
		}
		avg := int64(total / 5)
		fmt.Printf("%s=%d\n", s, avg)
	}
}

func main() {

	if length := len(os.Args); length > 0 {
		for _, item := range os.Args[1:] {
			wg.Add(1)
			go checkTSDB(item)
		}
	} else {
		os.Exit(0)
	}

	wg.Wait()

}
