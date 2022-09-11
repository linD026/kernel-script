#!/usr/bin/env bash


LIST_KERNEL=`ls | grep "linux*"`

function target_is_in_list()
{
	for item in $LIST_KERNEL; do
		if [[ "$item" == "$1" ]]; then
			return 0
		fi
	done
	return 1
}

target_is_in_list $1
