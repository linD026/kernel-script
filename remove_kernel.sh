#!/usr/bin/env bash

echo "[remove] dpkg: "
dpkg --list | egrep -i 'linux-image|linux-headers'
echo ""

echo "[remove] /boot directory (before): "
ls /boot
echo "[remove] *.old postfix file(s): "
OLD=`ls /boot | grep ".*\.old"`
for item in $OLD; do
	if [[ "$item" = "vmlinuz.old" ]]; then
		continue
	fi
	echo "	$item"
done

read -p "[remove] Delete {config-,initrd.img-,System.map-,vmlinuz-}*.old (Y/N): " READY
case $READY in
	[Yy]* )
		sudo rm -f /boot/{config-,initrd.img-,System.map-,vmlinuz-}*.old;
		sudo update-grub;;
	[Nn]* )
		exit 0;;
	* ) echo "[Skip]"
esac
echo ""

echo "[remove] initrd.img:"
LIST_KERNEL=`ls /boot | grep "initrd.img-*."`
for item in $LIST_KERNEL; do
	tmp=`echo "$item" | awk -F "img-" '{print $2}'`
	echo "	$tmp"
done

read -p "[remove] remove method (Y/N/dpkg): " READY
if [[ "$READY" = "dpkg" ]]; then
	echo "[remove] Selected \"dpkg\" remove"
	dpkg --list | grep linux-image
	read -p "[remove] Which linux-image version: " VERSION
	dpkg --list | grep "$VERSION"
	echo "[remove] $ sudo apt-get remove kernel-image, linux-header, linux-image, linux-modules"
elif [[ "$READY" =~ $yesexpr ]]; then
	echo "[remove] Selected \"manually\" remove"
	echo "[current kernel]: $(uname -r)"

	CURR_KERNEL=`ls /boot/initrd.img-$(uname -r)`

	while read -p "[remove] Which verson (ENTER to exit): " TARGET_KERNEL; do
		if [[ "$TARGET_KERNEL" = "" ]]; then
			echo "[remove] exit"
			exit 0
		fi
		SUCCESS=0
		if [[ ! "$CURR_KERNEL" =~ "$TARGET_KERNEL" ]]; then
			for item in $LIST_KERNEL; do
				if [[ "$item" =~ "$TARGET_KERNEL" ]]; then
					SUCCESS=1
					break
				fi
			done
		fi
		if [ $SUCCESS -eq 1 ]; then
			break
		fi
		echo "[remove] $TARGET_KERNEL is using or may not exist, plz try again"
	done

	echo "[remove] Ready to remove following:"
	ls /boot/{config-,initrd.img-,System.map-,vmlinuz-}$TARGET_KERNEL
	echo "/lib/modules/$(ls /lib/modules | grep $TARGET_KERNEL)"

	sudo rm /boot/{config-,initrd.img-,System.map-,vmlinuz-}$TARGET_KERNEL
	sudo rm -rf /lib/modules/$TARGET_KERNEL
	sudo update-grub
	echo "[remove] Need to check the image is still in dpkg or not"
	echo "[remove] Remove kernel: $TARGET_KERNEL"
	dpkg --list | grep kernel-image
	echo "[remove] If still exists, use following command to cleanup kernel-image:"
	echo "        $ sudo apt-get remove kernel-image-version"
	echo "        $ sudo apt-get autopurge kernel-image-version"
	echo "[remove] Ditto at header, modules, linux-image"
fi
echo "[remove] For more details, see: https://www.cyberciti.biz/faq/debian-redhat-linux-delete-kernel-command/"
