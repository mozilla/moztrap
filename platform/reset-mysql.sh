#!/bin/bash

tmpsql=`mktemp tmp.XXXXXX`
cat db_scripts/db_tcm_create_empty_db_script.sql | grep -v "GRANT ALL PRIVILEGES" > $tmpsql
cat db_scripts/db_tcm_update_db_script_?.sql >> $tmpsql
cat db_scripts/db_tcm_update_db_script_??.sql >> $tmpsql
mysql -uroot < $tmpsql
rm $tmpsql
