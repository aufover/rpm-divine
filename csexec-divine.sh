#!/usr/bin/bash

usage() {
  cat << EOF
USAGE:
1) Build the source with CC=dioscc CFLAGS='-g -O0' and
   LDFLAGS='-Wl,--dynamic-linker=/usr/bin/csexec-loader'.
2) CSEXEC_WRAP_CMD=$'csexec-divine\acheck' make check
3) Wait for some time.
4) ...
5) Profit!
EOF
}

set -ex

if [ $# -le 1 ]; then
  usage
  exit 1
fi

i=1
while [ -n "${!i}" ]; do
  # Skip LD_LINUX_SO
  if [[ "${!i}" =~ "ld-linux" ]]; then
    ((i++))

    # Skip --argv0
    if [ "${!i}" = "--argv0" ]; then
      ((i += 2))
    fi
  fi

  ARGS="$ARGS ${!i}"
  ((i++))
done

echo "Executing 'divine$ARGS'" 1> /dev/tty 2>&1
exec divine $ARGS 1> /dev/tty 2>&1
