# docker镜像使用总结

将一些镜像方法记录下来

[Authenticate Docker to Harbor Image Registry with a Robot Account](https://veducate.co.uk/authenticate-docker-harbor-robot/)

```bash
username=$(cat file.json | jq -r .name)
password=$(cat file.json | jq -r .token) <<< See below update
echo "$password" | docker login https://URL --username "$username" --password-stdin

Example
username=$(cat "robot\$veducate.json" | jq -r .name)
password=$(cat robot\$veducate.json | jq -r .token)
echo "$password" | docker login https://harbor-repo.veducate.com --username "$username" --password-stdin

Update October 2021
Since Harbor 2.2 minor release, and I found that within the JSON the key name has changed to secret, so this is the updated example

username=$(cat robot-veducate.json | jq -r .name)
password=$(cat robot-veducate.json | jq -r .secret)
echo "$password" | docker login https://harbor-repo.veducate.com --username "$username" --password-stdin
```
