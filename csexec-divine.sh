#!/usr/bin/bash

usage() {
  cat << EOF
USAGE: $0 -d DIVINE_ARGS ARGV
1) Build the source with CC=dioscc CFLAGS='-g -O0' and
   LDFLAGS='-Wl,--dynamic-linker=/usr/bin/csexec-loader'.
2) CSEXEC_WRAP_CMD=$'--skip-ld-preload\acsexec-divine\a-d\acheck' make check
3) Wait for some time.
4) ...
5) Profit!
EOF
}

[[ $# -eq 0 ]] && usage && exit 1

while getopts "d:h" opt; do
  case "$opt" in
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

# Catch stdin for Divine if it is not a terminal
# FIXME: what if /dev/zero is used?
if [ ! -t 0 ]; then
  tmp_stdin="$(/usr/bin/mktemp --tmpdir divine-stdinXXXX)"
  /usr/bin/cat - >> "$tmp_stdin"

  DIVINE_ARGS+=("--stdin" "$tmp_stdin")
  exec < "$tmp_stdin"
fi

# Process --capture entries
i=1
while [ $i -le $# ]; do
  if [ -e "${!i}" ]; then
    DIVINE_ARGS+=("--capture")

    if [[ "${!i}" =~ "^/" ]]; then
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
# FIXME: this may actually slow things down
DIVINE_ARGS+=("--threads" "$(nproc)")

# Run!
divine "${DIVINE_ARGS[@]}" "${ARGV[@]}" 1> /dev/tty 2>&1

# Continue
exec $(csexec --print-ld-exec-cmd) "${ARGV[@]}"
