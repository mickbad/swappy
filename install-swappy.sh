#!/bin/bash

if [ "$UID" -ne 0 ]; then
	echo "must be root"
	echo "we only install swappy.yml to /etc/swappy.yml"
	exit 1
fi

cp ./scripts/swappy.yml /etc/swappy.yml
echo "done"
