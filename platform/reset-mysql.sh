#!/bin/bash

if [ -n "$1" ]; then
    DB_NAME="$1"
else
    DB_NAME="tcm"
fi

if [ -n "$2" ]; then
    DB_USER="$2"
else
    DB_USER="root"
fi

mysqladmin -u "$DB_USER" drop "$DB_NAME"
mysqladmin -u "$DB_USER" create "$DB_NAME"

tmpsql=`mktemp tmp.XXXXXX`
cat db_scripts/db_tcm_create_empty_db_script.sql > $tmpsql
cat db_scripts/db_tcm_update_db_script_?.sql >> $tmpsql
cat db_scripts/db_tcm_update_db_script_??.sql >> $tmpsql
mysql -u "$DB_USER" "$DB_NAME" < $tmpsql
rm $tmpsql
