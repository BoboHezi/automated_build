#!/usr/bin/env bash

src=`pwd`
dest=$1

if [ ! `echo $dest | grep "/$"` ]; then
    dest=$dest/
fi

echo "src=$src, dest=$dest"

excludes=("link.sh" "utils.py" "RepoParser.py")

src_files=`find -maxdepth 1 -type f -regex '.*\.sh\|.*\.py'`
for file in $src_files; do
    file=${file:2:${#file}}
    if [[ ${excludes[@]/${file}/} != ${excludes[@]} ]]; then
        continue
    fi
    if [ ! -d "$file" ]; then
        target="$dest$file"
        echo "ln -s $src/$file $target"
        rm -rf $target
        ln -s $src/$file $target
    fi
done
