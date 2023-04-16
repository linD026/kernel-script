#!/usr/bin/env bash

# TO: per-line: name <email>
# CC: ditto
# PATCH: per-line: patch file name

TO=`cat send-to.txt`
CC=`cat send-cc.txt`
PATCH=`cat send-patch.txt`

IFS='
'

# prefix to from
function for_each_line() {
	args=("$@")
	from="${args[2]}"
	for line in $from; do
		echo "$1\"${line//\"/\\\"}\" \\" >> $2
	done
}

touch send-email.sh
echo "#!/usr/bin/env bash" > send-email.sh
echo "" >> send-email.sh
echo "git send-email \\" >> send-email.sh
for_each_line "--to=" send-email.sh "${TO[@]}"
for_each_line "--cc=" send-email.sh "${CC[@]}"

for line in $PATCH; do
	echo "$line \\" >> send-email.sh
done

echo "" >> send-email.sh
