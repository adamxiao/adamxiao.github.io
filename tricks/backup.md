# adam备份技巧

备份目录有:
* workspaces
* Downloads
* Documents
* ...

```bash
data_dir=/media/adam/nas_data

for dir in Documents Downloads Pictures Music Videos workspaces
do
    if [[ -h $HOME/$dir ]]; then
        echo "link dir $HOME/$dir exist!"
        continue
    fi

    if [[ -d  $HOME/$dir ]]; then
        rmdir $HOME/$dir 2>/dev/null || echo "can't remove dir: $HOME/$dir"
    fi

    if [[ ! -e $HOME/$dir ]]; then
        ln -sf $data_dir/$dir $HOME && echo "link dir $HOME/$dir success!"
    fi
done

#rmdir $HOME/Documents && ln -sf $data_dir/Documents $HOME && echo "Documents link created!"
```
