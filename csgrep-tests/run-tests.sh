#!/bin/bash

rm -rf report
mkdir report

for test in *input.txt; do
    echo -n "$test: "
    ../divine2csgrep.py $test
    OUTPUT=$()

    if diff -u $(echo $test | cut -d '-' -f1)*-output.txt $test.csgrep &> report/$test.diff
    then
        echo -e "\e[1m\e[92mPASS\e[0m"
    else
        echo -e "\e[1m\e[91mFAIL\e[0m"
	cat report/$test.diff
    fi

    rm *.csgrep
done	
