import os
import collections
import json
import sys
import urllib
import urllib.request
import random
import signal

URL_PREFIX = "https://raw.githubusercontent.com/taugin/flashres/master/themeres/"

USER_CANCELED = False

def log(msg):
    print("[Logging...] %s" % msg)

def sigint_handler(signum, frame):
  global USER_CANCELED
  USER_CANCELED = True

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)

def get_dynamic_list(process_dir):
    log("生成资源列表")
    resdir = process_dir
    filelist = os.listdir(resdir)
    random.shuffle(filelist)
    res = []
    max_len = 0
    for file in filelist:
        if file.endswith("gif") or file.endswith("mp4"):
            base, ext = os.path.splitext(file)
            resitem = collections.OrderedDict()
            base = base.replace("_", " ")
            resitem["name"] = base.capitalize()
            name_len = len(resitem["name"])
            if name_len > max_len:
                max_len = name_len
            if ext == ".gif":
                resitem["type"] = "gif"
            else:
                resitem["type"] = "video"
            resitem["link_count"] = random.randint(100000, 999999)
            resitem["cover_url"] = URL_PREFIX + base + "_preview.png"
            resitem["theme_url"] = URL_PREFIX + file
            resitem["acceptUrl"] = ""
            resitem["rejectUrl"] = ""
            res.append(resitem)
    return res, max_len

def is_url_exist(url):
    try:
        response = urllib.request.urlopen(url,timeout=5)
        response.close()
        return True
    except Exception as e:
        pass
    return False

def checkUrl(res_list, max_len):
    log("检查资源列表")
    global USER_CANCELED
    new_res_list = []
    err_res_list = []
    cover_url_exist = True
    theme_url_exist = True
    for res_item in res_list:
        if USER_CANCELED == True:
            log("用户取消操作")
            break;
        if res_item != None and "cover_url" in res_item and "theme_url" in res_item:
            name = None
            restype = None
            cover_url = res_item["cover_url"]
            theme_url = res_item["theme_url"]
            if "name" in res_item:
                name = res_item["name"]
            if "type" in res_item:
                restype = res_item["type"]
            log("正在处理资源 : %-*s [%-5s]" % (int(max_len), name , restype))
            cover_url_exist = is_url_exist(cover_url)
            theme_url_exist = is_url_exist(theme_url)
            status = "资源不存在"
            if theme_url_exist == True and cover_url_exist == True:
                status = "资源存在"
                new_res_list.append(res_item)
            else:
                status = "资源不存在"
                err_res_list.append(res_item)
            log("资源处理结果 : %-*s [%-5s] -> [%-6s] - [%s]" % (int(max_len), name, restype, status, theme_url))
    return new_res_list, err_res_list

def sort_res_list(res_list, sort_way):
    sort_string = "降序"
    if (sort_way == "asc"):
        sort_string = "升序"
    elif (sort_way == "desc"):
        sort_string = "降序"
    elif (sort_way == "random"):
        sort_string = "随机"

    log("资源列表排序 : [%s]" % sort_string)
    if (sort_way == "asc"):
        res_list.sort(key=lambda x:x["name"], reverse=False)
    elif (sort_way == "desc"):
        res_list.sort(key=lambda x:x["name"], reverse=True)
    elif (sort_way == "random"):
        random.shuffle(res_list)
    return res_list;

def writeToFile(res_list, file_name):
    log("写入资源列表")
    output = json.dumps(res_list, sort_keys=False, indent=4)
    f = open(file_name, "w")
    f.write(output)
    f.close()

if __name__ == "__main__":
    process_dir = None
    sort_way = "desc"
    if len(sys.argv) > 2:
        process_dir = sys.argv[1]
        sort_way = sys.argv[2]
    elif len(sys.argv) > 1:
        process_dir = sys.argv[1]
    else:
        log("Usage : %s resfolder [asc/desc/random]" % os.path.basename(sys.argv[0]))
        sys.exit(0)
    res_list, max_len = get_dynamic_list(process_dir)
    res_list, err_list = checkUrl(res_list, max_len)
    res_list = sort_res_list(res_list, sort_way)
    writeToFile(res_list, "config_list.json")
    writeToFile(err_list, "error_list.json")
