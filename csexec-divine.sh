#!/usr/bin/bash

usage() {
  cat << EOF
USAGE: $0 -d DIVINE_ARGS ARGV
1) Build the source with CC=dioscc CFLAGS='-g -O0' and
   LDFLAGS='-Wl,--dynamic-linker=/usr/bin/csexec-loader'.
2) CSEXEC_WRAP_CMD=$'--skip-ld-linux\acsexec-divine\a-l\aLOGDIR\a-d\acheck' make check
3) Wait for some time.
4) ...
5) Profit!
EOF
}

[[ $# -eq 0 ]] && usage && exit 1

while getopts "l:d:h" opt; do
  case "$opt" in
    l)
      LOGDIR="$OPTARG"
      ;;
    d)
      DIVINE_ARGS=($OPTARG)
      ;;
    h)
      usage && exit 0
      ;;
    *)
      usage && exit 1
      ;;
  esac
done

shift $((OPTIND - 1))
ARGV=("$@")

if [ -z "$LOGDIR" ]; then
  echo "-l LOGDIR option is mandatory!"
  exit 1
fi

# Catch stdin for Divine if it is not a terminal
if [ ! -t 0 ]; then
  tmp_stdin="$(/usr/bin/mktemp --tmpdir divine-stdinXXXX)"
  # FIXME: what if /dev/zero is used?
  /usr/bin/timeout 5 /usr/bin/cat - >> "$tmp_stdin"

  DIVINE_ARGS+=("--stdin" "$tmp_stdin")
  exec < "$tmp_stdin"
fi

# Process --capture entries
i=1
while [ $i -le $# ]; do
  if [ -e "${!i}" ]; then
    DIVINE_ARGS+=("--capture")

    if [[ "${!i}" =~ ^/ ]]; then
      prefix=""
    else
      prefix="./"
    fi

    DIVINE_ARGS+=("$prefix${!i}")
    ((i++))
  fi

  ((i++))
done

# Make it parallel
DIVINE_ARGS+=("--threads" "2")

# Save the report
DIVINE_ARGS+=("--report-filename" "$LOGDIR/pid-$$.report")

# Do not trace stdout
DIVINE_ARGS+=("-o" "stdout:notrace")

# Run and convert!
/usr/bin/env -i /usr/bin/bash -lc 'exec "$@"' divine \
  /usr/bin/divine "${DIVINE_ARGS[@]}" "${ARGV[@]}" 2> "$LOGDIR/pid-$$.err" | \
  /usr/bin/tee "$LOGDIR/pid-$$.out" | \
  /usr/bin/divine2csgrep > "$LOGDIR/pid-$$.out.conv"

# Continue
exec $(/usr/bin/csexec --print-ld-exec-cmd ${CSEXEC_ARGV0}) "${ARGV[@]}"
