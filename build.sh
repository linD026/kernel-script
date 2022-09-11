#!/usr/bin/env bash

ls | grep "linux*"

while read -p "[build] Which kernel to make config (ENTER to exit): " TARGET_DIR; do
	if [[ "$TARGET_DIR" = "" ]]; then
		echo "[build] exit"
		break
	fi
	if ./script/target_is_in_list.sh $TARGET_DIR; then
		sudo make -C $TARGET_DIR menuconfig
		# sudo make -C $TARGET_DIR x86_64_defconfig
		break
	fi
	echo "[build] $TARGET_DIR not exist, plz try again"
done

read -p "[build] Compile kernel: " READY
if [[ "$READY" = $yesexpr ]]; then
	sudo make -C $TARGET_DIR -j12 bindeb-pkg
	if [ $? -ne 0 ]; then
		echo "[build] failed"
		exit 1
	fi
fi

echo ""
echo "---"
echo "Other:"
echo " - make subtree=\$(pwd) ARCH=x86 cscope tags && cscope -b -q -k"
echo " - tips"
echo "    - Using following commands to install:"
echo "    - $ sudo dpkg -i ../linux-headers-5.16.0-rc5+_5.16.0-rc5+-3_amd64.deb"
echo "    - $ sudo dpkg -i ../linux-image-5.16.0-rc5+_5.16.0-rc5+-3_amd64.deb"
echo "    - /usr/src/linux-headers-3.16.0.[69|71|73|..]"
echo ""
echo "https://www.cyberciti.biz/faq/debian-redhat-linux-delete-kernel-command/"
