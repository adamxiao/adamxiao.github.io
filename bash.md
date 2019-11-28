# bash strick

if ssh pty, echo ip
```
ssh_ip=`env | awk '/^SSH_CONNECTION=/ {print $3}'` 
if [[ "" != "$ssh_ip" ]];then 
        export PS1="\[\e[31m\][ssh_"$ssh_ip"]\[\e[0m\] \u@\h: \W\$" 
fi
```
