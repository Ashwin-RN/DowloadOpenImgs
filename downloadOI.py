# Modified Version by Ashwin R Nair
# Original by: Sunita Nayak, Big Vision LLC

import argparse
import csv
import subprocess
import os
from tqdm import tqdm
import multiprocessing
from multiprocessing import Pool as thread_pool
import random

cpu_count = multiprocessing.cpu_count()

parser = argparse.ArgumentParser(description='Download Class specific images from OpenImagesV4')
parser.add_argument("--mode", help="Dataset category - train, validation or test", required=True)
parser.add_argument("--classes", help="Names of object classes to be downloaded", required=True)
parser.add_argument("--nthreads", help="Number of threads to use", type=int, default=cpu_count*2)
parser.add_argument("--occluded", help="Include occluded images", type=int, default=1)
parser.add_argument("--truncated", help="Include truncated images", type=int, default=1)
parser.add_argument("--groupOf", help="Include groupOf images", type=int, default=1)
parser.add_argument("--depiction", help="Include depiction images", type=int, default=1)
parser.add_argument("--inside", help="Include inside images", type=int, default=1)
parser.add_argument("--percentage", help="Percentage of images to download per class", type=int, default=100)
parser.add_argument("--drive_path", help="Directory to save the images", default='.')

args = parser.parse_args()

run_mode = args.mode
threads = args.nthreads
percentage = args.percentage
drive_path = args.drive_path
classes = [class_name.strip() for class_name in args.classes.split(',')]

# Ensure the drive_path directory exists
if not os.path.exists(drive_path):
    os.makedirs(drive_path)

# Open class-descriptions-boxable.csv file
with open(os.path.join(drive_path, 'class-descriptions-boxable.csv'), mode='r') as infile:
    reader = csv.reader(infile)
    dict_list = {rows[1]: rows[0] for rows in reader}

# Create mode directory
mode_path = os.path.join(drive_path, run_mode)
if not os.path.exists(mode_path):
    os.makedirs(mode_path)

pool = thread_pool(threads)
commands = []
cnt = 0

# Load checkpoint data
checkpoint_file = os.path.join(drive_path, 'checkpoint.txt')
downloaded_images = set()
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r') as f:
        downloaded_images = set(f.read().splitlines())

for ind in range(0, len(classes)):
    class_name = classes[ind]
    print("Class " + str(ind) + " : " + class_name)
    
    class_dir = os.path.join(mode_path, class_name)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    command = f"grep {dict_list[class_name.replace('_', ' ')]} {os.path.join(drive_path, run_mode + '-annotations-bbox.csv')}"
    class_annotations = subprocess.run(command.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
    class_annotations = class_annotations.splitlines()

    random.shuffle(class_annotations)
    class_annotations = class_annotations[:len(class_annotations) * percentage // 100]  # Keep specified percentage

    for line in class_annotations:
        line_parts = line.split(',')

        # Check if the image is already downloaded
        if line_parts[0] in downloaded_images:
            continue
        
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
        commands.append(command)
        
        with open(f'{class_dir}/{line_parts[0]}.txt', 'a') as f:
            f.write(','.join([class_name, line_parts[4], line_parts[5], line_parts[6], line_parts[7]]) + '\n')

print("Annotation Count : " + str(cnt))
commands = list(set(commands))
print("Number of images to be downloaded : " + str(len(commands)))

# Define a function to execute the command and save progress
def execute_command(command):
    os.system(command)
    image_id = command.split()[-1].split('/')[-1].replace('.jpg', '')
    with open(checkpoint_file, 'a') as f:
        f.write(image_id + '\n')

list(tqdm(pool.imap(execute_command, commands), total=len(commands)))

pool.close()
pool.join()

# Save the checkpoint after completing the download
save_checkpoint(checkpoint)

