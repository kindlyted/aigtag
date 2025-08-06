import os
import json
from flasgger import Swagger, swag_from
from services import invoke_qwen, invoke_qwen_with_picture
from utils import allowed_file, cleanup_temp_file, check_file_size
from werkzeug.utils import secure_filename
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from constants import HERO_OPTIONS_MAPPING

load_dotenv()  # 加载 .env 文件

# Initialize Flask app
app = Flask(__name__)
# CORS(app)  # 允许所有来源访问（开发环境用）
# 从环境变量获取允许的域名列表
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')

# 配置 CORS，只允许特定域名访问
CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Configuration
app.config.update({
    'UPLOAD_FOLDER': 'temp_uploads',
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB limit
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tif', 'tiff', 'webp', 'heic'},
    'SWAGGER': {
        'title': 'AIGTag API',
        'uiversion': 3,
        'description': 'API documentation for AIGTag backend services'
    }
})

# Initialize Swagger
Swagger(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    check_file_size(request, app.config)

@app.route('/ask', methods=['POST'])
@swag_from({
    'tags': ['AI Services'],
    'description': '调用AI模型生成回答',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'prompt_id': {'type': 'string', 'description': '提示模板ID', 'example': 'zhouyi'},
                    'user_input': {'type': 'string', 'description': '用户输入内容', 'example': '测试输入'}
                },
                'required': ['prompt_id', 'user_input']
            }
        }
    ],
    'responses': {
        '200': {
            'description': '成功响应',
            'examples': {
                'application/json': {
                    'result': 'AI生成的回答内容'
                }
            }
        },
        '400': {
            'description': '参数错误',
            'examples': {
                'application/json': {
                    'error': 'Missing required parameters'
                }
            }
        },
        '500': {
            'description': '服务器内部错误',
            'examples': {
                'application/json': {
                    'error': 'Internal server error'
                }
            }
        }
    }
})
def invoke_qwen_api():

    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        prompt_id = data.get('prompt_id')
        user_input = data.get('user_input')
        model_name = 'deepseek-v3'

        if not prompt_id or not user_input:
            return jsonify({"error": "Missing required parameters"}), 400

        if prompt_id not in HERO_OPTIONS_MAPPING:
            return jsonify({"error": "Invalid prompt ID"}), 400
            
        prompt_path = HERO_OPTIONS_MAPPING[prompt_id]['prompt_path']

        result = invoke_qwen(prompt_path, user_input, model_name)
        return jsonify({"result": result})

    except Exception as e:
        logger.error(f"Error in invoke_qwen: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/get-hero-options', methods=['GET'])
@swag_from({
    'tags': ['Configuration'],
    'description': '获取所有可用的AI服务选项',
    'responses': {
        '200': {
            'description': '成功响应',
            'examples': {
                'application/json': {
                    'options': [
                        {'value': 'zhouyi', 'label': '周易解读'},
                        {'value': 'taluo', 'label': '塔罗解读'},
                        {'value': 'ouzhou', 'label': '北欧女巫'}
                    ]
                }
            }
        },
        '500': {
            'description': '服务器内部错误',
            'examples': {
                'application/json': {
                    'error': 'Internal server error'
                }
            }
        }
    }
})
def get_hero_options():
    try:
        options = [
            {"value": key, "label": value['label']}
            for key, value in HERO_OPTIONS_MAPPING.items()
        ]
        return jsonify({"options": options})
    except Exception as e:
        logger.error(f"Error in get_hero_options: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/analyze-image', methods=['POST'])
@swag_from({
    'tags': ['AI Services'],
    'description': '上传图片并调用AI模型分析',
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'image',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '支持的格式: png, jpg, jpeg, gif, bmp, tif, tiff, webp, heic'
        }
    ],
    'responses': {
        '200': {
            'description': '成功响应',
            'examples': {
                'application/json': {
                    'result': 'AI生成的图片分析结果'
                }
            }
        },
        '400': {
            'description': '参数错误',
            'examples': {
                'application/json': {
                    'error': 'File type not allowed'
                }
            }
        },
        '500': {
            'description': '服务器内部错误',
            'examples': {
                'application/json': {
                    'error': 'Internal server error'
                }
            }
        }
    }
})
def invoke_qwen_with_picture_api():
    # 文件检查逻辑保持不变
    if 'image' not in request.files:
        logger.warning("No image file in request")
        return jsonify({"error": "No image file provided"}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        logger.warning("Empty filename")
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(image_file.filename, app.config['ALLOWED_EXTENSIONS']):
        logger.warning(f"Disallowed file type: {image_file.filename}")
        return jsonify({"error": "File type not allowed"}), 400
    
    try:
        # 保存文件逻辑保持不变
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(image_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(temp_path)
        logger.info(f"File saved to: {temp_path}")
        
        # 调用函数时强制使用硬编码路径
        result = json.loads(invoke_qwen_with_picture(image_path=temp_path, prompt_path="./backend/prompt/vl.prompt"))
        return jsonify({"result": result})
        
    except IOError as e:
        logger.error(f"File save error: {str(e)}")
        return jsonify({"error": "File processing failed"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cleanup_temp_file(temp_path)

if __name__ == "__main__":
    # Create upload folder if not exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Run the app
    app.run(host='0.0.0.0', port=5008, debug=True)