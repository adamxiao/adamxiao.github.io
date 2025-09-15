# auditctl使用

## 监控文件删除

监控文件wa操作
```
auditctl -w /xxx/xxx -p aw -k adam_delete
```

## 监控信号

linux如何监控进程收到的TERM信号，以及USR2信号

```
sudo auditctl -a always,exit -S kill -S tkill -S tgkill -F arch=b64 -F "a1=15" -F "a1=12"  # 监控 TERM(15) 和 USR2(12)
     auditctl -a always,exit -F arch=b64 -S kill -S tkill -S tgkill -F a1=15 -F a1=12 # => ok
     auditctl -a always,exit -F arch=b64 -S kill -S tkill -S tgkill -S rt_sigqueueinfo -S rt_tgsigqueueinfo -F a1=15 -F a1=12
     auditctl -a always,exit -F arch=b64 -S kill -S tkill -S tgkill -S rt_sigqueueinfo -S rt_tgsigqueueinfo -F a1=15 -k adamkill;
     auditctl -a always,exit -F arch=b64 -S kill -S tkill -S tgkill -S rt_sigqueueinfo -S rt_tgsigqueueinfo -F a1=12 -k adamkill2
```

查看审计日志
```
sudo ausearch -sc kill -i | grep -E "pid=12345|sig=15|sig=12"
```

## ioctl系统调用

https://docs.redhat.com/zh-cn/documentation/red_hat_enterprise_linux/8/html/security_hardening/understanding-audit-log-files_auditing-the-system#understanding-audit-log-files_auditing-the-system
a0=7fffd19c5592, a1=0, a2=7fffd19c5592, a3=a
a0至a3字段记录了该事件中系统调用的前四个参数，用十六进制符号编码。这些参数取决于使用的系统调用，可以通过 ausearch 工具来解释它们。

ioctl的系统调用，这4个参数表示什么

- 文件描述符 (int)
- 请求代码 (int)
- 参数，通常是用户空间的指针 (void *)
- 如果第四个参数被使用，它通常也会是一个指针或一个附加的整数值。

```
ioctl(4, RTC_SET_TIME, {tm_sec=16, tm_min=42, tm_hour=8, tm_mday=4, tm_mon=0, tm_year=125, ...}) = 0
#define RTC_SET_TIME    _IOW('p', 0x0a, struct rtc_time)
```

审计所有的ioctl系统调用，来获取参数!
```
sudo auditctl -a always,exit -S ioctl -k all_ioctl
```

审计到a1=4024700a => 最后真的审计到了! => 结果发现不是通过这种方法修改的!
```
auditctl -a always,exit -F arch=b64 -S ioctl -F a1=0x4024700a -k rtc_set_time
```

gpt《修改硬件时间，就是通过写入 /dev/rtc 吧? 》
内核提供了一系列系统调用来访问和修改 RTC，如 ioctl()、clock_settime() 和 clock_gettime()。这些调用由像 hwclock 这样的工具在后台使用，而不是通过直接写入 /dev/rtc 来进行。

```
auditctl -a always,exit -F arch=b64 -S clock_settime -k clock_settime
```

还有/sys 接口?
/sys/class/rtc/rtc0

## 旧的资料

```
auditctl -s //查询状态
auditctl -l //查看规则
auditctl -D //删除所有规则
```

#### 监控配置文件修改

安装: `apt-get install auditd`

* auditd 是后台守护进程，负责监控记录
* auditctl 配置规则的工具
* auditsearch 搜索查看
* aureport 根据监控记录生成报表

比如，监控 /root/.ssh/authorized_keys 文件是否被修改过：
```
auditctl -w /root/.ssh/authorized_keys -p war -k auth_key
auditctl -w /etc/multipath.conf -p aw -k mutlipth_conf
```

* -w 指明要监控的文件
* -p awrx 要监控的操作类型，append, write, read, execute
* -k 给当前这条监控规则起个名字，方便搜索过滤
查看修改纪录：`ausearch -i -k auth_key`，生成报表 aureport.
```
ausearch -i -k mutlipth_conf
```

#### 监控系统调用bind

关键字《linux系统审计tcp端口绑定》《linux系统审计bind》

https://docs.redhat.com/zh_hans/documentation/red_hat_enterprise_linux/7/html/security_guide/chap-system_auditing#chap-system_auditing
审计系统调用bind

关键字《auditctl审计系统调用bind》

gpt关键字《linux配置审计系统调用bind》
```
auditctl -a always,exit -F arch=b64 -S bind
ausearch -sc bind | grep 0200BDE8
ausearch -i -ts 09/07/2024 07:50:00" -te "09/07/2024 08:00:00"
ausearch -i -ts 2024年09月07日 07:50:00 -te 2024年09月07日 08:00:00
=> date '+%x' # https://man7.org/linux/man-pages/man8/ausearch.8.html
                                                                                                                                                                                                           审计进程的退出
auditctl -a always,exit -F arch=b64 -S exit -S exit_group                                                                                                                                                  ausearch -sc exit                                                                                                                                                                                          ausearch -sc exit_group

指定进程
auditctl -a always,exit -F path=/usr/lib/ksvd/bin/ksvdcmd -F perm=x -k ksvdcmd_audit                                                                                                                       auditctl -a always,exit -F arch=b64 -S exit -S exit_group -F exe=/usr/lib/ksvd/bin/ksvdcmd -k ksvdcmd_exit
ausearch -k ksvdcmd_exit
```

/etc/audit/rules.d/audit.rules
=> 配置这个文件，固话审计规则                                                                                                                                                                              ```
-a always,exit -F arch=b64 -S bind
-a always,exit -F arch=b64 -S exit -S exit_group -F exe=/usr/lib/ksvd/bin/ksvdcmd -k ksvdcmd_exit
```

```
auditctl -a always,exit -F arch=b64 -S bind;
echo "-a always,exit -F arch=b64 -S bind" > /etc/audit/rules.d/audit.rules

auditctl -a always,exit -F arch=b64 -S bind -F 'a1&=0xBDE800000000' -k bind-port-48616
ausearch -k bind-port-48616
=> 验证失败, 一本正经的胡说八道
```

/etc/audit/auditd.conf
修改日志保留大小时间!
```
max_log_file = 200
num_logs = 500
```
生效
```
sed -i -c -e 's/^max_log_file =.*/max_log_file = 200/' -e 's/^num_logs =.*/num_logs = 500/' /etc/audit/auditd.conf;
kill -HUP $(pidof auditd)
```

gpt《bind 10.90.6.134:48616 failed: bind: Address already in use》
直接使用命令杀死这个进程!
```
sudo fuser -k 48616/tcp
```

发现可能是本地tcp客户端随机端口占用了!
```
net.ipv4.ip_local_port_range = 32768 60999
net.ipv4.ip_local_reserved_ports = 48616
sysctl -w net.ipv4.ip_local_reserved_ports=48616
```

入口gpt《内核处理bind系统调用的代码》
net/ipv4/inet_connection_sock.c : inet_csk_get_port
=> 分配端口的入口函数?
net/ipv4/inet_connection_sock.c : inet_csk_bind_conflict
=> 检查绑定是否冲突
inet_bind_conflict
=> 最终发现是这里的检查逻辑

xcap：基于 eBPF 技术的下一代内核网络抓包工具 | 第二届eBPF开发者大会分享回顾


```
#!/usr/bin/python
from bcc import BPF
import time

# 定义 eBPF 程序
bpf_program = """
#include <uapi/linux/ptrace.h>
BPF_HASH(start_time, u32, u64);

int trace_exit_entry(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid();
    u64 ts = bpf_ktime_get_ns();
    start_time.update(&pid, &ts);
    return 0;
}

int trace_exit_return(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid();
    u64 *tsp, delta;
    u64 ts = bpf_ktime_get_ns();

    // 获取开始时间
    tsp = start_time.lookup(&pid);
    if (tsp != 0) {
        delta = ts - *tsp;
        // 打印耗时信息
        bpf_trace_printk("PID: %d, exit syscall took %llu ns\\n", pid, delta);
        start_time.delete(&pid);
    }
    return 0;
}
"""

# 初始化 BPF
b = BPF(text=bpf_program)

# 追踪 sys_exit 的入口和返回
b.attach_kprobe(event="sys_exit", fn_name="trace_exit_entry")
b.attach_kretprobe(event="sys_exit", fn_name="trace_exit_return")

print("Tracing sys_exit... Ctrl+C to stop.")

# 打印追踪结果
while True:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        print(f"{ts} {msg}")
    except KeyboardInterrupt:
        exit()
```

