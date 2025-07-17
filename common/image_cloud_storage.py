import cloudinary.uploader
from typing import Union
from django.core.files.uploadedfile import UploadedFile
import re

def upload_to_cloud_storage(file: Union[UploadedFile, bytes], folder: str = "profile_pictures") -> str:
    """
    Uploads a file to Cloudinary and returns the secure URL.

    Args:
        file: The uploaded file object from a form (InMemoryUploadedFile or TemporaryUploadedFile).
        folder: Optional folder name to organize files in Cloudinary.

    Returns:
        str: The secure URL of the uploaded image.
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            overwrite=True,
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {str(e)}")

def get_public_id_from_url(url: str) -> str:
    """
    Extract the Cloudinary public ID from the URL.
    """
    pattern = r'/image/upload/(v\d+/)?(.+)\.[a-zA-Z]+$'
    match = re.search(pattern, url)
    if match:
        return match.group(2)
    return ''

def delete_cloudinary_image(public_id: str) -> bool:
    try:
        response = cloudinary.uploader.destroy(public_id)
        return response.get('result') == 'ok'
    except Exception as e:
        print(f"Error deleting Cloudinary image: {e}")
        return False