package main

import (
	"fmt"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
)

var (
	CheckCommand = [4]string{"MegaCli", "-PDList", "-aALL", "-NoLog"}
	CheckResult  = make(map[string]map[string]map[string]int64)
)

func numToChar(s string) string {
	num, _ := strconv.Atoi(strings.TrimSpace(s))
	num += 1
	return fmt.Sprintf("第%d块盘", num)
}

func main() {
	cmd := exec.Command(CheckCommand[0], CheckCommand[1:]...)
	out, _ := cmd.Output()
	outArray := strings.Split(string(out), "\n")
	var currentSlot string
	var currentID string
	for _, line := range outArray {
		if line == "" {
			continue
		}
		if ok, _ := regexp.MatchString("^Adapter.*", line); ok {
			currentSlot = line
			if _, exist := CheckResult[currentSlot]; !exist {
				CheckResult[currentSlot] = make(map[string]map[string]int64)
			}
		} else if dev, _ := regexp.MatchString("^Device Id", line); dev {
			tmp := strings.Split(line, ":")
			currentID = numToChar(tmp[1])
			if _, exist := CheckResult[currentSlot][currentID]; !exist {
				CheckResult[currentSlot][currentID] = make(map[string]int64)
			}

		} else if ok, _ := regexp.MatchString("Media Error\\s{1}Count", line); ok {
			tmp := strings.Split(line, ":")
			_, v := tmp[0], tmp[1]
			value, _ := strconv.ParseInt(strings.TrimSpace(v), 10, 64)
			CheckResult[currentSlot][currentID]["Media_Error"] = value
		} else if ok, _ := regexp.MatchString("Other Error\\s{1}Count", line); ok {
			tmp := strings.Split(line, ":")
			_, v := tmp[0], tmp[1]
			value, _ := strconv.ParseInt(strings.TrimSpace(v), 10, 64)
			CheckResult[currentSlot][currentID]["Other_Error"] = value
		}
	}
	for slot, value := range CheckResult {
		for k, v := range value {
			num := strings.Split(slot, " ")[1]
			num = strings.Replace(num, "#", "", -1)
			for subK, subV := range v {
				fmt.Printf("%s:%s:%s=%d\n", num, k, subK, subV)
				re := regexp.MustCompile("\\d+")
				kk := re.FindAllString(k, -1)
				fmt.Printf("optsdb:system.disk.%s|%d|slot|%s|disk|%s\n", subK, subV, num, kk[0])
			}
		}
	}
}
