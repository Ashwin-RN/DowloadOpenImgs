import argparse
import csv
import subprocess
import os
import random
from tqdm import tqdm
import multiprocessing
from multiprocessing import Pool as thread_pool

cpu_count = multiprocessing.cpu_count()

parser = argparse.ArgumentParser(description='Download Class specific images from OpenImagesV4')
parser.add_argument("--mode", help="Dataset category - train, validation or test", required=True)
parser.add_argument("--classes", help="Names of object classes to be downloaded", required=True)
parser.add_argument("--nthreads", help="Number of threads to use", required=False, type=int, default=cpu_count*2)
parser.add_argument("--occluded", help="Include occluded images", required=False, type=int, default=1)
parser.add_argument("--truncated", help="Include truncated images", required=False, type=int, default 1)
parser.add_argument("--groupOf", help="Include groupOf images", required=False, type=int, default=1)
parser.add_argument("--depiction", help="Include depiction images", required=False, type=int, default=1)
parser.add_argument("--inside", help="Include inside images", required=False, type=int, default=1)
parser.add_argument("--percentage", help="Percentage of images to download for each class", required=False, type=int, default=100)

args = parser.parse_args()

run_mode = args.mode

threads = args.nthreads

percentage = args.percentage / 100.0

classes = []
for class_name in args.classes.split(','):
    classes.append(class_name)

with open('./class-descriptions-boxable.csv', mode='r') as infile:
    reader = csv.reader(infile)
    dict_list = {rows[1]:rows[0] for rows in reader}

subprocess.run(['rm', '-rf', run_mode])
subprocess.run(['mkdir', run_mode])

pool = thread_pool(threads)
commands = []

for ind in range(0, len(classes)):
    
    class_name = classes[ind]
    print("Class "+str(ind) + " : " + class_name)
    
    subprocess.run(['mkdir', run_mode+'/'+class_name])

    command = "grep " + dict_list[class_name.replace('_', ' ')] + " ./" + run_mode + "-annotations-bbox.csv"
    class_annotations = subprocess.run(command.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
    class_annotations = class_annotations.splitlines()

    # Apply filtering conditions
    filtered_annotations = []
    for line in class_annotations:
        line_parts = line.split(',')
        
        if (args.occluded == 0 and int(line_parts[8]) > 0):
            continue
        if (args.truncated == 0 and int(line_parts[9]) > 0):
            continue
        if (args.groupOf == 0 and int(line_parts[10]) > 0):
            continue
        if (args.depiction == 0 and int(line_parts[11]) > 0):
            continue
        if (args.inside == 0 and int(line_parts[12]) > 0):
            continue
        
        filtered_annotations.append(line)

    # Select a percentage of the filtered annotations
    num_annotations_to_select = int(len(filtered_annotations) * percentage)
    selected_annotations = random.sample(filtered_annotations, num_annotations_to_select)

    for line in selected_annotations:
        line_parts = line.split(',')

        command = 'aws s3 --no-sign-request --only-show-errors cp s3://open-images-dataset/' + run_mode + '/' + line_parts[0] + '.jpg ' + run_mode + '/' + class_name + '/' + line_parts[0] + '.jpg'
        commands.append(command)
        
        with open('%s/%s/%s.txt' % (run_mode, class_name, line_parts[0]), 'a') as f:
            f.write(','.join([class_name, line_parts[4], line_parts[5], line_parts[6], line_parts[7]]) + '\n')

print("Annotation Count : " + str(len(commands)))
commands = list(set(commands))
print("Number of images to be downloaded : " + str(len(commands)))

list(tqdm(pool.imap(os.system, commands), total=len(commands)))

pool.close()
pool.join()
