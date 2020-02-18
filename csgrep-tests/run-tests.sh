#!/bin/bash

rm -rf report
mkdir report

for test in *input.txt; do
  for mode in "" "-v"; do
    echo -n "$test$mode: "

    if ! ../divine2csgrep.py $mode $test > $test$mode.csgrep; then
      if [[ $test =~ "invalid" ]]; then
        echo -e "\e[1m\e[92mPASS\e[0m"
        continue
      fi

      echo -e "\e[1m\e[91mCONVERT FAIL\e[0m"
      continue
    fi

    if ! csgrep $test$mode.csgrep &> /dev/null; then
      echo -e "\e[1m\e[91mCSGREP FAIL\e[0m"
      continue
    fi

    if diff -u $(echo $test | cut -d '-' -f1)*-output$mode.txt \
          $test$mode.csgrep &> report/$test$mode.diff; then
      echo -e "\e[1m\e[92mPASS\e[0m"
    else
      echo -e "\e[1m\e[91mDIFF FAIL\e[0m"
      cat report/$test$mode.diff
    fi
  done

  rm ./*.csgrep
done
