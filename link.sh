#!/usr/bin/env bash

src=`pwd`
dest=$1

if [ ! `echo $dest | grep "/$"` ]; then
    dest=$dest/
fi

echo "src=$src, dest=$dest"

src_files=`find -type f -regex '.*\.sh\|.*\.py'`
for file in $src_files; do
	if [ ! -d "$file" ]; then
        target="$dest$file"
        echo "ln -s $src/$file $target"
        rm -rf $target
        ln -s $src/$file $target
    fi
done
