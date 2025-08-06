import os
import logging
from flask import abort

logger = logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def cleanup_temp_file(filepath):
    """Safely remove temporary file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Removed temp file: {filepath}")
    except Exception as e:
        logger.error(f"Error removing temp file {filepath}: {str(e)}")

def check_file_size(request, config):
    """Check if uploaded file exceeds size limit"""
    if request.method == 'POST' and 'image' in request.files:
        if request.content_length > config['MAX_CONTENT_LENGTH']:
            logger.warning("File size exceeds limit")
            abort(413)  # Payload Too Large