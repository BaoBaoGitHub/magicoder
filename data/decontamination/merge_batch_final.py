def merge_files(file1, file2, output_file):
    with open(file1, 'r', encoding='utf-8') as f1, \
         open(file2, 'r', encoding='utf-8') as f2, \
         open(output_file, 'w', encoding='utf-8') as out:
        for line in f1:
            out.write(line)
        for line in f2:
            out.write(line)

def main():
    file1 = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/backup_merged_data_clean_up_decontamination_modified.jsonl'
    file2 = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/backup_processed_batch_inference_data_clean_up_decontamination_modified.jsonl'
    output_file = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/backup_merged_final.jsonl'
    merge_files(file1, file2, output_file)
    print("合并完成，输出文件：", output_file)

if __name__ == '__main__':
    main()