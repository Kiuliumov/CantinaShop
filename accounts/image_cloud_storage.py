import cloudinary.uploader
from typing import Union
from django.core.files.uploadedfile import UploadedFile


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
