import base64
import reflex as rx


async def handle_image_upload(state, files: list[rx.UploadFile]):
    """Handle image uploads"""
    for file in files:
        upload_data = await file.read()
        # Convert to base64
        base64_image = base64.b64encode(upload_data).decode('utf-8')
        state.uploaded_images.append(base64_image)


def remove_image(state, index: int):
    """Remove an uploaded image"""
    state.uploaded_images.pop(index)

