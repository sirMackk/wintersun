#!/bin/bash

cd ../../media/
for file in *.{jpg,jpeg,JPG,png}; do convert -resize 500x $file  ./thumbs/${file%%.*}_thumb.${file##*.}; done;
