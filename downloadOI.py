# Modified Version by Ashwin R Nair
# Original by : Sunita Nayak, Big Vision LLC

import argparse
import csv
import subprocess
import os
from tqdm import tqdm
import multiprocessing
from multiprocessing import Pool as thread_pool
import random
import json

cpu_count = multiprocessing.cpu_count()

parser = argparse.ArgumentParser(description='Download Class specific images from OpenImagesV4')
parser.add_argument("--mode", help="Dataset category - train, validation or test", required=True)
parser.add_argument("--classes", help="Names of object classes to be downloaded", required=True)
parser.add_argument("--nthreads", help="Number of threads to use", required=False, type=int, default=cpu_count*2)
parser.add_argument("--occluded", help="Include occluded images", required=False, type=int, default=1)
parser.add_argument("--truncated", help="Include truncated images", required=False, type=int, default=1)
parser.add_argument("--groupOf", help="Include groupOf images", required=False, type=int, default=1)
parser.add_argument("--depiction", help="Include depiction images", required=False, type=int, default=1)
parser.add_argument("--inside", help="Include inside images", required=False, type=int, default=1)
parser.add_argument("--percentage", help="Percentage of images to download per class", required=True, type=int)
parser.add_argument("--drive_path", help="Path to Google Drive", required=True)

args = parser.parse_args()

run_mode = args.mode
threads = args.nthreads
percentage = args.percentage
drive_path = args.drive_path

# Create the drive path if it doesn't exist
if not os.path.exists(drive_path):
    os.makedirs(drive_path)

classes = [class_name.strip() for class_name in args.classes.split(',')]

with open(os.path.join(drive_path, 'class-descriptions-boxable.csv'), mode='r') as infile:
    reader = csv.reader(infile)
    dict_list = {rows[1]: rows[0] for rows in reader}

checkpoint_file = os.path.join(drive_path, 'download_checkpoint.json')

def load_checkpoint():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return {}

def save_checkpoint(checkpoint):
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f)

checkpoint = load_checkpoint()

subprocess.run(['rm', '-rf', os.path.join(drive_path, run_mode)])
subprocess.run(['mkdir', os.path.join(drive_path, run_mode)])

pool = thread_pool(threads)
commands = []
cnt = 0

for ind in range(0, len(classes)):
    class_name = classes[ind]
    print("Class " + str(ind) + " : " + class_name)
    
    class_dir = os.path.join(drive_path, run_mode, class_name)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    command = f"grep {dict_list[class_name.replace('_', ' ')]} {os.path.join(drive_path, run_mode)}-annotations-bbox.csv"
    class_annotations = subprocess.run(command.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
    class_annotations = class_annotations.splitlines()

    random.shuffle(class_annotations)
    class_annotations = class_annotations[:len(class_annotations) * percentage // 100]  # Keep specified percentage

    for line in class_annotations:
        line_parts = line.split(',')
        
        # IsOccluded, IsTruncated, IsGroupOf, IsDepiction, IsInside
        if (args.occluded == 0 and int(line_parts[8]) > 0):
            print("Skipped %s", line_parts[0])
            continue
        if (args.truncated == 0 and int(line_parts[9]) > 0):
            print("Skipped %s", line_parts[0])
            continue
        if (args.groupOf == 0 and int(line_parts[10]) > 0):
            print("Skipped %s", line_parts[0])
            continue
        if (args.depiction == 0 and int(line_parts[11]) > 0):
            print("Skipped %s", line_parts[0])
            continue
        if (args.inside == 0 and int(line_parts[12]) > 0):
            print("Skipped %s", line_parts[0])
            continue

        cnt += 1

        command = f'aws s3 --no-sign-request --only-show-errors cp s3://open-images-dataset/{run_mode}/{line_parts[0]}.jpg {class_dir}/{line_parts[0]}.jpg'
        
        if class_name not in checkpoint:
            checkpoint[class_name] = []
        
        if command not in checkpoint[class_name]:
            commands.append(command)
            checkpoint[class_name].append(command)

        with open(os.path.join(class_dir, f'{line_parts[0]}.txt'), 'a') as f:
            f.write(','.join([class_name, line_parts[4], line_parts[5], line_parts[6], line_parts[7]]) + '\n')

print("Annotation Count : " + str(cnt))
commands = list(set(commands))
print("Number of images to be downloaded : " + str(len(commands)))

# Save the checkpoint before starting the download
save_checkpoint(checkpoint)

for _ in tqdm(pool.imap_unordered(os.system, commands), total=len(commands)):
    pass

pool.close()
pool.join()

# Save the checkpoint after completing the download
save_checkpoint(checkpoint)

