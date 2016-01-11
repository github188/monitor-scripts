package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"reflect"
	"regexp"
	"strings"
	"sync"
)

type JmxData map[string][]map[string]interface{}

var wg sync.WaitGroup

func getHttp(url string) JmxData {
	var jmx = make(JmxData)
	resp, err := http.Get(url)
	if err != nil {
		os.Exit(1)
	}
	body, _ := ioutil.ReadAll(resp.Body)
	err = json.Unmarshal(body, &jmx)
	if err != nil {
		os.Exit(1)
	}
	return jmx
}

func retValue(item map[string]interface{}, key string) float64 {
	return reflect.ValueOf(item[key]).Float()
}
func RegionData(data []map[string]interface{}) {
	defer wg.Done()
	for _, item := range data {
		if item["name"] != "Hadoop:service=HBase,name=RegionServer,sub=Regions" {
			continue
		}
		var ret = make(map[string]float64)
		re := regexp.MustCompile("[Nn]amespace_(.*)_table_(.*)_region_.*_metric_(.*)")
		find := regexp.MustCompile("^[Nn]amespace_")

		for k, _ := range item {
			if ret := find.FindString(k); len(ret) == 0 {
				continue
			}

			key := re.ReplaceAllString(k, "${1}|${2}|${3}")
			if t := reflect.TypeOf(item[k]).Kind(); t != reflect.Float64 {
				continue
			}
			value := retValue(item, k)
			if _, exist := ret[key]; exist {
				ret[key] += value
			} else {
				ret[key] = value
			}
		}
		for k, v := range ret {
			keys := strings.Split(k, "|")
			fmt.Printf("optsdb:%s|%.1f|namespace|%s|table|%s\n", keys[2], v, keys[0], keys[1])
		}
	}
}

func WALData(data []map[string]interface{}) {
	defer wg.Done()
	var ret = make(map[string]float64)
	for _, item := range data {
		if item["name"] != "Hadoop:service=HBase,name=RegionServer,sub=WAL" {
			continue
		}
		syncTimeAvg := retValue(item, "SyncTime_mean")
		syncTimeMax := retValue(item, "SyncTime_max")
		ret["SyncTime_mean"] = syncTimeAvg
		ret["SyncTime_max"] = syncTimeMax
	}
	for k, v := range ret {
		fmt.Printf("optsdb:%s|%.1f\n", k, v)
	}
}

func ServerData(data []map[string]interface{}) {
	defer wg.Done()
	var ret = make(map[string]float64)
	for _, item := range data {
		if item["name"] != "Hadoop:service=HBase,name=RegionServer,sub=Server" {
			continue
		}
		ret["memStoreSize"] = retValue(item, "memStoreSize")
		ret["totalRequestCount"] = retValue(item, "totalRequestCount")
		ret["readRequestCount"] = retValue(item, "readRequestCount")
		ret["writeRequestCount"] = retValue(item, "writeRequestCount")
		ret["compactionQueueLength"] = retValue(item, "compactionQueueLength")
		ret["flushQueueLength"] = retValue(item, "flushQueueLength")
		ret["updatesBlockedTime"] = retValue(item, "updatesBlockedTime")
		ret["blockCacheFreeSize"] = retValue(item, "blockCacheFreeSize")
		ret["blockCountHitPercent"] = retValue(item, "blockCountHitPercent")
		ret["blockCacheSize"] = retValue(item, "blockCacheSize")
		ret["Mutate_mean"] = retValue(item, "Mutate_mean")
		ret["Get_mean"] = retValue(item, "Get_mean")
		ret["Delete_mean"] = retValue(item, "Delete_mean")
	}
	for k, v := range ret {
		fmt.Printf("optsdb:%s|%.1f\n", k, v)
	}

}

func main() {
	var host string
	if ok := len(os.Args); ok > 1 {
		host = os.Args[1]
	} else {
		host, _ = os.Hostname()
	}
	jmx := getHttp(fmt.Sprintf("http://%s.wandoujia.com:60030/jmx", host))
	wg.Add(3)
	go RegionData(jmx["beans"])
	go WALData(jmx["beans"])
	go ServerData(jmx["beans"])
	wg.Wait()

}
