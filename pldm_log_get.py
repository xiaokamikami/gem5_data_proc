import re  
import os  
import csv  

def extract_info_from_log(file_path):
    print(f"处理文件: {file_path}")

    instrCnt, cycleCnt, IPC = None, None, None  

    with open(file_path, 'r') as file:
        content = file.read()
    pattern = r'instrCnt = (\d+), cycleCnt = (\d+), IPC = ([\d.]+)'
    match = re.search(pattern, content)
    if match:
        instrCnt = int(match.group(1))
        cycleCnt = int(match.group(2))
        IPC = float(match.group(3))
        print(f"找到所有值: instrCnt={instrCnt}, cycleCnt={cycleCnt}, IPC={IPC}")
    else:
        print("未找到所需的所有信息")

    pattern = r'.*/checkpoint-0-0-0/([^/]+)/(\d+)/_\d+_([0-9.]+)_\.zstd'
    match = re.search(pattern, content)
    
    if match:
        benchmark = match.group(1)  # 例如 'gcc_s04'
        checkpoint = match.group(2)  # 例如 '8005'
        weights = float(match.group(3))  # 例如 0.011782

    print(f'{benchmark} {checkpoint} {instrCnt} {cycleCnt} {IPC} {weights}')
    return benchmark, checkpoint, instrCnt, cycleCnt, IPC , weights
  
def main(log_dir, output_csv):  
    """遍历日志目录并写入CSV文件"""  
    header = ['', 'workload', 'bmk', 'point', 'instrCnt', 'Cycles', 'ipc', 'weight']  
    with open(output_csv, 'w', newline='') as csvfile:  
        writer = csv.writer(csvfile)  
        writer.writerow(header)  
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(log_dir, filename)
                workload, point, instrCnt, cycleCnt, IPC, weights = extract_info_from_log(file_path)
                if all([workload, point, instrCnt, cycleCnt, IPC, weights]):
                    program_name = f"{workload}_{point}"
                    bmk = workload.split('_')[0]
                    writer.writerow([program_name, workload, bmk, point, instrCnt, cycleCnt, IPC, weights])

  
if __name__ == "__main__":  
    log_directory = '/nfs/home/fengkehan/gem5_data_proc/ckpt_all_logs'  # 替换为你的日志文件目录  
    output_csv_file = 'output_pldm.csv'  # 输出CSV文件的名称  
    main(log_directory, output_csv_file)