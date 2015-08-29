#!/bin/bash

cd ../../posts
 
sed -i -r 's!https?://mattscodecave.com/system/uploads/assets/[0-9]{3}/[0-9]{3}/[0-9]{3}/original/([a-zA-Z0-9_\.-]+)\?[0-9]+!/media/\1!g' *.md
sed -i -r 's!https?://mattscodecave.com/system/uploads/assets/[0-9]{3}/[0-9]{3}/[0-9]{3}/thumb/([a-zA-Z0-9_-]+)\.([a-zA-Z]{2,4})\?[0-9]+!/media/thumbs/\1_thumb.\2!g' *.md
