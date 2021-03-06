#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import traceback

import psutil

from script.utils.SignatureMapping import SignatureMapping
from script.utils.utils import *
from script.modules.worker import fetch_url


def kill_child_processes(parent_pid):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        print '[ERROR][loader] No such process with PID ' + str(parent_pid)
        return
    for child in parent.children(recursive=True):
        try:
            child.kill()
        except psutil.NoSuchProcess:
            print '[ERROR][loader] No such process with PID ' + str(child.pid)
            continue
    parent.kill()


def url_reader(path_to_urllist):
    f = open(path_to_urllist, 'r')
    lst = f.readline()
    return lst.strip()


def url_loader(url, is_with_ext):
    is_warming = False if url else True
    opt_w_ab = OPT_W_AB
    opt_wo_ab = OPT_WO_AB
    if VERIFY_RUN:
        opt_w_ab = opt_wo_ab
    if BEHIND_PROXY:
        opt_w_ab += ADDI_OPT_PROXY
        opt_wo_ab += ADDI_OPT_PROXY
    if is_warming:
        print "[INFO][looper] Warming up Chromium..."
        if is_with_ext:
            args = opt_w_ab
        else:
            args = opt_wo_ab
    else:
        print "[INFO][looper] Visiting " + url
        if is_with_ext:
            args = opt_w_ab + [url]
        else:
            args = opt_wo_ab + [url]
    return subprocess.Popen(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)


def log_extractor(path_to_log, flag_mode, url):
    def load(path_to_file):
        f = open(path_to_file, 'r')
        lst = f.readlines()
        f.close()
        return lst

    def unload(path_to_file, lst):
        f = open(path_to_file, 'w')
        f.writelines(lst)
        f.close()
        return

    '''
    def call_stack_builder(line):
        if CALL_STACK_WOFT:
            return call_stack_builder_woft(line)
        else:
            return call_stack_builder_wooft(line)
    
    def call_stack_builder_wooft(line):
        if len(line) == 1:
            return
        eles = line.split(" ")
        if len(eles) < 5:
            print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
            return
        elif eles[4] == "CALL":
            if eles[0] == '(1259,38)':
                print eles[7][:-1] + ' + ' + str(call_stack)
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            else:
                call_stack.append(eles[7][:-1])
            return True
        elif eles[4] == "RET":
            if eles[0] == '(1259,38)':
                print eles[7][:-1] + ' + ' + str(call_stack)
            if not call_stack:
                print '[ERROR][context] Empty call stack, curr line: ' + line[:-1]
                return True
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            if call_stack[-1] == eles[7][:-1]:
                call_stack.pop()
                return True
        return False

    def call_stack_builder_woft(line):
        if len(line) == 1:
            return
        eles = line.split(" ")
        if len(eles) < 5:
            print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
            return
        elif eles[4] == "CALL":
            if eles[0] == '(1259,38)':
                print eles[7][:-1] + ' + ' + str(call_stack)
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            else:
                call_stack.append(eles[7][:-1] + "_" + eles[8] + "_" + eles[9].strip())
            return True
        elif eles[4] == "RET":
            if eles[0] == '(1259,38)':
                print eles[7][:-1] + ' + ' + str(call_stack)
            if not call_stack:
                print '[ERROR][context] Empty call stack, curr line: ' + line[:-1]
                return True
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            elif call_stack[-1] == eles[7][:-1] + "_" + eles[8] + "_" + eles[9].strip():
                call_stack.pop()
                return True
        return False

    def call_stack_builder(line):
        if len(line) == 1:
            return
        eles = line.split(" ")
        if len(eles) < 5:
            print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
            return
        elif eles[4] == "CALL":
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            else:
                call_stack.append(eles[7][:-1] + "_" + eles[8] + "_" + eles[9].strip())
            return True
        elif eles[4] == "RET":
            if not call_stack:
                print '[ERROR][context] Empty call stack, curr line: ' + line[:-1]
                return True
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            elif call_stack[-1] == eles[7][:-1] + "_" + eles[8] + "_" + eles[9].strip():
                call_stack.pop()
                return True
        return False
    '''
    def call_stack_builder(line):
        if len(line) == 1:
            return
        eles = line.split(" ")
        if len(eles) < 5:
            print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
            return
        elif eles[4] == "CALL":
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            else:
                call_stack.append(eles[7][:-1] + "_" + eles[8] + "_" + eles[9].strip())
            return True
        elif eles[4] == "RET":
            if not call_stack:
                print '[ERROR][context] Empty call stack, curr line: ' + line[:-1]
                return True
            if len(eles) < 10:
                print '[ERROR][looper] Corrupted raw log: ' + line[:-1]
                return True
            elif call_stack[-1] == eles[7][:-1] + "_" + eles[8] + "_" + eles[9].strip():
                call_stack.pop()
                return True
        return False

    def transform_cs(call_entry):
        for i in range(len(call_entry)):
            while call_entry[i] == '_':
                return call_entry[0:i]

    def get_top_2_caller():
        if len(call_stack) > 2:
            if USE_CALL_STACK_WOFT:
                return call_stack[-2] + "_" + call_stack[-1]
            else:
                return transform_cs(call_stack[-2]) + "_" + transform_cs(call_stack[-1])
        elif len(call_stack) == 1:
            if USE_CALL_STACK_WOFT:
                return call_stack[0]
            else:
                return transform_cs(call_stack[0])
        else:
            return ""

    def get_top_1_caller():
        if len(call_stack) == 1:
            return call_stack[0]
        else:
            return ""

    def func_transform(line):
        if call_stack_builder(line):
            return None
        reg_match = re.match(log_pattern, line)
        if reg_match:
            reg_group = reg_match.groups()
            script_url, stmt_type, position = \
                reg_group[2], reg_group[3], 'x' + reg_group[0] + 'y' + reg_group[1] + 'o' + reg_group[4]
            if USE_CALL_STACK:
                return get_top_2_caller() + '_' + script_url + ' ' + stmt_type + ' ' + position + '\n'
            else:
                return '_' + script_url + ' ' + stmt_type + ' ' + position + '\n'
        else:
            return None

    def filter_by_kword(lst):
        return [func_transform(line) for line in lst if func_transform(line)]

    call_stack = []
    log = load(path_to_log)
    log_pattern = re.compile(PATTERN_LOG)
    filtered_log = filter_by_kword(log)

    if flag_mode == FLAG_W_AB:
        output_dir = (PATH_TO_FILTERED_LOG + url + '/w_adblocker/')
    else:
        output_dir = (PATH_TO_FILTERED_LOG + url + '/wo_adblocker/')
    output_path = output_dir + 'filtered_log_' + str(int(time.time() * 100)) + '.log'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    unload(output_path, filtered_log)
    return output_dir


def log_differ(path_to_dir, flag_mode, mapping):
    files = []
    grand_dict = {}
    run_count = 0
    log_pattern = re.compile(NEW_PATTERN_LOG)
    blklist = set()
    already_thened_dict = set()
    already_elsed_dict = set()
    for fname in os.listdir(path_to_dir):
        files.append(path_to_dir + fname)

    def regex_match(line):
        reg_match = re.match(log_pattern, line)
        if reg_match:
            reg_group = reg_match.groups()
            return reg_group
        else:
            return None

    for f in files:
        already_ifed_dict = {}
        run_count += 1
        log_file = open(f, 'r')
        lst = log_file.readlines()
        lst = [DUMMY_LOG_RECORD] + lst + [DUMMY_LOG_RECORD]
        for idx in range(1, len(lst) - 1):
            reg_group_prev, reg_group_curr, reg_group_next = \
                regex_match(lst[idx - 1]), regex_match(lst[idx]), regex_match(lst[idx + 1])
            if reg_group_curr is None or reg_group_next is None or reg_group_prev is None:
                continue

            if USE_SIG_MAPPING:
                trace_key_curr = mapping.map_to_compact(reg_group_curr[0] + ' ' + reg_group_curr[2])
                trace_key_next = mapping.map_to_compact(reg_group_next[0] + ' ' + reg_group_next[2])
                trace_key_prev = mapping.map_to_compact(reg_group_prev[0] + ' ' + reg_group_prev[2])
            else:
                trace_key_curr = reg_group_curr[0] + ' ' + reg_group_curr[2]
                trace_key_next = reg_group_next[0] + ' ' + reg_group_next[2]
                trace_key_prev = reg_group_prev[0] + ' ' + reg_group_prev[2]

            if reg_group_curr[1] == 'IF':
                if already_ifed_dict.get(trace_key_curr, -1) == -1:
                    already_ifed_dict[trace_key_curr] = 1
                else:
                    already_ifed_dict[trace_key_curr] += 1
                if trace_key_curr != trace_key_next \
                        or (trace_key_curr == trace_key_next and reg_group_next[1] == 'IF'):
                    if grand_dict.get(trace_key_curr, -1) == -1:
                        grand_dict[trace_key_curr] = [THIS_POS_ONLY_HAS_IF, {run_count}]
                    else:
                        if grand_dict[trace_key_curr][0] != THIS_POS_ONLY_HAS_IF:
                            grand_dict[trace_key_curr][0] = THIS_POS_ONLY_HAS_IF
                            grand_dict[trace_key_curr][1].add(run_count)
                            blklist.add(trace_key_curr)
                        else:
                            grand_dict[trace_key_curr][1].add(run_count)
                else:
                    continue
            elif reg_group_curr[1] == 'THEN':
                already_thened_dict.add(trace_key_curr)
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_IF_THEN, {run_count}]
                elif grand_dict[trace_key_curr][0] == THIS_POS_ONLY_HAS_IF and trace_key_curr != trace_key_prev \
                        and run_count in grand_dict[trace_key_curr][1] and trace_key_curr not in already_elsed_dict \
                        and already_ifed_dict[trace_key_curr] == 1:
                    grand_dict[trace_key_curr][0] = THIS_POS_HAS_IF_THEN
                    blklist.discard(trace_key_curr)
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_IF_THEN or trace_key_curr in already_elsed_dict:
                        blklist.add(trace_key_curr)
                        grand_dict[trace_key_curr][1].add(run_count)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)
            elif reg_group_curr[1] == 'ELSE':
                already_elsed_dict.add(trace_key_curr)
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_IF_ELSE, {run_count}]
                elif grand_dict[trace_key_curr][0] == THIS_POS_ONLY_HAS_IF and trace_key_curr != trace_key_prev \
                        and run_count in grand_dict[trace_key_curr][1] and trace_key_curr not in already_thened_dict \
                        and already_ifed_dict[trace_key_curr] == 1:
                    grand_dict[trace_key_curr][0] = THIS_POS_HAS_IF_ELSE
                    blklist.discard(trace_key_curr)
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_IF_ELSE or trace_key_curr in already_thened_dict:
                        blklist.add(trace_key_curr)
                        grand_dict[trace_key_curr][1].add(run_count)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)
            elif reg_group_curr[1] == 'ConditionalStatementTrue':
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_COND_TRUE, {run_count}]
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_COND_TRUE:
                        blklist.add(trace_key_curr)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)
            elif reg_group_curr[1] == 'ConditionalStatementFalse':
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_COND_FALSE, {run_count}]
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_COND_FALSE:
                        blklist.add(trace_key_curr)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)

    grand_dict_copy = grand_dict.copy()
    if flag_mode == FLAG_W_AB:
        threshold = DIFF_THRESHD_W_AB
    else:
        threshold = DIFF_THRESHD_WO_AB
    for key, val in grand_dict.iteritems():
        if key in blklist or run_count - len(val[1]) > threshold:
            del grand_dict_copy[key]

    return grand_dict_copy


def log_reporter(path_to_dir, dict_w_ab, dict_wo_ab, mapping):
    def save_response(url, path_prefix):
        page = requests.get(url)
        if url.split('/')[-1] == '':
            script_name = url.split('/')[-2]
        else:
            script_name = url.split('/')[-1]
        f_cache = open(path_prefix + "/" + script_name, 'w')
        content = page.text
        f_cache.write(content)
        f_cache.close()

    def process_record(rec):
        return rec.split()[0][1:]

    f = open(path_to_dir + 'diff_res', 'w')
    flag_flipping = False
    script_set = set()
    print "[INFO][looper] Starting log diff..."
    for key, value in dict_wo_ab.iteritems():
        curr_val = dict_w_ab.get(key, -1)
        if curr_val == -1:
            continue
        if curr_val[0] != value[0]:
            flag_flipping = True
            script_url = process_record(key)
            script_set.add(script_url)
            if USE_SIG_MAPPING:
                match_mark = "Unmatched: pos " + mapping.map_to_full(str(key)) + " abp-on " + str(dict_w_ab.get(key, -1)) \
                         + " abp-off " + str(dict_wo_ab.get(key, -1))
            else:
                match_mark = "Unmatched: pos " + str(key) + " abp-on " + str(dict_w_ab.get(key, -1)) + \
                             " abp-off " + str(dict_wo_ab.get(key, -1))
            f.write(match_mark + '\n')
            print '[INFO][looper] ' + match_mark
    if len(script_set) > 0:
        os.makedirs(path_to_dir + '/script_cache/')
    path_to_dir += '/script_cache/'
    if SAVE_SCRIPT_SNAPSHOT:
        for scr_url in list(script_set):
            save_response(scr_url, path_to_dir)
    if flag_flipping is False:
        print "[INFO][looper] No unmatch detected!"
        f.write('No unmatch detected!\n')
    f.close()


def main_loop():
    while True:
        try:
            url = fetch_url()
            if not url:
                break
            try:
                shutil.rmtree(PATH_TO_FILTERED_LOG + url)
            except OSError as err:
                print "[INFO][looper] No existing directory"
            else:
                print "[INFO][looper] Deleted duplicate directory"

            for i in range(NUM_OF_RUNS):
                # 1st pass, with adblock enabled
                # tick its runtime
                p0 = url_loader(None, is_with_ext=True)
                time.sleep(TIMEOUT_WARMING)
                p1 = url_loader(url, is_with_ext=True)
                time.sleep(TIMEOUT_LOAD_W_AB)
                kill_child_processes(p0.pid)
                p0.kill()
                kill_child_processes(p1.pid)
                p1.kill()
                site_dir1 = log_extractor(PATH_TO_LOG, flag_mode=FLAG_W_AB, url=url)

                # 2nd pass, with adblock disabled
                p2 = url_loader(url, is_with_ext=False)
                time.sleep(TIMEOUT_LOAD_WO_AB)
                kill_child_processes(p2.pid)
                p2.kill()
                site_dir2 = log_extractor(PATH_TO_LOG, flag_mode=FLAG_WO_AB, url=url)
            cache = SignatureMapping()
            hashtable1 = log_differ(site_dir1, flag_mode=FLAG_W_AB, mapping=cache)
            hashtable2 = log_differ(site_dir2, flag_mode=FLAG_WO_AB, mapping=cache)
            curr_site_dir = PATH_TO_FILTERED_LOG + url + '/'
            if DELETE_ONGOING_RAW_LOG:
                print '[INFO][switch] Ongoing raw log removal enabled!'
                shutil.rmtree(curr_site_dir + 'w_adblocker/')
                shutil.rmtree(curr_site_dir + 'wo_adblocker/')
            log_reporter(curr_site_dir, hashtable1, hashtable2, mapping=cache)

            js_dict = single_log_stat_analyzer(curr_site_dir)
            dispatch_urls(js_dict, curr_site_dir)
            #sync_list_file(PATH_TO_URLFILE)
            print '[INFO][looper] This site is done\n'
        except Exception as e:
            error_msg = '[FATAL][looper] ' + str(e)
            traceback.print_exc()
            print(error_msg + '\n')
            error_log = open(PATH_TO_FILTERED_LOG + url + '/error_log.txt', 'w')
            error_log.write(str(error_msg))
            error_log.close()
            #sync_list_file(PATH_TO_URLFILE)
            continue

    print '[INFO][looper] A batch of experiments are done!'


def call_stack_test():
    def load(path_to_file):
        f = open(path_to_file, 'r')
        lst = f.readlines()
        f.close()
        return lst

    def unload(path_to_file, lst):
        f = open(path_to_file, 'w')
        f.writelines(lst)
        f.close()
        return

    def call_stack_builder(line):
        if len(line) == 1:
            return
        eles = line.split(" ")
        if eles[2] == "CALL":
            call_stack.append(eles[3] + "_" + eles[4] + "_" + eles[5].strip())
        elif eles[2] == "RET":
            if call_stack[-1] == eles[3] + "_" + eles[4] + "_" + eles[5].strip():
                call_stack.pop()
                print call_stack

    call_stack = []
    log = load("/home/hu/work/adblockJSLog.txt")
    for line in log:
        call_stack_builder(line)
    print call_stack


if __name__ == '__main__':
    files = []
    for fname in os.listdir(PATH_TO_FILTERED_LOG):
        files.append(PATH_TO_FILTERED_LOG + fname)
    print len(files)
    for url in files:
        try:
            print url
            site_dir1 = (url + '/w_adblocker/')
            site_dir2 = (url + '/wo_adblocker/')
            cache = SignatureMapping()
            hashtable1 = log_differ(site_dir1, flag_mode=FLAG_W_AB, mapping=cache)
            hashtable2 = log_differ(site_dir2, flag_mode=FLAG_WO_AB, mapping=cache)
            curr_site_dir = url + '/'
            log_reporter(curr_site_dir, hashtable1, hashtable2, mapping=cache)
        except Exception:
            continue
    #call_stack_test()
