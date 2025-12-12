# valgrind 使用记录

让一个daemon进程，不fork，然后使用valgrind分析内存问题
```
valgrind --leak-check=full --show-leak-kinds=all --log-file=valgrind_report.txt --track-origins=yes /usr/lib/ksvd/bin/uniqbvded -nodaemonize

valgrind --tool=memcheck --leak-check=full --show-leak-kinds=all --log-file=valgrind_report.txt --track-origins=yes /usr/lib/ksvd/bin/uniqbvded -nodaemonize
```
