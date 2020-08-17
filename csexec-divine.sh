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

if [ $# -le 1 ]; then
  usage
  exit 1
fi

echo "Argv: $*" > /dev/tty

i=1
j=0
# Parse divine args
while [[ ! "${!i}" =~ "ld-linux" ]]; do
  ARGS[$((j++))]="${!i}"
  ((i++))
done

# Skip ld-linux and --argv0
((i++))
if [ "${!i}" = "--argv0" ]; then
  ((i += 2))
fi

# Pipe stdin to divine if it is not terminal
if [ ! -t 0 ]; then
  tmp_stdin="$(/usr/bin/mktemp --tmpdir divine-stdinXXX)"
  /usr/bin/cat - >> "$tmp_stdin"

  ARGS[$((j++))]="--stdin"
  ARGS[$((j++))]="$tmp_stdin"

  exec < "$tmp_stdin"
fi

# Process --capture entries
i_bak=$((i++))
while [ -n "${!i}" ]; do
  if [ -e "${!i}" ]; then
    ARGS[((j++))]="--capture"

    if [[ ! "${!i}" =~ "^/" ]]; then
      prefix="./"
    fi

    ARGS[((j++))]="${prefix}${!i}"
    ((i++))
  fi

  ((i++))
done

# Process the rest of arguments
i="$i_bak"
while [ -n "${!i}" ]; do
  ARGS[$((j++))]="${!i}"
  ((i++))
done

echo "Executing 'divine ${ARGS[*]}'" 1> /dev/tty 2>&1
divine "${ARGS[@]}" 1> /dev/tty 2>&1

i=1
while [[ ! "${!i}" =~ "ld-linux" ]]; do
  ((i++))
done

ARGS=( "$@" )
exec "${ARGS[@]:i-1}"
