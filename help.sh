#!/usr/bin/env bash

echo "========================================="
echo "[current kernel]: $(uname -r)"
echo "========================================="

echo ""
echo "===== command ====="
echo ""

echo "[build]  build_kernel  -  build the kernel from:"
LIST_KERNEL=`ls | grep "linux*"`
for item in $LIST_KERNEL; do
	echo "	- $item:"
	BRANCH="$(git -C $item branch 2>&1)"
	while read -r line; do
		echo -n "	"
		if [[ "$line" =~ "fatal:" ]]; then
			echo "      NO BRANCH"
			break;
		fi
		if [ `echo $line | grep -c "/* "` -eq 0 ]; then
			echo -n "  "
		fi
		echo "    $line"
	done <<< $BRANCH
done

echo "[remove] remove_kernel -  remove (uninstall) the installed kernel:"
LIST_KERNEL=`ls /boot/initrd.img-*`
for item in $LIST_KERNEL; do
	tmp=`echo "$item" | awk -F "img-" '{print $2}'`
	echo "	- $tmp"
done
echo "[check] check_patch    -  check the patch format by kernel scripts"

echo ""
echo "======= dpkg ======="
echo ""

dpkg --list | grep linux-image
dpkg --list | grep kernel-image
dpkg --list | grep linux-header
dpkg --list | grep linux-modules
