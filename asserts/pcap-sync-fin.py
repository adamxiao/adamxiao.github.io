from scapy.all import rdpcap, TCP

# 读取PCAP文件
packets = rdpcap("file.pcap")

# 存储每个连接的请求和回复时间
response_times = {}

packet_limit = 10000  # 限制处理的包数量
count = 0;


# 遍历数据包
for pkt in packets:
    if pkt.haslayer(TCP):
        src_ip = pkt["IP"].src
        dst_ip = pkt["IP"].dst
        src_port = pkt["TCP"].sport
        dst_port = pkt["TCP"].dport
        connection_id = (src_ip, src_port, dst_ip, dst_port)

        # 过滤源IP为127.0.0.1的包
        if src_ip == "127.0.0.1":
            continue

        #if count >= packet_limit:
        #    break  # 只处理前10000个包
        #count = count + 1


        # 检查是否为请求包（SYN）
        if pkt["TCP"].flags == "S":
            if connection_id not in response_times:
                response_times[connection_id] = {"request": pkt.time, "reply": None}

        # 检查是否为回复包（SYN-ACK或ACK）
        elif pkt["TCP"].flags == "FA":
            # reverse_id = (dst_ip, dst_port, src_ip, src_port)
            # if reverse_id in response_times and response_times[reverse_id]["reply"] is None:
            if connection_id in response_times and response_times[connection_id]["reply"] is None:
                response_times[connection_id]["reply"] = pkt.time

# 计算每个连接的请求-回复耗时
for conn, times in response_times.items():
    if times["request"] and times["reply"]:  # 确保有完整的请求和回复时间
        duration = times["reply"] - times["request"]
        print(f"Connection {conn} - Request-Reply Duration: {duration} seconds")
