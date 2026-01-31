import base64
import reflex as rx


class ImageFileHandler:
    """Encapsulates upload/remove helpers that mutate the state."""

    async def handle_upload(self, state, files: list[rx.UploadFile]):
        """Handle image uploads."""
        for file in files:
            upload_data = await file.read()
            base64_image = base64.b64encode(upload_data).decode("utf-8")
            state.uploaded_images.append(base64_image)

    def remove(self, state, index: int):
        """Remove an uploaded image."""
        state.uploaded_images.pop(index)


image_file_handler = ImageFileHandler()

