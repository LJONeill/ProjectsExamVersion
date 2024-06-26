import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.color import rgb2gray, rgba2rgb  # Import rgba2rgb function
from skimage.filters import threshold_otsu
from skimage.morphology import closing, square, opening, disk
from skimage.measure import label, regionprops
from skimage.segmentation import clear_border

# Paths to the image and the mask
image_path = 'PAT_1379_1300_924.png' #test images
mask_path = 'PAT_1379_1300_924_mask.png'

def calculate_compactness(region):
    perimeter = region.perimeter
    area = region.area
    if perimeter == 0:
        return 0
    return (perimeter ** 2) / (4 * np.pi * area)

def load_and_process_image(image_path, mask_path):
    # Load the image and the mask
    image = imread(image_path)
    mask = imread(mask_path)

    # Convert RGBA image to RGB if it has an alpha channel
    if image.shape[2] == 4:
        image = rgba2rgb(image)

    # Convert the image to grayscale
    gray_image = rgb2gray(image)

    # Adjust the threshold to focus on dark brown spots
    thresh = threshold_otsu(gray_image)
    binary = gray_image < thresh * 0.6  # Adjust the threshold value as needed for better separation

    # Apply the mask to the binary image
    binary_masked = np.logical_and(binary, mask)

    # Morphological operations to clean up the image
    binary_closed = closing(binary_masked, disk(1))  # Adjust the disk size as needed for better closing
    binary_opened = opening(binary_closed, disk(1))  # Adjust the disk size as needed for better opening

    # Remove artifacts connected to image border
    binary_cleared = clear_border(binary_opened)

    # Label and identify regions in the image
    label_image = label(binary_cleared)

    # Calculate compactness for each region
    compactness_threshold = 2  # Adjust as needed for better detection of small circular shapes
    regions = regionprops(label_image)
    image_label_overlay = np.zeros_like(label_image)
    for region in regions:
        compactness = calculate_compactness(region)
        if compactness > compactness_threshold:
            image_label_overlay[label_image == region.label] = 1

    return image, gray_image, binary_cleared, image_label_overlay, label_image

def display_results(image, gray_image, binary_cleared, label_image, dots_detected):
    fig, ax = plt.subplots(1, 4, figsize=(16, 4))
    ax[0].imshow(image)
    ax[0].set_title('Original Image')
    ax[0].axis('off')

    ax[1].imshow(gray_image, cmap='gray')
    ax[1].set_title('Grayscale Image')
    ax[1].axis('off')

    ax[2].imshow(binary_cleared, cmap='gray')
    ax[2].set_title('Binary Image')
    ax[2].axis('off')

    dots_detected_str = 'Dots Detected: ' + str(dots_detected)
    ax[3].text(0.5, 0.5, dots_detected_str, fontsize=12, ha='center')
    ax[3].axis('off')

    plt.tight_layout()
    plt.show()

# Load, process, and display
image, gray_image, binary_cleared, label_image, dots_detected = load_and_process_image(image_path, mask_path)

# Display the results
display_results(image, gray_image, binary_cleared, label_image, dots_detected)

# Load, process, and display
image, gray_image, binary_cleared, image_label_overlay, label_image = load_and_process_image(image_path, mask_path)
display_results(image, gray_image, binary_cleared, image_label_overlay, label_image)
