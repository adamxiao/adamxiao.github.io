# fio测试磁盘IO性能

关键字《fio测试》
https://www.huaweicloud.com/articles/2a6a62f7bdebb2c88424ae5f8a5efb01.html

## 安装

```
#yum安装
yum install libaio-devel fio
#手动安装
yum install libaio-devel
wget http://brick.kernel.dk/snaps/fio-2.2.10.tar.gz
tar -zxvf fio-2.2.10.tar.gz
cd fio-2.2.10
make && make install
```

docker镜像
```dockerfile
# FIO benchmark on Ubuntu

FROM ubuntu:20.04
MAINTAINER Chris Mutchler <chris@virtualelephant.com>

RUN apt-get update
RUN apt-get -y install fio wget
RUN wget http://virtualelephant.com/wp-content/uploads/2015/10/threads.txt

CMD [ "/bin/bash" ]
```

## fio测试性能

参考: https://m.linuxidc.com/Linux/2017-04/143251.htm

1. 测试顺序读
fio --filename=/tmp/tmpdir/test -iodepth=64 -ioengine=libaio --direct=1 --rw=read --bs=1m --size=2g --numjobs=4 --runtime=10 --group_reporting --name=test-read
2. 测试顺序写
fio --filename=/tmp/tmpdir/test -iodepth=64 -ioengine=libaio --direct=1 --rw=write --bs=1m --size=2g --numjobs=4 --runtime=20 --group_reporting --name=test-write
3. 测试随机读
fio --filename=/tmp/tmpdir/test -iodepth=64 -ioengine=libaio --direct=1 --rw=randread --bs=4k --size=2g --numjobs=64 --runtime=20 --group_reporting --name=test-rand-read
4. 测试随机写
fio --filename=/tmp/tmpdir/test -iodepth=64 -ioengine=libaio --direct=1 --rw=randwrite --bs=4k --size=2G --numjobs=64 --runtime=20 --group_reporting --name=test-rand-write


fio测试磁盘性能
https://m.linuxidc.com/Linux/2017-04/143251.htm


## 测试配置

fio.conf
```
[global]
ioengine=libaio
direct=1
thread=1
norandommap=1
randrepeat=0
runtime=60
ramp_time=6
size=1g
directory=/root/fio-test

[read4k-rand]
stonewall
group_reporting
bs=4k
rw=randread
numjobs=8
iodepth=32

[read64k-seq]
stonewall
group_reporting
bs=64k
rw=read
numjobs=4
iodepth=8

[write4k-rand]
stonewall
group_reporting
bs=4k
rw=randwrite
numjobs=2
iodepth=4

[write64k-seq]
stonewall
group_reporting
bs=64k
rw=write
numjobs=2
iodepth=4
```


#### 1.50物理pc测试结果

```
read4k-rand: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=32
...
read64k-seq: (g=1): rw=read, bs=(R) 64.0KiB-64.0KiB, (W) 64.0KiB-64.0KiB, (T) 64.0KiB-64.0KiB, ioengine=libaio, iodepth=8
...
write4k-rand: (g=2): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=4
...
write64k-seq: (g=3): rw=write, bs=(R) 64.0KiB-64.0KiB, (W) 64.0KiB-64.0KiB, (T) 64.0KiB-64.0KiB, ioengine=libaio, iodepth=4
...
fio-3.1
Starting 16 threads
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
write4k-rand: Laying out IO file (1 file / 1024MiB)
write4k-rand: Laying out IO file (1 file / 1024MiB)
write64k-seq: Laying out IO file (1 file / 1024MiB)
write64k-seq: Laying out IO file (1 file / 1024MiB)
read64k-seq: No I/O performed by libaio, perhaps try --debug=io option for details?m:12s]
read64k-seq: No I/O performed by libaio, perhaps try --debug=io option for details?OPS][eta 03m:29s]
read64k-seq: No I/O performed by libaio, perhaps try --debug=io option for details?ta 03m:28s]
read64k-seq: No I/O performed by libaio, perhaps try --debug=io option for details?ta 03m:18s]
write64k-seq: No I/O performed by libaio, perhaps try --debug=io option for details?s]
write64k-seq: No I/O performed by libaio, perhaps try --debug=io option for details?0m:09s]

read4k-rand: (groupid=0, jobs=8): err= 0: pid=23979: Fri Sep 10 12:52:26 2021
   read: IOPS=162, BW=666KiB/s (682kB/s)(39.9MiB/61404msec)
    slat (nsec): min=1980, max=2721.6M, avg=35131199.46, stdev=199207367.03
    clat (msec): min=43, max=5937, avg=1533.32, stdev=617.83
     lat (msec): min=43, max=5937, avg=1568.37, stdev=647.79
    clat percentiles (msec):
     |  1.00th=[  489],  5.00th=[  835], 10.00th=[  919], 20.00th=[ 1053],
     | 30.00th=[ 1167], 40.00th=[ 1301], 50.00th=[ 1435], 60.00th=[ 1552],
     | 70.00th=[ 1687], 80.00th=[ 1871], 90.00th=[ 2265], 95.00th=[ 2735],
     | 99.00th=[ 3742], 99.50th=[ 4144], 99.90th=[ 4597], 99.95th=[ 4597],
     | 99.99th=[ 5000]
   bw (  KiB/s): min=    5, max=  386, per=17.62%, avg=117.37, stdev=94.11, samples=551
   iops        : min=    1, max=   96, avg=28.92, stdev=23.57, samples=551
  lat (msec)   : 50=0.02%, 100=0.17%, 250=0.44%, 500=0.41%, 750=1.58%
  lat (msec)   : 1000=15.33%, 2000=68.70%, >=2000=15.82%
  cpu          : usr=0.00%, sys=0.01%, ctx=939, majf=0, minf=0
  IO depths    : 1=0.1%, 2=0.2%, 4=0.3%, 8=0.6%, 16=1.3%, 32=111.7%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=99.9%, 8=0.0%, 16=0.0%, 32=0.1%, 64=0.0%, >=64=0.0%
     issued rwt: total=9972,0,0, short=0,0,0, dropped=0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=32
read64k-seq: (groupid=1, jobs=4): err= 0: pid=25397: Fri Sep 10 12:52:26 2021
   read: IOPS=1396, BW=87.3MiB/s (91.6MB/s)(3691MiB/42254msec)
    slat (usec): min=3, max=138, avg=16.20, stdev= 7.50
    clat (usec): min=196, max=3159.1k, avg=18627.45, stdev=161040.12
     lat (usec): min=214, max=3159.1k, avg=18643.86, stdev=161039.63
    clat percentiles (msec):
     |  1.00th=[    4],  5.00th=[    4], 10.00th=[    4], 20.00th=[    4],
     | 30.00th=[    4], 40.00th=[    4], 50.00th=[    4], 60.00th=[    5],
     | 70.00th=[    6], 80.00th=[    6], 90.00th=[    6], 95.00th=[   11],
     | 99.00th=[  148], 99.50th=[  575], 99.90th=[ 3037], 99.95th=[ 3104],
     | 99.99th=[ 3171]
   bw (  KiB/s): min=  259, max=114022, per=43.01%, avg=38470.95, stdev=41488.11, samples=163
   iops        : min=    4, max= 1781, avg=600.62, stdev=648.25, samples=163
  lat (usec)   : 250=0.01%, 500=0.01%, 750=0.01%, 1000=0.01%
  lat (msec)   : 2=0.05%, 4=54.26%, 10=40.70%, 20=0.27%, 50=1.23%
  lat (msec)   : 100=1.84%, 250=0.91%, 500=0.18%, 750=0.14%, 1000=0.07%
  lat (msec)   : 2000=0.11%, >=2000=0.27%
  cpu          : usr=0.14%, sys=0.91%, ctx=56409, majf=0, minf=0
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=111.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.1%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwt: total=59024,0,0, short=0,0,0, dropped=0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=8
write4k-rand: (groupid=2, jobs=2): err= 0: pid=26571: Fri Sep 10 12:52:26 2021
  write: IOPS=151, BW=607KiB/s (622kB/s)(36.1MiB/60866msec)
    slat (usec): min=2, max=1298, avg=20.30, stdev=19.47
    clat (usec): min=266, max=2509.5k, avg=52641.29, stdev=123341.80
     lat (usec): min=286, max=2509.5k, avg=52661.82, stdev=123341.04
    clat percentiles (usec):
     |  1.00th=[    734],  5.00th=[   1663], 10.00th=[   2638],
     | 20.00th=[   5342], 30.00th=[  12780], 40.00th=[  29230],
     | 50.00th=[  32113], 60.00th=[  39584], 70.00th=[  42730],
     | 80.00th=[  52167], 90.00th=[  82314], 95.00th=[ 177210],
     | 99.00th=[ 658506], 99.50th=[ 742392], 99.90th=[1803551],
     | 99.95th=[2499806], 99.99th=[2499806]
   bw (  KiB/s): min=   22, max=  857, per=44.98%, avg=273.02, stdev=167.81, samples=218
   iops        : min=    5, max=  214, avg=67.86, stdev=41.94, samples=218
  lat (usec)   : 500=0.17%, 750=0.91%, 1000=1.02%
  lat (msec)   : 2=4.66%, 4=9.65%, 10=11.24%, 20=3.61%, 50=45.64%
  lat (msec)   : 100=14.15%, 250=6.36%, 500=1.39%, 750=0.81%, 1000=0.29%
  lat (msec)   : 2000=0.09%, >=2000=0.09%
  cpu          : usr=0.05%, sys=0.18%, ctx=8907, majf=0, minf=0
  IO depths    : 1=0.1%, 2=0.1%, 4=112.3%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwt: total=0,9234,0, short=0,0,0, dropped=0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=4
write64k-seq: (groupid=3, jobs=2): err= 0: pid=28094: Fri Sep 10 12:52:26 2021
  write: IOPS=846, BW=52.9MiB/s (55.5MB/s)(1628MiB/30759msec)
    slat (nsec): min=4835, max=88352, avg=20079.18, stdev=8583.29
    clat (usec): min=206, max=1789.2k, avg=9306.76, stdev=41138.00
     lat (usec): min=223, max=1789.2k, avg=9327.03, stdev=41137.30
    clat percentiles (usec):
     |  1.00th=[    685],  5.00th=[    865], 10.00th=[    955],
     | 20.00th=[   1188], 30.00th=[   1778], 40.00th=[   1876],
     | 50.00th=[   1942], 60.00th=[   2008], 70.00th=[   2114],
     | 80.00th=[   3752], 90.00th=[  19530], 95.00th=[  56886],
     | 99.00th=[ 137364], 99.50th=[ 160433], 99.90th=[ 278922],
     | 99.95th=[ 591397], 99.99th=[1786774]
   bw (  KiB/s): min=  507, max=84332, per=51.65%, avg=27997.48, stdev=17100.51, samples=114
   iops        : min=    7, max= 1317, avg=437.03, stdev=267.25, samples=114
  lat (usec)   : 250=0.01%, 500=0.10%, 750=1.69%, 1000=10.72%
  lat (msec)   : 2=46.77%, 4=27.73%, 10=2.75%, 20=0.28%, 50=4.17%
  lat (msec)   : 100=4.24%, 250=1.44%, 500=0.06%, 750=0.05%, 2000=0.03%
  cpu          : usr=0.28%, sys=0.87%, ctx=24118, majf=0, minf=0
  IO depths    : 1=0.1%, 2=0.1%, 4=125.8%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwt: total=0,26045,0, short=0,0,0, dropped=0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=4

Run status group 0 (all jobs):
   READ: bw=666KiB/s (682kB/s), 666KiB/s-666KiB/s (682kB/s-682kB/s), io=39.9MiB (41.9MB), run=61404-61404msec

Run status group 1 (all jobs):
   READ: bw=87.3MiB/s (91.6MB/s), 87.3MiB/s-87.3MiB/s (91.6MB/s-91.6MB/s), io=3691MiB (3870MB), run=42254-42254msec

Run status group 2 (all jobs):
  WRITE: bw=607KiB/s (622kB/s), 607KiB/s-607KiB/s (622kB/s-622kB/s), io=36.1MiB (37.8MB), run=60866-60866msec

Run status group 3 (all jobs):
  WRITE: bw=52.9MiB/s (55.5MB/s), 52.9MiB/s-52.9MiB/s (55.5MB/s-55.5MB/s), io=1628MiB (1707MB), run=30759-30759msec

Disk stats (read/write):
    dm-0: ios=76936/44254, merge=0/0, ticks=10989583/1372574, in_queue=12362183, util=96.59%, aggrios=74615/49150, aggrmerge=2321/5295, aggrticks=10185297/4779306, aggrin_queue=14964557, aggrutil=96.71%
  sda: ios=74615/49150, merge=2321/5295, ticks=10185297/4779306, in_queue=14964557, util=96.71%
```


#### 2.11测试结果

```
read4k-rand: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=32
...
read64k-seq: (g=1): rw=read, bs=(R) 64.0KiB-64.0KiB, (W) 64.0KiB-64.0KiB, (T) 64.0KiB-64.0KiB, ioengine=libaio, iodepth=8
...
write4k-rand: (g=2): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=4
...
write64k-seq: (g=3): rw=write, bs=(R) 64.0KiB-64.0KiB, (W) 64.0KiB-64.0KiB, (T) 64.0KiB-64.0KiB, ioengine=libaio, iodepth=4
...
fio-3.7
Starting 16 threads
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read4k-rand: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
read64k-seq: Laying out IO file (1 file / 1024MiB)
write4k-rand: Laying out IO file (1 file / 1024MiB)
write4k-rand: Laying out IO file (1 file / 1024MiB)
write64k-seq: Laying out IO file (1 file / 1024MiB)
write64k-seq: Laying out IO file (1 file / 1024MiB)
Jobs: 2 (f=2): [_(14),W(2)][49.6%][r=0KiB/s,w=1344KiB/s][r=0,w=21 IOPS][eta 04m:32s]                   
read4k-rand: (groupid=0, jobs=8): err= 0: pid=11492: Fri Sep 10 05:55:23 2021
   read: IOPS=134, BW=555KiB/s (568kB/s)(33.6MiB/62088msec)
    slat (usec): min=6, max=1344.9k, avg=914.67, stdev=25842.04
    clat (msec): min=565, max=4332, avg=1866.10, stdev=538.11
     lat (msec): min=565, max=4332, avg=1866.99, stdev=537.97
    clat percentiles (msec):
     |  1.00th=[  776],  5.00th=[ 1045], 10.00th=[ 1200], 20.00th=[ 1435],
     | 30.00th=[ 1569], 40.00th=[ 1687], 50.00th=[ 1804], 60.00th=[ 1938],
     | 70.00th=[ 2123], 80.00th=[ 2333], 90.00th=[ 2601], 95.00th=[ 2769],
     | 99.00th=[ 3205], 99.50th=[ 3473], 99.90th=[ 4212], 99.95th=[ 4329],
     | 99.99th=[ 4329]
   bw (  KiB/s): min=    5, max=  256, per=19.20%, avg=106.37, stdev=70.25, samples=513
   iops        : min=    1, max=   64, avg=26.21, stdev=17.58, samples=513
  lat (msec)   : 750=0.77%, 1000=3.38%
  cpu          : usr=0.01%, sys=0.04%, ctx=8308, majf=0, minf=1
  IO depths    : 1=0.1%, 2=0.2%, 4=0.4%, 8=0.8%, 16=1.5%, 32=113.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=99.9%, 8=0.0%, 16=0.0%, 32=0.1%, 64=0.0%, >=64=0.0%
     issued rwts: total=8364,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=32
read64k-seq: (groupid=1, jobs=4): err= 0: pid=11500: Fri Sep 10 05:55:23 2021
   read: IOPS=211, BW=13.3MiB/s (13.9MB/s)(797MiB/60043msec)
    slat (usec): min=9, max=205, avg=21.81, stdev=11.78
    clat (msec): min=3, max=1466, avg=151.05, stdev=120.32
     lat (msec): min=3, max=1466, avg=151.07, stdev=120.32
    clat percentiles (msec):
     |  1.00th=[   23],  5.00th=[   42], 10.00th=[   53], 20.00th=[   70],
     | 30.00th=[   85], 40.00th=[  102], 50.00th=[  121], 60.00th=[  142],
     | 70.00th=[  176], 80.00th=[  220], 90.00th=[  275], 95.00th=[  342],
     | 99.00th=[  550], 99.50th=[  818], 99.90th=[ 1200], 99.95th=[ 1334],
     | 99.99th=[ 1435]
   bw (  KiB/s): min=  121, max= 6884, per=23.36%, avg=3173.64, stdev=1413.57, samples=474
   iops        : min=    1, max=  107, avg=49.19, stdev=22.11, samples=474
  lat (msec)   : 4=0.01%, 10=0.03%, 20=0.57%, 50=7.78%, 100=31.12%
  lat (msec)   : 250=46.77%, 500=12.60%, 750=0.82%, 1000=0.07%
  cpu          : usr=0.05%, sys=0.18%, ctx=9703, majf=0, minf=0
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=108.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.1%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=12718,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=8
write4k-rand: (groupid=2, jobs=2): err= 0: pid=11504: Fri Sep 10 05:55:23 2021
  write: IOPS=227, BW=910KiB/s (931kB/s)(53.4MiB/60161msec)
    slat (usec): min=7, max=300, avg=24.12, stdev=14.99
    clat (usec): min=113, max=881530, avg=35165.22, stdev=65586.40
     lat (usec): min=130, max=881557, avg=35191.30, stdev=65587.31
    clat percentiles (usec):
     |  1.00th=[   210],  5.00th=[   963], 10.00th=[  1795], 20.00th=[  2835],
     | 30.00th=[  4490], 40.00th=[  6194], 50.00th=[  7635], 60.00th=[  9110],
     | 70.00th=[ 17171], 80.00th=[ 64750], 90.00th=[106431], 95.00th=[154141],
     | 99.00th=[274727], 99.50th=[396362], 99.90th=[792724], 99.95th=[868221],
     | 99.99th=[876610]
   bw (  KiB/s): min=    8, max= 1804, per=44.31%, avg=402.79, stdev=313.07, samples=236
   iops        : min=    2, max=  451, avg=100.53, stdev=78.25, samples=236
  lat (usec)   : 250=1.44%, 500=0.98%, 750=1.18%, 1000=1.59%
  lat (msec)   : 2=6.60%, 4=15.77%, 10=36.08%, 20=6.79%, 50=6.17%
  lat (msec)   : 100=12.35%, 250=9.66%, 500=1.26%, 750=0.08%, 1000=0.10%
  cpu          : usr=0.19%, sys=0.55%, ctx=12255, majf=0, minf=0
  IO depths    : 1=0.1%, 2=0.1%, 4=104.7%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=0,13675,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=4
write64k-seq: (groupid=3, jobs=2): err= 0: pid=11508: Fri Sep 10 05:55:23 2021
  write: IOPS=99, BW=6366KiB/s (6519kB/s)(375MiB/60346msec)
    slat (usec): min=12, max=169, avg=38.77, stdev=19.60
    clat (usec): min=171, max=2079.0k, avg=80739.82, stdev=142072.44
     lat (usec): min=197, max=2080.0k, avg=80780.86, stdev=142072.12
    clat percentiles (usec):
     |  1.00th=[    734],  5.00th=[   2278], 10.00th=[   3163],
     | 20.00th=[   6390], 30.00th=[   7898], 40.00th=[  13566],
     | 50.00th=[  20317], 60.00th=[  41681], 70.00th=[  76022],
     | 80.00th=[ 130548], 90.00th=[ 227541], 95.00th=[ 333448],
     | 99.00th=[ 633340], 99.50th=[ 801113], 99.90th=[1468007],
     | 99.95th=[1602225], 99.99th=[2071987]
   bw (  KiB/s): min=  128, max=18906, per=51.07%, avg=3250.97, stdev=3373.87, samples=236
   iops        : min=    2, max=  295, avg=50.74, stdev=52.72, samples=236
  lat (usec)   : 250=0.08%, 500=0.20%, 750=0.75%, 1000=0.73%
  lat (msec)   : 2=1.92%, 4=9.40%, 10=23.08%, 20=13.06%, 50=12.39%
  lat (msec)   : 100=13.92%, 250=16.02%, 500=6.82%, 750=1.08%, 1000=0.33%
  cpu          : usr=0.15%, sys=0.32%, ctx=5447, majf=0, minf=0
  IO depths    : 1=0.1%, 2=0.1%, 4=127.2%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=0,5997,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=4

Run status group 0 (all jobs):
   READ: bw=555KiB/s (568kB/s), 555KiB/s-555KiB/s (568kB/s-568kB/s), io=33.6MiB (35.3MB), run=62088-62088msec

Run status group 1 (all jobs):
   READ: bw=13.3MiB/s (13.9MB/s), 13.3MiB/s-13.3MiB/s (13.9MB/s-13.9MB/s), io=797MiB (835MB), run=60043-60043msec

Run status group 2 (all jobs):
  WRITE: bw=910KiB/s (931kB/s), 910KiB/s-910KiB/s (931kB/s-931kB/s), io=53.4MiB (56.0MB), run=60161-60161msec

Run status group 3 (all jobs):
  WRITE: bw=6366KiB/s (6519kB/s), 6366KiB/s-6366KiB/s (6519kB/s-6519kB/s), io=375MiB (393MB), run=60346-60346msec

Disk stats (read/write):
  vda: ios=23456/22025, merge=1/142, ticks=19416922/1137063, in_queue=10276494, util=83.19%
```
