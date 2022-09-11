#!/usr/bin/env bash

function kpatch () {
  patch=$1
  shift
  git send-email \
    --cc-cmd="./scripts/get_maintainer.pl --norolestats $patch" \
    $@ $patch
}

set +x

TEST="
	--to shiyn.lin@gmail.com
"

REC="
	--to corbet@lwn.net
	--cc tglx@linutronix.de
	--cc mingo@redhat.com
	--cc bp@alien8.de
	--cc dave.hansen@linux.intel.com
	--cc x86@kernel.org
	--cc hpa@zytor.com
	--cc linux-kernel@vger.kernel.org
	--cc linux-doc@vger.kernel.org
"

echo "file: $1"
echo "test send to $TEST"
echo "send to $REC"

#git send-email $REC $1
#git send-email $TEST $1
