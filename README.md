Download Open Images


This script downloads images from the Open Images V4 dataset based on specified classes. It allows filtering by dataset category and includes options to include or exclude occluded, truncated, groupOf, depiction, and inside images.

Usage

python3 downloadOI.py --classes 'Brassiere,Coat,Dress,Jacket,Jeans,Miniskirt,Scarf,Shirt,Shorts,Skirt,Suit,Sunglasses,Tie,Trousers,Backpack,Belt,Hat,Fedora,Sombrero,CowboyHat,Earrings,Necklace,Tiara,Handbag,HighHeels,Glove' --mode train


Parameters
--mode: Dataset category (train, validation, test)
--classes: Comma-separated list of object classes to download
--nthreads: Number of threads to use (default: 2 * CPU count)
--occluded, --truncated, --groupOf, --depiction, --inside: Include these types of images (default: 1)
