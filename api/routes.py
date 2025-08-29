import os
import re
import json
import csv
from datetime import datetime, timedelta
from io import StringIO
from flask import Blueprint, request, jsonify, current_app, Response, stream_template, abort
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from PIL import Image

from models import FoodLog, FoodItem, CoachMessage, Photo, WeighIn, WaterIntake, Settings, User, NotificationTemplate, Notification
from extensions import db
from services.ollama_client import OllamaClient
from services.nutrition_search import NutritionSearch
from services.food_parser import FoodParser
from services.recommendations import RecommendationService
from services.analytics import AnalyticsService
from services.vision_classifier import VisionClassifier

api_bp = Blueprint('api', __name__)


@api_bp.route('/healthz')
@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@api_bp.route('/search_nutrition')
@login_required
def search_nutrition():
    """Search for nutrition information"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    try:
        nutrition_search = NutritionSearch()
        results = nutrition_search.search_food(query)
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in nutrition search: {e}")
        return jsonify({'error': 'Search failed'}), 500


@api_bp.route('/search_barcode')
@login_required  
def search_barcode():
    """Search for food by barcode"""
    barcode = request.args.get('barcode', '').strip()
    
    if not barcode:
        return jsonify({'error': 'Barcode parameter is required'}), 400
    
    try:
        nutrition_search = NutritionSearch()
        result = nutrition_search.search_barcode(barcode)
        
        if result:
            return jsonify({'result': result})
        else:
            return jsonify({'error': 'Product not found'}), 404
    
    except Exception as e:
        current_app.logger.error(f"Error in barcode search: {e}")
        return jsonify({'error': 'Barcode search failed'}), 500


@api_bp.route('/models/list')
@login_required
def list_models():
    """List available Ollama models"""
    try:
        client = OllamaClient.from_user_settings()
        models = client.list_models()
        
        return jsonify({
            'models': models,
            'count': len(models)
        })
    
    except Exception as e:
        current_app.logger.error(f"Error listing models: {e}")
        return jsonify({'error': 'Failed to list models'}), 500


@api_bp.route('/models/pull', methods=['POST'])
@login_required
def pull_model():
    """Pull a model from Ollama"""
    data = request.get_json()
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'Model name is required'}), 400
    
    try:
        client = OllamaClient.from_user_settings()
        success = client.pull_model(model_name)
        
        if success:
            return jsonify({'status': 'success', 'message': f'Model {model_name} pulled successfully'})
        else:
            return jsonify({'error': 'Failed to pull model'}), 500
    
    except Exception as e:
        current_app.logger.error(f"Error pulling model: {e}")
        return jsonify({'error': 'Model pull failed'}), 500


@api_bp.route('/settings/test_ollama', methods=['POST'])
@login_required
def test_ollama_connection():
    """Test Ollama connection"""
    data = request.get_json()
    ollama_url = data.get('ollama_url')
    
    if not ollama_url:
        return jsonify({'error': 'Ollama URL is required'}), 400
    
    try:
        # This endpoint tests a specific URL, so we use the provided URL directly
        client = OllamaClient(ollama_url)
        connected = client.test_connection()
        
        return jsonify({
            'connected': connected,
            'url': ollama_url
        })
    
    except Exception as e:
        current_app.logger.error(f"Error testing Ollama connection: {e}")
        return jsonify({'connected': False, 'error': str(e)})


@api_bp.route('/logs', methods=['GET'])
@login_required
def get_food_logs():
    """Get food logs for the current user"""
    date_str = request.args.get('date')
    limit = request.args.get('limit', 50, type=int)
    
    query = FoodLog.query.filter_by(user_id=current_user.id)
    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(FoodLog.logged_at) == date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    logs = query.order_by(FoodLog.logged_at.desc()).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            'id': log.id,
            'food_name': log.custom_name or (log.food_item.canonical_name if log.food_item else ''),
            'meal': log.meal,
            'grams': log.grams,
            'calories': log.calories,
            'protein_g': log.protein_g,
            'carbs_g': log.carbs_g,
            'fat_g': log.fat_g,
            'fiber_g': log.fiber_g,
            'sugar_g': log.sugar_g,
            'sodium_mg': log.sodium_mg,
            'source': log.source,
            'logged_at': log.logged_at.isoformat()
        })
    
    return jsonify({'logs': result, 'count': len(result)})


@api_bp.route('/logs', methods=['POST'])
@login_required
def create_food_log():
    """Create a new food log entry"""
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    required_fields = ['custom_name', 'meal', 'grams', 'calories']
    for field in required_fields:
        if field not in data or not data[field]:
            if request.is_json:
                return jsonify({'error': f'Field {field} is required'}), 400
            else:
                return f"""
                    <div class="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <i class="fas fa-exclamation-triangle text-red-400"></i>
                            </div>
                            <div class="ml-3">
                                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                                    Missing required field
                                </h3>
                                <p class="mt-1 text-sm text-red-700 dark:text-red-300">
                                    Field {field} is required. Please fill in all required fields.
                                </p>
                            </div>
                        </div>
                    </div>
                """, 400
    
    try:
        # Create new food log
        log = FoodLog(
            user_id=current_user.id,
            custom_name=data['custom_name'],
            meal=data['meal'],
            grams=float(data['grams']),
            calories=float(data['calories']),
            protein_g=float(data.get('protein_g', 0)),
            carbs_g=float(data.get('carbs_g', 0)),
            fat_g=float(data.get('fat_g', 0)),
            fiber_g=float(data.get('fiber_g', 0)),
            sugar_g=float(data.get('sugar_g', 0)),
            sodium_mg=float(data.get('sodium_mg', 0)),
            source=data.get('source', 'manual')
        )
        
        db.session.add(log)
        db.session.commit()
        
        # Create notification for successful food logging
        try:
            from services.notification_service import ActionNotificationService
            ActionNotificationService.notify_food_logged(current_user.id, log)
        except Exception as e:
            current_app.logger.error(f"Failed to create food logged notification: {e}")
        
        # Return different response based on request type
        if request.is_json:
            return jsonify({
                'id': log.id,
                'message': 'Food logged successfully'
            }), 201
        else:
            # Return HTML response for htmx
            return f"""
                <div class="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-md p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-check-circle text-green-400"></i>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-green-800 dark:text-green-200">
                                Food logged successfully!
                            </h3>
                            <p class="mt-1 text-sm text-green-700 dark:text-green-300">
                                {data['custom_name']} has been added to your {data['meal']} log.
                            </p>
                            <div class="mt-3">
                                <a href="/dashboard" class="text-sm font-medium text-green-800 dark:text-green-200 hover:text-green-600 dark:hover:text-green-400">
                                    View Dashboard <i class="fas fa-arrow-right ml-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            """, 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating food log: {e}")
        
        if request.is_json:
            return jsonify({'error': 'Failed to create food log'}), 500
        else:
            return f"""
                <div class="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-exclamation-triangle text-red-400"></i>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                                Error logging food
                            </h3>
                            <p class="mt-1 text-sm text-red-700 dark:text-red-300">
                                There was an error saving your food log. Please try again.
                            </p>
                        </div>
                    </div>
                </div>
            """, 500


@api_bp.route('/logs/<int:log_id>', methods=['DELETE'])
@login_required
def delete_food_log(log_id):
    """Delete a food log entry"""
    log = FoodLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    
    if not log:
        return jsonify({'error': 'Food log not found'}), 404
    
    try:
        db.session.delete(log)
        db.session.commit()
        return jsonify({'message': 'Food log deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting food log: {e}")
        return jsonify({'error': 'Failed to delete food log'}), 500


@api_bp.route('/photo/upload', methods=['POST'])
@login_required
def upload_photo():
    """Upload and analyze food photo"""
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo file provided'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file or not _allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only images allowed.'}), 400
    
    try:
        # Save the file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{current_user.id}_{timestamp}_{filename}"
        
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'food')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Process the image
        _process_image(filepath)
        
        # Save photo record
        photo = Photo(
            user_id=current_user.id,
            filepath=filepath
        )
        db.session.add(photo)
        db.session.commit()
        
        # Analyze the photo
        candidates, meta = _analyze_food_photo(filepath, photo.id)
        
        # If analysis failed entirely, surface error to client
        if not candidates:
            current_app.logger.warning(f"Photo analysis returned no candidates. Warning: {meta.get('warning')}, Errors: {meta.get('errors')}")
            return jsonify({
                'photo_id': photo.id,
                'filename': filename,
                'error': 'Photo analysis failed',
                'warning': meta.get('warning'),
                'errors': meta.get('errors')
            }), 502
        
        response_body = {
            'photo_id': photo.id,
            'filename': filename,
            'candidates': candidates
        }
        
        # Include analysis metadata (e.g., fallback/vision, warnings)
        if meta.get('source'):
            response_body['analysis_source'] = meta['source']
        if meta.get('warning'):
            response_body['warning'] = meta['warning']
        if meta.get('errors'):
            response_body['errors'] = meta['errors']
        
        return jsonify(response_body), 201
    
    except Exception as e:
        current_app.logger.error(f"Error uploading photo: {e}")
        return jsonify({'error': 'Photo upload failed'}), 500


@api_bp.route('/coach/chat', methods=['POST'])
@login_required
def coach_chat():
    """Chat with AI coach"""
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        # Get user settings using helper function
        try:
            client = OllamaClient.from_user_settings()
            user_models = OllamaClient.get_user_models()
            chat_model = user_models['chat_model']
        except Exception as e:
            current_app.logger.error(f"Error getting user settings: {e}")
            return jsonify({'error': 'Failed to load user settings'}), 500
        
        if not chat_model:
            return jsonify({'error': 'No chat model configured. Please configure a model in settings.'}), 400
        
        # Save user message
        user_msg = CoachMessage(
            user_id=current_user.id,
            role='user',
            content=message
        )
        db.session.add(user_msg)
        
        # Get recent chat history
        recent_messages = CoachMessage.query.filter_by(user_id=current_user.id)\
            .order_by(CoachMessage.created_at.desc())\
            .limit(10).all()
        
        # Build context
        context = _build_coach_context(current_user.id)
        
        # Prepare messages for Ollama
        messages = []
        for msg in reversed(recent_messages[-5:]):  # Last 5 messages
            if msg.role != 'system':
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
        
        messages.append({'role': 'user', 'content': message})
        
        # Get response from Ollama using user settings
        system_prompt = user_models['system_prompt'] or _get_default_system_prompt()
        
        # Add context to system prompt
        enhanced_prompt = f"{system_prompt}\n\nUser Context:\n{context}"
        
        # Capture user_id outside the generator to avoid context issues
        user_id = current_user.id
        
        # Create a shared variable to store the response
        response_data = {'content': ''}
        
        def generate():
            try:
                for chunk in client.chat(messages, chat_model, enhanced_prompt, stream=True):
                    response_data['content'] += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': 'Chat stream failed'})}\n\n"
        
        # Create the response with a callback
        from flask import Response
        response = Response(generate(), mimetype='text/plain')
        app_obj = current_app._get_current_object()
        
        # Use response.call_on_close to save message after streaming
        def save_assistant_message():
            if response_data['content']:
                with app_obj.app_context():
                    try:
                        assistant_msg = CoachMessage(
                            user_id=user_id,
                            role='assistant',
                            content=response_data['content']
                        )
                        db.session.add(assistant_msg)
                        db.session.commit()
                    except Exception:
                        try:
                            db.session.rollback()
                        except Exception:
                            # Silently handle rollback errors
                            pass
        
        response.call_on_close(save_assistant_message)
        
        db.session.commit()  # Commit user message
        
        return response
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in coach chat: {e}")
        return jsonify({'error': 'Chat failed'}), 500


@api_bp.route('/coach/clear-history', methods=['DELETE'])
@login_required
def clear_coach_history():
    """Clear all coach chat history for the current user"""
    try:
        # Delete all coach messages for the current user
        deleted_count = CoachMessage.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully cleared {deleted_count} chat messages',
            'deleted_count': deleted_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error clearing coach history: {e}")
        return jsonify({'error': 'Failed to clear chat history'}), 500


@api_bp.route('/coach/history', methods=['GET'])
@login_required
def get_coach_history():
    """Get chat history for the current user"""
    try:
        # Get recent chat messages for the user
        messages = CoachMessage.query.filter_by(user_id=current_user.id)\
            .order_by(CoachMessage.created_at.asc())\
            .limit(50).all()
        
        messages_data = []
        for msg in messages:
            if msg.role != 'system':  # Don't include system messages in mobile app
                messages_data.append({
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat(),
                    'refs': msg.get_refs() if msg.refs else []
                })
        
        return jsonify({
            'messages': messages_data,
            'count': len(messages_data)
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting coach history: {e}")
        return jsonify({'error': 'Failed to get chat history'}), 500


@api_bp.route('/weigh-in', methods=['POST'])
@login_required
def record_weight():
    """Record a weight measurement"""
    data = request.get_json()
    weight_kg = data.get('weight_kg')
    
    if not weight_kg:
        return jsonify({'error': 'Weight is required'}), 400
    
    try:
        weigh_in = WeighIn(
            user_id=current_user.id,
            weight_kg=float(weight_kg)
        )
        db.session.add(weigh_in)
        db.session.commit()
        
        return jsonify({
            'id': weigh_in.id,
            'message': 'Weight recorded successfully'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error recording weight: {e}")
        return jsonify({'error': 'Failed to record weight'}), 500


@api_bp.route('/water-intake', methods=['POST'])
@login_required
def record_water():
    """Record water intake"""
    data = request.get_json()
    ml = data.get('ml')
    
    if not ml:
        return jsonify({'error': 'Water amount in ml is required'}), 400
    
    try:
        water_intake = WaterIntake(
            user_id=current_user.id,
            ml=int(ml)
        )
        db.session.add(water_intake)
        db.session.commit()
        
        return jsonify({
            'id': water_intake.id,
            'message': 'Water intake recorded successfully'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error recording water intake: {e}")
        return jsonify({'error': 'Failed to record water intake'}), 500


@api_bp.route('/analytics/nutrition-trends')
@login_required
def get_nutrition_trends():
    """Get nutrition trends chart data"""
    days = request.args.get('days', 30, type=int)
    
    try:
        data = AnalyticsService.get_nutrition_trends(current_user.id, days)
        return jsonify(data)
    
    except Exception as e:
        current_app.logger.error(f"Error getting nutrition trends: {e}")
        return jsonify({'error': 'Failed to get nutrition trends'}), 500


@api_bp.route('/analytics/weight-trends')
@login_required
def get_weight_trends():
    """Get weight trends chart data"""
    days = request.args.get('days', 90, type=int)
    
    try:
        data = AnalyticsService.get_weight_trends(current_user.id, days)
        return jsonify(data)
    
    except Exception as e:
        current_app.logger.error(f"Error getting weight trends: {e}")
        return jsonify({'error': 'Failed to get weight trends'}), 500


@api_bp.route('/analytics/dashboard')
@login_required
def get_dashboard_data():
    """Get dashboard analytics data"""
    try:
        # Get today's summary
        today_summary = RecommendationService.get_daily_summary(current_user.id)
        
        # Get weekly summary  
        weekly_summary = RecommendationService.get_weekly_summary(current_user.id)
        
        # Get meal distribution
        meal_distribution = AnalyticsService.get_meal_distribution(current_user.id, 7)
        
        # Get macro distribution
        macro_distribution = AnalyticsService.get_macro_distribution(current_user.id, 7)
        
        # Get logging streaks
        streaks = AnalyticsService.get_logging_streaks(current_user.id)
        
        # Get top foods
        top_foods = AnalyticsService.get_top_foods(current_user.id, 7, 5)
        
        return jsonify({
            'today': today_summary,
            'weekly': weekly_summary,
            'meal_distribution': meal_distribution,
            'macro_distribution': macro_distribution,
            'streaks': streaks,
            'top_foods': top_foods
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500


@api_bp.route('/export/logs.csv')
@login_required
def export_logs():
    """Export food logs as CSV"""
    start_date = request.args.get('from')
    end_date = request.args.get('to')
    
    try:
        # Parse dates
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.utcnow()
        
        # Get export data
        data = AnalyticsService.export_data(current_user.id, start_date, end_date)
        
        # Create CSV
        output = StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        csv_content = output.getvalue()
        output.close()
        
        # Create response
        response = Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=nutrition_log_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv'
            }
        )
        
        return response
    
    except Exception as e:
        current_app.logger.error(f"Error exporting logs: {e}")
        return jsonify({'error': 'Export failed'}), 500


# Helper functions

def _allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _process_image(filepath):
    """Process uploaded image (resize, strip EXIF, etc.)"""
    try:
        with Image.open(filepath) as img:
            # Strip EXIF data
            img = img.convert('RGB')
            
            # Resize if too large
            if img.width > 1920 or img.height > 1920:
                img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
            
            # Save processed image
            img.save(filepath, 'JPEG', quality=85, optimize=True)
    
    except Exception as e:
        current_app.logger.error(f"Error processing image: {e}")


def _analyze_food_photo(filepath, photo_id):
    """Analyze food photo and return (candidates, meta) with enhanced food identification"""
    try:
        meta = {'source': None, 'warning': None, 'errors': []}
        vision_items = []
        
        # Try Ollama vision first using user settings
        try:
            client = OllamaClient.from_user_settings()
            current_app.logger.info(f"Connecting to Ollama at: {client.base_url}")
            
            # Test connection first
            if not client.test_connection():
                current_app.logger.warning("Ollama is not available, check if Ollama is running")
                meta['warning'] = 'AI vision service unavailable - ensure Ollama is running and accessible'
                raise Exception("Ollama connection failed")
            
            user_models = OllamaClient.get_user_models()
            vision_model = user_models['vision_model']
            
            if vision_model:
                current_app.logger.info(f"Using Ollama vision model: {vision_model}")
                
                # Neutral, JSON-only prompt to avoid anchoring on examples
                food_prompt = """You are analyzing a food photograph.

Identify only the food items that are clearly visible in the image. Do not guess.

For each identified item, return an object with these fields:
- name: specific food name that matches what is visible
- portion_grams: numeric estimate of weight in grams
- confidence: a number from 0.0 to 1.0 for how sure you are

Output must be ONLY a JSON array (no prose, no markdown), for example:
[
  {"name": "item name", "portion_grams": 120, "confidence": 0.82}
]

If nothing is clearly identifiable, return []."""

                # Use the vision analysis method
                analysis_result = client.vision_analyze(filepath, vision_model, food_prompt)
                current_app.logger.info(f"Raw vision analysis result: {analysis_result}")
                current_app.logger.info(f"Vision analysis result type: {type(analysis_result)}")
                if analysis_result:
                    current_app.logger.info(f"Vision analysis result length: {len(analysis_result)} chars")
                
                if analysis_result:
                    # Try to extract JSON from the response
                    import re
                    
                    # First try to parse the entire response as JSON
                    try:
                        vision_items = json.loads(analysis_result.strip())
                        current_app.logger.info(f"Successfully parsed entire response as JSON with {len(vision_items)} items")
                        meta['source'] = 'vision'
                    except json.JSONDecodeError:
                        # Try to extract JSON array from text
                        json_match = re.search(r'\[.*?\]', analysis_result, re.DOTALL)
                        if json_match:
                            try:
                                vision_items = json.loads(json_match.group())
                                current_app.logger.info(f"Successfully parsed extracted JSON array with {len(vision_items)} food items from vision")
                                meta['source'] = 'vision'
                            except json.JSONDecodeError as e:
                                current_app.logger.warning(f"Failed to parse extracted JSON from vision result: {e}")
                                current_app.logger.warning(f"Extracted JSON was: {json_match.group()}")
                                meta['errors'].append(f"Vision JSON parse error: {str(e)}")
                                # Parse the text response as fallback
                                vision_items = _parse_vision_text_response(analysis_result)
                                if vision_items:
                                    meta['source'] = 'vision'
                        else:
                            current_app.logger.warning(f"No JSON array found in response: {analysis_result[:200]}...")
                            # Parse the text response
                            vision_items = _parse_vision_text_response(analysis_result)
                            if vision_items:
                                meta['source'] = 'vision'
                else:
                    current_app.logger.warning("No result from Ollama vision analysis")
                    meta['warning'] = 'Vision model returned no result'
            else:
                current_app.logger.warning("No vision model configured")
                meta['warning'] = 'No vision model configured'
                
        except Exception as e:
            current_app.logger.error(f"Error with Ollama vision: {e}")
            meta['errors'].append(f"Vision error: {str(e)}")
            # Don't fail completely, fall through to fallback
        
        # If Ollama vision failed, return error instead of fake results
        if not vision_items:
            current_app.logger.error("Vision analysis failed - no results from Ollama")
            meta['errors'].append("Vision analysis failed - check Ollama connection and vision model")
            return [], meta
        
        current_app.logger.info(f"Vision items before parsing: {vision_items}")
        current_app.logger.info(f"Vision items type: {type(vision_items)}, length: {len(vision_items) if hasattr(vision_items, '__len__') else 'N/A'}")
        
        # Ensure vision_items is a list before passing to parser
        if isinstance(vision_items, str):
            current_app.logger.warning("Vision items is still a string, attempting to parse as JSON")
            try:
                vision_items = json.loads(vision_items)
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse vision items string as JSON: {e}")
                return [], meta
        
        # Handle case where vision model returns a single dict instead of a list
        if isinstance(vision_items, dict):
            current_app.logger.info("Vision items is a dict, wrapping in list")
            vision_items = [vision_items]
        
        if not isinstance(vision_items, list):
            current_app.logger.error(f"Vision items is not a list: {type(vision_items)}")
            return [], meta
        
        # Parse results with enhanced nutrition lookup
        parser = FoodParser()
        try:
            candidates = parser.parse_vision_results(vision_items)
            current_app.logger.info(f"Parser returned {len(candidates)} candidates")
            
            # Ensure candidates is a list
            if not isinstance(candidates, list):
                current_app.logger.error(f"Parser returned non-list type: {type(candidates)}")
                candidates = []
        except Exception as e:
            current_app.logger.error(f"Error parsing vision results: {e}")
            candidates = []
        
        # Enhance candidates with nutrition search results
        for candidate in candidates:
            if candidate and isinstance(candidate, dict) and candidate.get('name'):
                # Search for nutrition data
                nutrition_results = parser.nutrition_search.search_food(candidate['name'])
                if nutrition_results:
                    candidate['search_results'] = nutrition_results[:3]
                    
                    # Use the best nutrition result if available
                    for result in nutrition_results:
                        if result.get('nutrition') and result['source'] == 'openfoodfacts':
                            # Scale nutrition to portion size
                            nutrition = result['nutrition']
                            portion_grams = candidate.get('portion_grams', 100)
                            scale_factor = portion_grams / 100
                            
                            candidate['nutrition'] = {
                                'calories': nutrition.get('calories_per_100g', 0) * scale_factor,
                                'protein_g': nutrition.get('protein_per_100g', 0) * scale_factor,
                                'carbs_g': nutrition.get('carbs_per_100g', 0) * scale_factor,
                                'fat_g': nutrition.get('fat_per_100g', 0) * scale_factor,
                                'fiber_g': nutrition.get('fiber_per_100g', 0) * scale_factor,
                                'sugar_g': nutrition.get('sugar_per_100g', 0) * scale_factor,
                                'sodium_mg': nutrition.get('sodium_per_100g', 0) * scale_factor * 1000,
                                'source': result['title']
                            }
                            break
                    
                    # If no nutrition found in search, use estimates
                    if not candidate.get('nutrition'):
                        candidate['nutrition'] = parser.nutrition_search.get_nutrition_estimate(
                            candidate['name'], 
                            candidate.get('portion_grams', 100)
                        )
        
        # Update photo with analysis
        photo = Photo.query.get(photo_id)
        if photo:
            photo.set_analysis({'candidates': candidates, 'vision_items': vision_items, 'meta': meta})
            db.session.commit()
        
        current_app.logger.info(f"Analysis complete. Found {len(candidates)} food candidates")
        return candidates, meta
    
    except Exception as e:
        current_app.logger.error(f"Error analyzing photo: {e}")
        return [], {'source': None, 'warning': 'Unexpected error during analysis', 'errors': [str(e)]}


def _parse_vision_text_response(text_response):
    """Parse text response from vision model into structured food items"""
    items = []
    
    try:
        lines = text_response.strip().split('\n')
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for food mentions
            if any(keyword in line.lower() for keyword in ['food', 'dish', 'item', '1.', '2.', '3.', '-', '•']):
                # Save previous item if exists
                if current_item and current_item.get('name'):
                    items.append(current_item)
                
                # Extract food name
                # Remove common prefixes
                clean_line = re.sub(r'^[\d\.\-\•\s]*', '', line)
                clean_line = re.sub(r'(food|dish|item)[\s:]*', '', clean_line, flags=re.IGNORECASE)
                
                if clean_line:
                    current_item = {
                        'name': clean_line.split(',')[0].split('(')[0].strip(),
                        'portion': '100g',
                        'confidence': 0.7
                    }
            
            # Look for portion information
            elif current_item and ('gram' in line.lower() or 'portion' in line.lower() or 'size' in line.lower()):
                # Extract portion
                portion_match = re.search(r'(\d+)\s*(g|gram|grams)', line.lower())
                if portion_match:
                    current_item['portion'] = f"{portion_match.group(1)}g"
            
            # Look for confidence
            elif current_item and ('confidence' in line.lower() or 'sure' in line.lower()):
                conf_match = re.search(r'(\d+\.?\d*)%?', line)
                if conf_match:
                    conf = float(conf_match.group(1))
                    if conf > 1:
                        conf = conf / 100
                    current_item['confidence'] = min(1.0, max(0.0, conf))
        
        # Add the last item
        if current_item and current_item.get('name'):
            items.append(current_item)
        
        # If no structured items found, try to extract food names from the text
        if not items:
            # Look for common food words
            food_patterns = [
                r'(?:I see|I can see|visible|appears to be|looks like)\s+([^.]+)',
                r'(?:contains|includes|has)\s+([^.]+)',
                r'(?:chicken|beef|pork|fish|rice|pasta|bread|vegetable|fruit|salad|soup)\w*[^.]*'
            ]
            
            for pattern in food_patterns:
                matches = re.findall(pattern, text_response, re.IGNORECASE)
                for match in matches:
                    clean_match = match.strip().split(',')[0].split(' and')[0].strip()
                    if len(clean_match) > 3 and len(clean_match) < 50:
                        items.append({
                            'name': clean_match,
                            'portion': '100g',
                            'confidence': 0.6
                        })
                        if len(items) >= 3:  # Limit to 3 items
                            break
                if len(items) >= 3:
                    break
        
    except Exception as e:
        current_app.logger.error(f"Error parsing vision text: {e}")
        # Return at least one generic item so the system doesn't completely fail
        items = [{'name': 'Mixed Food', 'portion': '100g', 'confidence': 0.5}]
    
    return items[:5]  # Limit to 5 items max


def _build_coach_context(user_id):
    """Build comprehensive context for AI coach with all user data"""
    try:
        from models import Profile, WeighIn, WaterIntake
        from datetime import datetime, timedelta
        
        # Get user profile
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        # Get recent food logs (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_food_logs = FoodLog.query.filter_by(user_id=user_id)\
            .filter(FoodLog.logged_at >= week_ago)\
            .order_by(FoodLog.logged_at.desc())\
            .limit(20).all()
        
        # Get recent weight entries  
        recent_weigh_ins = WeighIn.query.filter_by(user_id=user_id)\
            .order_by(WeighIn.recorded_at.desc())\
            .limit(5).all()
        
        # Get conversation history for memory
        recent_messages = CoachMessage.query.filter_by(user_id=user_id)\
            .order_by(CoachMessage.created_at.desc())\
            .limit(20).all()
        
        # Build context with available data
        context = f"""
=== USER PROFILE ===
Name: {profile.name if profile else 'Unknown'}
Age: {profile.age if profile else 'Unknown'}
Sex: {profile.sex if profile else 'Unknown'}  
Height: {profile.height_cm if profile else 'Unknown'}cm
Current Weight: {profile.weight_kg if profile else 'Unknown'}kg
Target Weight: {profile.target_weight_kg if profile else 'Not set'}kg
Goal: {profile.goal_type if profile else 'Unknown'} ({profile.timeframe_weeks if profile else 'Unknown'} weeks)
Activity Level: {profile.activity_level if profile else 'Unknown'}

Dietary Preferences: {', '.join(profile.get_preferences()) if profile and hasattr(profile, 'get_preferences') and profile.get_preferences() else 'None specified'}
Food Allergies: {', '.join(profile.get_allergies()) if profile and hasattr(profile, 'get_allergies') and profile.get_allergies() else 'None specified'}
Kitchen Equipment: {', '.join(profile.get_equipment()) if profile and hasattr(profile, 'get_equipment') and profile.get_equipment() else 'None specified'}

=== RECENT WEIGHT PROGRESS ==="""
        
        if recent_weigh_ins:
            for weigh_in in recent_weigh_ins:
                context += f"\n{weigh_in.recorded_at.strftime('%Y-%m-%d')}: {weigh_in.weight_kg:.1f}kg"
            
            if len(recent_weigh_ins) >= 2:
                weight_change = recent_weigh_ins[0].weight_kg - recent_weigh_ins[-1].weight_kg
                context += f"\nRecent Weight Change: {weight_change:+.1f}kg"
        else:
            context += "\nNo recent weight entries"
            
        context += f"""

=== RECENT FOOD LOGS (Last 7 days) ==="""
        
        if recent_food_logs:
            for log in recent_food_logs:
                food_name = log.custom_name or (log.food_item.canonical_name if log.food_item else 'Unknown')
                context += f"\n{log.logged_at.strftime('%Y-%m-%d %H:%M')} - {log.meal}: {food_name} ({log.grams}g, {log.calories:.0f}cal)"
        else:
            context += "\nNo recent food logs"
            
        context += f"""

=== CONVERSATION MEMORY (Recent exchanges) ==="""
        
        if recent_messages:
            context += "\nRecent conversations:"
            # Reverse to show oldest first for context
            for msg in reversed(recent_messages[:10]):  # Last 10 messages
                role_label = "User" if msg.role == 'user' else "Assistant"
                context += f"\n{role_label}: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}"
        else:
            context += "\nNo previous conversations"
        
        return context
        
    except Exception as e:
        current_app.logger.error(f"Error building coach context: {e}")
        return f"User profile available with basic information. Recent error: {str(e)}"


def _get_default_system_prompt():
    """Get default system prompt for AI coach"""
    return """You are a supportive nutrition coach. Help users achieve their health goals through evidence-based guidance. 

Guidelines:
- Be encouraging and supportive
- Provide specific, actionable advice
- Reference the user's current nutrition data when relevant
- Suggest foods that fit their preferences and restrictions
- If asked for medical advice, recommend consulting a healthcare professional
- Keep responses concise and practical
- Use the nutrition search results when making food recommendations"""


# =============================================================================
# NOTIFICATION API ENDPOINTS
# =============================================================================






@api_bp.route('/notifications/read', methods=['POST'])
@login_required
def mark_multiple_notifications_read():
    """Mark multiple notifications as read"""
    try:
        data = request.get_json() or {}
        notification_ids = data.get('notification_ids', [])
        
        if not notification_ids:
            return jsonify({'error': 'No notification IDs provided'}), 400
        
        from services.notification_service import NotificationService
        
        count = NotificationService.mark_multiple_as_read(notification_ids, current_user.id)
        
        return jsonify({
            'message': f'Marked {count} notifications as read',
            'updated_count': count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error marking multiple notifications as read: {e}")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500




@api_bp.route('/notifications/<int:notification_id>/dismiss', methods=['POST'])
@login_required
def dismiss_notification(notification_id):
    """Dismiss a specific notification"""
    try:
        from services.notification_service import NotificationService
        
        success = NotificationService.dismiss_notification(notification_id, current_user.id)
        
        if success:
            return jsonify({'message': 'Notification dismissed'})
        else:
            return jsonify({'error': 'Notification not found'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error dismissing notification: {e}")
        return jsonify({'error': 'Failed to dismiss notification'}), 500


@api_bp.route('/notifications/test', methods=['POST'])
@login_required
def create_test_notification():
    """Create a test notification (for development/testing)"""
    try:
        data = request.get_json() or {}
        
        from services.notification_service import NotificationService
        
        notification = NotificationService.create_notification(
            user_id=current_user.id,
            title=data.get('title', 'Test Notification'),
            message=data.get('message', 'This is a test notification.'),
            notification_type=data.get('type', 'system'),
            category=data.get('category', 'test'),
            priority=data.get('priority', 'normal')
        )
        
        return jsonify({
            'message': 'Test notification created',
            'notification': notification.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating test notification: {e}")
        return jsonify({'error': 'Failed to create test notification'}), 500


# =============================================================================
# ADMIN API ENDPOINTS
# =============================================================================

def admin_required(f):
    """Decorator to require admin access for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/admin/users-list')
@login_required
@admin_required
def admin_users_list():
    """API endpoint for getting list of users"""
    try:
        users = User.query.filter_by(is_active=True).order_by(User.username).all()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'name': user.username,
                'email': user.username  # Using username as email for display
            })
        
        return jsonify({'users': users_data})
        
    except Exception as e:
        current_app.logger.error(f"Error getting users list: {e}")
        return jsonify({'error': 'Failed to get users list'}), 500


@api_bp.route('/admin/notification-templates')
@login_required
@admin_required
def admin_notification_templates():
    """API endpoint for getting notification templates"""
    try:
        templates = NotificationTemplate.query.filter_by(is_active=True).order_by(NotificationTemplate.name).all()
        
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'title_template': template.title_template,
                'message_template': template.message_template,
                'category': template.category,
                'priority': template.priority
            })
        
        return jsonify({'templates': templates_data})
        
    except Exception as e:
        current_app.logger.error(f"Error getting notification templates: {e}")
        return jsonify({'error': 'Failed to get notification templates'}), 500


@api_bp.route('/admin/send-notification', methods=['POST'])
@login_required
@admin_required
def admin_send_notification():
    """API endpoint for sending notifications from dashboard"""
    try:
        data = request.get_json()
        
        recipient_type = data.get('recipient_type')
        title = data.get('title', '').strip()
        message = data.get('message', '').strip()
        priority = data.get('priority', 'normal')
        template_id = data.get('template_id')
        user_id = data.get('user_id')
        
        if not title or not message:
            return jsonify({'success': False, 'message': 'Title and message are required'}), 400
        
        from services.notification_service import AdminNotificationService
        
        count = 0
        
        if recipient_type == 'specific' and user_id:
            # Send to specific user
            notification = AdminNotificationService.send_to_user(
                admin_user_id=current_user.id,
                target_user_id=int(user_id),
                title=title,
                message=message,
                priority=priority
            )
            if notification:
                count = 1
                
        elif recipient_type == 'all':
            # Send to all users
            users = User.query.filter_by(is_active=True).all()
            for user in users:
                notification = AdminNotificationService.send_to_user(
                    admin_user_id=current_user.id,
                    target_user_id=user.id,
                    title=title,
                    message=message,
                    priority=priority
                )
                if notification:
                    count += 1
                    
        elif recipient_type == 'active':
            # Send to active users only
            users = User.query.filter_by(is_active=True).all()
            for user in users:
                notification = AdminNotificationService.send_to_user(
                    admin_user_id=current_user.id,
                    target_user_id=user.id,
                    title=title,
                    message=message,
                    priority=priority
                )
                if notification:
                    count += 1
                    
        elif recipient_type == 'admin':
            # Send to admin users only
            users = User.query.filter_by(is_admin=True, is_active=True).all()
            for user in users:
                notification = AdminNotificationService.send_to_user(
                    admin_user_id=current_user.id,
                    target_user_id=user.id,
                    title=title,
                    message=message,
                    priority=priority
                )
                if notification:
                    count += 1
        
        # Log admin action (simplified for API)
        current_app.logger.info(f"Admin {current_user.username} sent notification '{title}' to {count} users")
        
        return jsonify({
            'success': True,
            'message': f'Notification sent to {count} users',
            'count': count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending notification via API: {e}")
        return jsonify({'success': False, 'message': 'Failed to send notification'}), 500


@api_bp.route('/admin/test-notification', methods=['POST'])
@login_required
@admin_required
def admin_test_notification():
    """API endpoint for sending test notifications"""
    try:
        from services.notification_service import AdminNotificationService
        
        # Send test notification to all admin users
        admin_users = User.query.filter_by(is_admin=True, is_active=True).all()
        count = 0
        
        for user in admin_users:
            notification = AdminNotificationService.send_to_user(
                admin_user_id=current_user.id,
                target_user_id=user.id,
                title="🧪 Test Notification",
                message="This is a test notification to verify the system is working properly. If you received this, the notification system is functioning correctly!",
                priority="normal"
            )
            if notification:
                count += 1
        
        current_app.logger.info(f"Admin {current_user.username} sent test notification to {count} admin users")
        
        return jsonify({
            'success': True,
            'message': f'Test notification sent to {count} admin users',
            'count': count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending test notification: {e}")
        return jsonify({'success': False, 'message': 'Failed to send test notification'}), 500


# Mobile Notifications API Endpoints
@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get notifications for the current user (mobile API)"""
    try:
        # Parse query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        current_app.logger.info(f"Mobile notifications request: user_id={current_user.id}, limit={limit}, offset={offset}, unread_only={unread_only}")
        
        # Build query
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Get notifications with pagination
        notifications = query.order_by(Notification.created_at.desc())\
                           .offset(offset)\
                           .limit(limit)\
                           .all()
        
        # Get total count
        total_query = Notification.query.filter_by(user_id=current_user.id)
        if unread_only:
            total_query = total_query.filter_by(is_read=False)
        total_count = total_query.count()
        
        # Get unread count
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        # Serialize notifications
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'category': notification.category,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
            })
        
        current_app.logger.info(f"Returning {len(notifications_data)} notifications, total_count={total_count}, unread_count={unread_count}")
        
        return jsonify({
            'success': True,
            'notifications': notifications_data,
            'total_count': total_count,
            'unread_count': unread_count,
            'has_more': len(notifications) == limit and (offset + limit) < total_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching notifications: {e}")
        return jsonify({'success': False, 'message': 'Failed to load notifications'}), 500


@api_bp.route('/notifications/counts', methods=['GET'])
@login_required
def get_notification_counts():
    """Get notification counts for the current user (mobile API)"""
    try:
        total_count = Notification.query.filter_by(user_id=current_user.id).count()
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'unread_count': unread_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching notification counts: {e}")
        return jsonify({'success': False, 'message': 'Failed to load notification counts'}), 500


@api_bp.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a specific notification as read (mobile API)"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {e}")
        return jsonify({'success': False, 'message': 'Failed to mark notification as read'}), 500


@api_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read for current user (mobile API)"""
    try:
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        count = 0
        for notification in unread_notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Marked {count} notifications as read',
            'count': count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error marking all notifications as read: {e}")
        return jsonify({'success': False, 'message': 'Failed to mark notifications as read'}), 500


@api_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """Delete a specific notification (mobile API)"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting notification: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete notification'}), 500