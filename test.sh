#!/bin/bash

for file in `find . -name "*_test.py"`
do
 if [[ $file =~ "smoke_test" ]]; then
   continue
 fi
 echo $file;
 $file;
done
