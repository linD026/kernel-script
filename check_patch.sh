#!/usr/bin/env bash

ls | grep "linux*"

while read -p "[patch] Which kernel: " TARGET_DIR; do
	if [[ "$TARGET_DIR" = "" ]]; then
		echo "[build] exit"
		exit 0
	fi
	if ./script/target_is_in_list.sh $TARGET_DIR; then
		break
	fi
	echo "[patch] $TARGET_DIR not exist, plz try again"
done

echo ""
echo "[patch] git branch:"
git -C $TARGET_DIR branch
echo ""

echo "[patch] patch file(s):"
ls $TARGET_DIR | grep ".*\.patch"
LIST_PATCH=`ls $TARGET_DIR | grep ".*\.patch"`

function patch_is_in_list()
{
	for item in $LIST_PATCH; do
		if [[ "$item" == "$1" ]]; then
			return 0
		fi
	done
	return 1
}

echo ""
while read -p "[patch] Which patch (ENTER to exit): " PATCH; do
	if [[ "$PATCH" = "" ]]; then
		echo "[patch] exit"
		exit 0
	fi
	if patch_is_in_list $PATCH; then
		break
	fi
	echo "[patch] $PATCH not exist, plz try again"
done

# scripts may not detect the right commit when using
# ./$TARGET_DIR/script.pl file
pushd $TARGET_DIR
echo ""
./scripts/checkpatch.pl $PATCH
echo ""
./scripts/get_maintainer.pl $PATCH
echo ""
popd
