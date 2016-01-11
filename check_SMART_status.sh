disks=`lsblk -a | awk '{if ($6 == "disk") print $1}'|egrep -v "(ram|vd)"`
vars="reread_count read_uncorrected_error rewrite_count write_uncorrected_error reverify_count verify_uncorrected_error"
for disk in $disks
do
        disk_path=/dev/$disk
        #status=`smartctl -H $disk_path |awk -F':' '/SMART Health Status/ {print $2}'|sed 's/^\s*//g'`
        smartctl -a $disk_path | awk '
        /read:/ {printf $4 " " $8 " "}
        /write:/ {printf $4 " " $8 " "}
        /verify:/ {printf $4 " " $8 "\n"}'|
                (while read $vars;
                do
                        for var in $vars;
                        do
                                echo "opentsdb:system.disk.smart.$var|$(eval echo \$$var)|disk|$disk"
                        done;
                done;
                )

        #echo "STATUS=$status,disk $disk_path status is $status"
done
