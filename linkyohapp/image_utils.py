import os
import logging
import subprocess
from io import BytesIO
from pathlib import Path
from PIL import Image, UnidentifiedImageError, ImageFile
from django.core.files.base import ContentFile
from django.conf import settings

# Enable large image handling
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Check if we have pillow-heif installed for HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False

# Maximum dimensions for different image types
AVATAR_MAX_SIZE = (400, 400)
COVER_MAX_SIZE = (1200, 600)
GIG_PHOTO_MAX_SIZE = (800, 600)

# Quality settings for compression
JPEG_QUALITY = 85
PNG_COMPRESSION = 6  # PNG compression level (0-9)
WEBP_QUALITY = 80   # WebP quality (0-100)

# Directory for original images
ORIGINALS_DIR = 'originals'

# Logger for image processing
logger = logging.getLogger(__name__)

def is_heic_image(file_path):
    """
    Check if an image is in HEIC/HEIF format

    Args:
        file_path: Path to the image file

    Returns:
        bool: True if the image is HEIC/HEIF, False otherwise
    """
    # Check file extension
    ext = Path(file_path).suffix.lower()
    if ext in ('.heic', '.heif'):
        return True

    # If extension doesn't match, try to check file header
    try:
        with open(file_path, 'rb') as f:
            header = f.read(12)
            # Check for HEIC file signature
            if b'ftypheic' in header or b'ftypheix' in header or b'ftyphevc' in header or b'ftypheim' in header:
                return True
    except Exception:
        pass

    return False

def convert_heic_to_jpeg(input_path, output_path=None):
    """
    Convert HEIC image to JPEG format

    Args:
        input_path: Path to the HEIC image
        output_path: Path to save the JPEG image (if None, uses input path with .jpg extension)

    Returns:
        str: Path to the converted image, or None if conversion failed
    """
    if output_path is None:
        output_path = str(Path(input_path).with_suffix('.jpg'))

    # Try using pillow-heif if available
    if HEIF_SUPPORT:
        try:
            img = Image.open(input_path)
            img.save(output_path, format='JPEG', quality=JPEG_QUALITY)
            return output_path
        except Exception as e:
            logger.warning(f"Failed to convert HEIC using pillow-heif: {str(e)}")

    # Fallback to external tools if available
    try:
        # Try using ImageMagick's convert
        subprocess.run(['convert', input_path, output_path], check=True)
        return output_path
    except (subprocess.SubprocessError, FileNotFoundError):
        try:
            # Try using heif-convert if available
            subprocess.run(['heif-convert', input_path, output_path], check=True)
            return output_path
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error(f"Failed to convert HEIC image {input_path}. Install pillow-heif or ImageMagick.")
            return None

def get_original_path(path):
    """
    Convert a path to its corresponding original path
    e.g., 'profile_avatars/user_1/avatar.jpg' -> 'profile_avatars/originals/user_1/avatar.jpg'
    """
    dirname, filename = os.path.split(path)
    return os.path.join(dirname, ORIGINALS_DIR, filename)

def process_image(image_field, max_size, format=None):
    """
    Process an image by:
    1. Saving the original image to the originals directory
    2. Resizing the image to fit within max_size while maintaining aspect ratio
    3. Detecting the image format and using appropriate compression
    4. Converting unsupported formats to web-friendly formats
    5. Handling special formats like HEIC/HEIF

    Args:
        image_field: A Django ImageField or FileField instance
        max_size: A tuple of (max_width, max_height)
        format: The output format (None to auto-detect, or 'JPEG', 'PNG', 'WEBP')

    Returns:
        True if processing was successful, False otherwise
    """
    if not image_field:
        return False

    # Get the original image path and name
    original_path = image_field.path
    original_name = image_field.name

    # Check if this is a HEIC/HEIF image that needs conversion
    if is_heic_image(original_path):
        logger.info(f"Detected HEIC/HEIF image: {original_name}")
        # Convert to JPEG first
        converted_path = convert_heic_to_jpeg(original_path)
        if converted_path:
            logger.info(f"Successfully converted HEIC to JPEG: {converted_path}")
            # Update the path to the converted image
            original_path = converted_path
        else:
            logger.error(f"Failed to convert HEIC image: {original_name}")
            return False

    try:
        # Open the image using PIL
        img = Image.open(original_path)

        # Auto-detect format if not specified
        if format is None:
            # Get original format
            original_format = img.format

            # Use original format if it's web-friendly, otherwise default to JPEG
            if original_format in ('JPEG', 'PNG', 'WEBP'):
                format = original_format
            else:
                # For non-web-friendly formats, convert to JPEG or WebP
                format = 'WEBP' if 'WEBP' in Image.SAVE_ALL_FORMATS else 'JPEG'
                logger.info(f"Converting {original_format} image to {format} for web compatibility")

        # Convert color mode if needed
        if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if 'A' in img.mode:  # If there's an alpha channel
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
            else:
                background.paste(img)
            img = background
        elif format == 'WEBP' and img.mode == 'P':
            # Convert palette mode to RGBA for WebP
            img = img.convert('RGBA')

        # Calculate new dimensions while maintaining aspect ratio
        img.thumbnail(max_size, Image.LANCZOS)

        # Save the processed image to a BytesIO object
        output = BytesIO()

        # Save with appropriate quality settings
        if format == 'JPEG':
            img.save(output, format=format, quality=JPEG_QUALITY, optimize=True)
        elif format == 'PNG':
            img.save(output, format=format, compress_level=PNG_COMPRESSION, optimize=True)
        elif format == 'WEBP':
            img.save(output, format=format, quality=WEBP_QUALITY)
        else:
            # Fallback for other formats
            img.save(output, format=format)

        # Move the original file to the originals directory
        originals_dir = os.path.join(os.path.dirname(original_path), ORIGINALS_DIR)
        os.makedirs(originals_dir, exist_ok=True)

        original_filename = os.path.basename(original_path)
        original_dest = os.path.join(originals_dir, original_filename)

        # Only copy to originals if it doesn't already exist there
        if not os.path.exists(original_dest):
            # Create a copy of the original file
            with open(original_path, 'rb') as f:
                original_content = f.read()

            with open(original_dest, 'wb') as f:
                f.write(original_content)

        # Determine the output extension based on format
        ext_map = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}
        output_ext = ext_map.get(format, '.jpg')

        # Get the base filename without extension
        base_name = os.path.splitext(os.path.basename(original_name))[0]
        output_filename = f"{base_name}{output_ext}"

        # Replace the image field's file with the processed image
        output.seek(0)
        content = ContentFile(output.read())
        image_field.save(output_filename, content, save=False)

        logger.info(f"Successfully processed image {original_name} to {format} format")
        return True
    except UnidentifiedImageError:
        logger.error(f"Could not identify image format for {original_name}")
        return False
    except IOError as e:
        logger.error(f"IO error processing image {original_name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error processing image {original_name}: {str(e)}", exc_info=True)
        return False

def process_avatar(avatar_field):
    """
    Process a profile avatar image

    Avatars are typically small images that need to be displayed quickly,
    so we use auto-detection but prefer JPEG or WebP for better compression.
    """
    return process_image(avatar_field, AVATAR_MAX_SIZE, format=None)

def process_cover(cover_field):
    """
    Process a profile cover image

    Cover images are larger and may benefit from WebP's better compression,
    but we use auto-detection to preserve transparency if needed.
    """
    return process_image(cover_field, COVER_MAX_SIZE, format=None)

def process_gig_photo(photo_field):
    """
    Process a gig photo image

    Gig photos are product images that may need transparency (PNG) or
    better compression (WebP), so we use auto-detection.
    """
    return process_image(photo_field, GIG_PHOTO_MAX_SIZE, format=None)
