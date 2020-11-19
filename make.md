# make manual

查看依赖目标等细节
make -p

```
PROTO_SRCS = $(wildcard *.proto)
CPP_SRCS = $(subst .proto,.pb.cc,$(PROTO_SRCS))

%.pb.cc: %.proto
  protoc --cpp_out=. $<
```
