#!/usr/bin/env bash

rm -rf results
mkdir results

isla -O fuzz -n 10 -d results/ \
  --constraint '<type> = "08 "' \
  --constraint '<code> = "00 "' \
  --constraint 'internet_checksum(<start>, <checksum>)' \
  --constraint '
exists int cnt: (
  str.to.int(cnt) mod 2 = 0 and 
  str.to.int(cnt) > 0 and 
  count(<payload_data>, "<byte>", cnt))' \
  'python send_icmp.py {}' \
  grammar.bnf internet_checksum.py

cat results/*_stdout.txt
