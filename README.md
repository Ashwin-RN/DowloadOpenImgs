---

# Download OpenImages Dataset

This script downloads images from the OpenImages dataset based on specified classes and modes (train, validation, or test). It supports multi-threaded downloads and saves progress to handle interruptions gracefully.

## Features

- Downloads images for specified classes from OpenImages.
- Supports multiple modes: train, validation, test.
- Optional filters for image types (occluded, truncated, groupOf, depiction, inside).
- Percentage control for the number of images to download per class.
- Saves progress to a checkpoint file to resume downloads if interrupted.
- Parallel processing using threads for efficient downloading.

## Requirements

- Python 3.x
- `wget`
- `aws-cli` (configured to access Open Images dataset)
- `tqdm` for progress visualization

## Installation

1. Clone the repository or download the script:
   ```bash
   git clone https://github.com/ashwinrnairopenimages/download-openimages
   cd download-openimages
   ```

2. Install required Python packages:
   ```bash
   pip install tqdm
   ```

## Usage

### Command-Line Arguments

- `--mode`: Dataset category - `train`, `validation`, or `test` (Required)
- `--classes`: Comma-separated list of object classes to download (Required)
- `--nthreads`: Number of threads to use for downloading (Optional, default: `os.cpu_count() * 2`)
- `--occluded`: Include occluded images (`1` or `0`, Optional, default: `1`)
- `--truncated`: Include truncated images (`1` or `0`, Optional, default: `1`)
- `--groupOf`: Include groupOf images (`1` or `0`, Optional, default: `1`)
- `--depiction`: Include depiction images (`1` or `0`, Optional, default: `1`)
- `--inside`: Include inside images (`1` or `0`, Optional, default: `1`)
- `--percentage`: Percentage of images to download per class (Optional, default: `100`)
- `--drive_path`: Directory to save the images (Optional, default: `.`)

### Example Usage

1. **Basic Usage**: Download all images of specific classes for training.
   ```bash
   python3 downloadOI.py --mode train --classes 'Brassiere,Coat,Dress,Jacket,Jeans'
   ```

2. **Specify Number of Threads**: Use 8 threads for downloading.
   ```bash
   python3 downloadOI.py --mode train --classes 'Brassiere,Coat,Dress,Jacket,Jeans' --nthreads 8
   ```

3. **Filter Images**: Exclude truncated images and only download 50% of the available images.
   ```bash
   python3 downloadOI.py --mode validation --classes 'Shirt,Shorts,Skirt' --truncated 0 --percentage 50
   ```

4. **Custom Save Location**: Save downloaded images to a specific directory.
   ```bash
   python3 downloadOI.py --mode test --classes 'Hat,Glove' --drive_path '/content/drive/MyDrive/Detectron2_Proj_Files'
   ```

## Checkpoints

The script includes a checkpoint mechanism that saves the list of downloaded image IDs to `checkpoint.txt` in the specified `drive_path`. If the script is interrupted, it will resume from where it left off using this checkpoint file.

