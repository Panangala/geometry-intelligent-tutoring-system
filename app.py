from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from functools import wraps
import logging
import os
import math
import random
from config import config
from modules.ontology_handler import initialize_ontology

app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ontology_handler = initialize_ontology(app.config['ONTOLOGY_PATH'])
logger.info("Ontology handler initialized successfully")

# LEVEL CONFIGURATION
LEVELS = {
    'beginner': {
        'name': 'Beginner',
        'description': 'Simple whole numbers, basic concepts',
        'questions_required': 5,
        'pass_threshold': 0.6,  # 60% to pass
        'color': '#10b981',
        'icon': '🌱'
    },
    'intermediate': {
        'name': 'Intermediate', 
        'description': 'Decimal numbers, medium difficulty',
        'questions_required': 5,
        'pass_threshold': 0.7,  # 70% to pass
        'color': '#f59e0b',
        'icon': '🌿'
    },
    'expert': {
        'name': 'Expert',
        'description': 'Complex calculations, real-world problems',
        'questions_required': 5,
        'pass_threshold': 0.8,  # 80% to pass
        'color': '#8b5cf6',
        'icon': '🌳'
    }
}

LEVEL_ORDER = ['beginner', 'intermediate', 'expert']

# AI Tutor responses
AI_TUTOR = {
    'correct': [
        {"message": "Excellent work! You've got it!", "emotion": "celebrating"},
        {"message": "Perfect! You're really understanding this!", "emotion": "happy"},
        {"message": "That's right! Keep up the great work!", "emotion": "thumbsup"},
        {"message": "Brilliant! You're a natural!", "emotion": "excited"},
        {"message": "Spot on! I knew you could do it!", "emotion": "proud"}
    ],
    'wrong': [
        {"message": "Not quite, but don't worry! Let's look at this together.", "emotion": "encouraging"},
        {"message": "Almost there! Check the formula and try again.", "emotion": "thinking"},
        {"message": "That's okay! Mistakes help us learn.", "emotion": "supportive"},
        {"message": "Let me help you understand this better.", "emotion": "helpful"},
        {"message": "No worries! Let's break this down step by step.", "emotion": "teaching"}
    ],
    'close': [
        {"message": "So close! Just a small calculation error.", "emotion": "encouraging"},
        {"message": "You're on the right track! Double-check your math.", "emotion": "thinking"}
    ],
    'level_up': [
        {"message": "AMAZING! You've mastered this level! Ready for the next challenge?", "emotion": "celebrating"},
        {"message": "Congratulations! You've leveled up! I'm so proud of you!", "emotion": "excited"}
    ],
    'level_complete': [
        {"message": "You've completed all levels for this shape! You're a geometry master!", "emotion": "proud"}
    ],
    'struggling': [
        {"message": "I can see this is tricky. Would you like to review the lesson?", "emotion": "supportive"},
        {"message": "Let's slow down and go through the basics again.", "emotion": "helpful"}
    ],
    'welcome': [
        {"message": "Hi! I'm Geo, your geometry tutor. Let's learn together!", "emotion": "waving"},
        {"message": "Welcome back! Ready to continue your learning journey?", "emotion": "happy"}
    ],
    'start_level': [
        {"message": "Let's start with the basics. You've got this!", "emotion": "encouraging"},
        {"message": "Time for a new challenge! I believe in you!", "emotion": "excited"},
        {"message": "Expert level! Show me what you've learned!", "emotion": "proud"}
    ]
}


def require_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def init_progress():
    """Initialize progress tracking in session if not exists."""
    if 'progress' not in session:
        session['progress'] = {
            'total_attempts': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'shapes': {
                'square': create_shape_progress(),
                'rectangle': create_shape_progress(),
                'triangle': create_shape_progress(),
                'circle': create_shape_progress()
            },
            'history': []
        }
        session.modified = True


def create_shape_progress():
    """Create initial progress structure for a shape."""
    return {
        'current_level': 'beginner',
        'levels': {
            'beginner': {'unlocked': True, 'attempts': 0, 'correct': 0, 'completed': False, 'questions': []},
            'intermediate': {'unlocked': False, 'attempts': 0, 'correct': 0, 'completed': False, 'questions': []},
            'expert': {'unlocked': False, 'attempts': 0, 'correct': 0, 'completed': False, 'questions': []}
        },
        'mastered': False
    }


def get_ai_response(category, level_index=0):
    """Get a random AI tutor response for a category."""
    responses = AI_TUTOR.get(category, AI_TUTOR['correct'])
    if category == 'start_level' and level_index < len(responses):
        return responses[level_index]
    return random.choice(responses)


def check_level_progress(shape, level):
    """Check if student should level up or needs help."""
    init_progress()
    progress = session['progress']
    level_data = progress['shapes'][shape]['levels'][level]
    level_config = LEVELS[level]
    
    result = {
        'can_advance': False,
        'level_complete': False,
        'needs_help': False,
        'attempts': level_data['attempts'],
        'correct': level_data['correct'],
        'required': level_config['questions_required'],
        'accuracy': 0,
        'threshold': level_config['pass_threshold']
    }
    
    if level_data['attempts'] > 0:
        result['accuracy'] = level_data['correct'] / level_data['attempts']
    
    # Check if enough questions answered
    if level_data['attempts'] >= level_config['questions_required']:
        if result['accuracy'] >= level_config['pass_threshold']:
            result['can_advance'] = True
            result['level_complete'] = True
        elif result['accuracy'] < 0.4:
            result['needs_help'] = True
    
    # Check if struggling (3+ wrong in a row)
    recent = level_data['questions'][-3:] if len(level_data['questions']) >= 3 else []
    if len(recent) == 3 and all(not q['correct'] for q in recent):
        result['needs_help'] = True
    
    return result


def advance_level(shape):
    """Advance student to next level for a shape."""
    init_progress()
    progress = session['progress']
    current_level = progress['shapes'][shape]['current_level']
    current_index = LEVEL_ORDER.index(current_level)
    
    # Mark current level as completed
    progress['shapes'][shape]['levels'][current_level]['completed'] = True
    
    if current_index < len(LEVEL_ORDER) - 1:
        # Advance to next level
        next_level = LEVEL_ORDER[current_index + 1]
        progress['shapes'][shape]['current_level'] = next_level
        progress['shapes'][shape]['levels'][next_level]['unlocked'] = True
        session['progress'] = progress
        session.modified = True
        return {'advanced': True, 'new_level': next_level, 'shape_mastered': False}
    else:
        # Shape mastered!
        progress['shapes'][shape]['mastered'] = True
        session['progress'] = progress
        session.modified = True
        return {'advanced': False, 'new_level': None, 'shape_mastered': True}


def generate_question(shape, level='beginner'):
    """Generate a question based on shape and difficulty level."""
    
    if level == 'beginner':
        # Whole numbers, simple calculations
        ranges = {'min': 2, 'max': 10}
        decimal_places = 0
        context = None
    elif level == 'intermediate':
        # Decimals, medium complexity
        ranges = {'min': 3, 'max': 15}
        decimal_places = 1
        context = None
    else:  # expert
        # Real-world problems, complex numbers
        ranges = {'min': 5, 'max': 25}
        decimal_places = 2
        context = get_real_world_context(shape)
    
    if shape == 'square':
        side = round(random.uniform(ranges['min'], ranges['max']), decimal_places)
        if decimal_places == 0:
            side = int(side)
        
        if context:
            problem = f"{context['setup']} The {context['object']} is square-shaped with sides of {side} {context['unit']}. {context['question']}"
        else:
            problem = f"A square has sides of {side} cm. Calculate its area."
        
        return {
            'problem': problem,
            'given': {'side': side},
            'correct_answer': side ** 2,
            'shape': shape,
            'level': level,
            'formula': f'A = s² = {side}² = {side**2:.2f}',
            'hint': f'Area of square = side × side = {side} × {side}',
            'steps': [
                f'Step 1: Identify the side length: s = {side}',
                f'Step 2: Apply the formula: A = s²',
                f'Step 3: Calculate: A = {side} × {side} = {side**2:.2f}'
            ]
        }
    
    elif shape == 'rectangle':
        length = round(random.uniform(ranges['min'], ranges['max']), decimal_places)
        width = round(random.uniform(ranges['min'], ranges['max'] * 0.7), decimal_places)
        if decimal_places == 0:
            length, width = int(length), int(width)
        
        if context:
            problem = f"{context['setup']} The {context['object']} is {length} {context['unit']} long and {width} {context['unit']} wide. {context['question']}"
        else:
            problem = f"A rectangle has length {length} cm and width {width} cm. Calculate its area."
        
        area = length * width
        return {
            'problem': problem,
            'given': {'length': length, 'width': width},
            'correct_answer': area,
            'shape': shape,
            'level': level,
            'formula': f'A = l × w = {length} × {width} = {area:.2f}',
            'hint': f'Area of rectangle = length × width = {length} × {width}',
            'steps': [
                f'Step 1: Identify length = {length}, width = {width}',
                f'Step 2: Apply the formula: A = l × w',
                f'Step 3: Calculate: A = {length} × {width} = {area:.2f}'
            ]
        }
    
    elif shape == 'triangle':
        base = round(random.uniform(ranges['min'], ranges['max']), decimal_places)
        height = round(random.uniform(ranges['min'], ranges['max'] * 0.8), decimal_places)
        if decimal_places == 0:
            base, height = int(base), int(height)
        
        if context:
            problem = f"{context['setup']} The {context['object']} has a base of {base} {context['unit']} and height of {height} {context['unit']}. {context['question']}"
        else:
            problem = f"A triangle has base {base} cm and height {height} cm. Calculate its area."
        
        area = (base * height) / 2
        return {
            'problem': problem,
            'given': {'base': base, 'height': height},
            'correct_answer': area,
            'shape': shape,
            'level': level,
            'formula': f'A = ½ × b × h = ½ × {base} × {height} = {area:.2f}',
            'hint': f'Area of triangle = ½ × base × height = ½ × {base} × {height}',
            'steps': [
                f'Step 1: Identify base = {base}, height = {height}',
                f'Step 2: Apply the formula: A = ½ × b × h',
                f'Step 3: Calculate: A = ½ × {base} × {height} = {area:.2f}'
            ]
        }
    
    elif shape == 'circle':
        radius = round(random.uniform(ranges['min'] * 0.5, ranges['max'] * 0.5), decimal_places)
        if decimal_places == 0:
            radius = int(radius)
        
        if context:
            problem = f"{context['setup']} The {context['object']} has a radius of {radius} {context['unit']}. {context['question']}"
        else:
            problem = f"A circle has radius {radius} cm. Calculate its area. (Use π = 3.14159)"
        
        area = math.pi * (radius ** 2)
        return {
            'problem': problem,
            'given': {'radius': radius},
            'correct_answer': area,
            'shape': shape,
            'level': level,
            'formula': f'A = π × r² = 3.14159 × {radius}² = {area:.2f}',
            'hint': f'Area of circle = π × radius² = 3.14159 × {radius}²',
            'steps': [
                f'Step 1: Identify radius = {radius}',
                f'Step 2: Apply the formula: A = π × r²',
                f'Step 3: Calculate: A = 3.14159 × {radius}² = {area:.2f}'
            ]
        }
    
    return None


def get_real_world_context(shape):
    """Get real-world problem context for expert level."""
    contexts = {
        'square': [
            {'setup': 'You are tiling a kitchen floor.', 'object': 'floor', 'unit': 'meters', 'question': 'How many square meters of tiles do you need?'},
            {'setup': 'A farmer is fencing a square garden.', 'object': 'garden', 'unit': 'meters', 'question': 'What is the area of the garden?'},
            {'setup': 'An artist is creating a square canvas.', 'object': 'canvas', 'unit': 'cm', 'question': 'What is the painting area?'}
        ],
        'rectangle': [
            {'setup': 'You are painting a bedroom wall.', 'object': 'wall', 'unit': 'meters', 'question': 'How much area needs to be painted?'},
            {'setup': 'A school is building a rectangular playground.', 'object': 'playground', 'unit': 'meters', 'question': 'What is the total area?'},
            {'setup': 'You need carpet for a living room.', 'object': 'room', 'unit': 'meters', 'question': 'How many square meters of carpet do you need?'}
        ],
        'triangle': [
            {'setup': 'A sail for a boat is triangular.', 'object': 'sail', 'unit': 'meters', 'question': 'What is the area of fabric needed?'},
            {'setup': 'You are designing a triangular garden bed.', 'object': 'garden bed', 'unit': 'meters', 'question': 'What is the planting area?'},
            {'setup': 'A road sign is triangular.', 'object': 'sign', 'unit': 'cm', 'question': 'What is the surface area of the sign?'}
        ],
        'circle': [
            {'setup': 'You are ordering a pizza.', 'object': 'pizza', 'unit': 'cm', 'question': 'What is the area of the pizza?'},
            {'setup': 'A sprinkler waters a circular area.', 'object': 'watered area', 'unit': 'meters', 'question': 'What area does it cover?'},
            {'setup': 'You are building a circular pond.', 'object': 'pond', 'unit': 'meters', 'question': 'What is the surface area?'}
        ]
    }
    return random.choice(contexts.get(shape, contexts['square']))


def get_lesson(shape):
    """Get lesson content for a shape."""
    data = ontology_handler.get_shape_definition(shape)
    examples = []
    
    for i in range(2):
        if shape == 'square':
            s = round(random.uniform(2, 5), 1)
            examples.append({
                'problem': f'Side: {s} cm',
                'solution': f'A = {s}² = {s**2:.2f} cm²',
                'steps': [f'Identify side = {s}', f'Apply A = s²', f'Calculate: {s} × {s} = {s**2:.2f}']
            })
        elif shape == 'rectangle':
            l, w = round(random.uniform(3, 6), 1), round(random.uniform(2, 5), 1)
            examples.append({
                'problem': f'{l} × {w} cm',
                'solution': f'A = {l*w:.2f} cm²',
                'steps': [f'Identify l = {l}, w = {w}', f'Apply A = l × w', f'Calculate: {l} × {w} = {l*w:.2f}']
            })
        elif shape == 'triangle':
            b, h = round(random.uniform(3, 6), 1), round(random.uniform(2, 5), 1)
            examples.append({
                'problem': f'Base {b}, height {h}',
                'solution': f'A = {(b*h)/2:.2f} cm²',
                'steps': [f'Identify b = {b}, h = {h}', f'Apply A = ½bh', f'Calculate: ½ × {b} × {h} = {(b*h)/2:.2f}']
            })
        elif shape == 'circle':
            r = round(random.uniform(1, 4), 1)
            examples.append({
                'problem': f'Radius {r} cm',
                'solution': f'A = {math.pi * r**2:.2f} cm²',
                'steps': [f'Identify r = {r}', f'Apply A = πr²', f'Calculate: 3.14159 × {r}² = {math.pi * r**2:.2f}']
            })
    
    return {
        'shape_name': shape,
        'introduction': data.get('description', ''),
        'properties': data.get('properties', []),
        'formula': data.get('formula', {}),
        'examples': examples,
        'learning_concepts': data.get('learning_concepts', [])
    }


def update_progress(shape, level, is_correct, question_data):
    """Update progress after answer submission."""
    init_progress()
    progress = session['progress']
    
    # Update global stats
    progress['total_attempts'] += 1
    if is_correct:
        progress['correct_answers'] += 1
    else:
        progress['wrong_answers'] += 1
    
    # Update shape-level stats
    level_data = progress['shapes'][shape]['levels'][level]
    level_data['attempts'] += 1
    if is_correct:
        level_data['correct'] += 1
    
    # Record question result
    level_data['questions'].append({
        'correct': is_correct,
        'question': question_data.get('problem', ''),
        'user_answer': question_data.get('user_answer', 0),
        'correct_answer': question_data.get('correct_answer', 0)
    })
    
    # Keep only last 20 questions per level
    if len(level_data['questions']) > 20:
        level_data['questions'] = level_data['questions'][-20:]
    
    # Add to history
    progress['history'].append({
        'shape': shape,
        'level': level,
        'correct': is_correct
    })
    if len(progress['history']) > 50:
        progress['history'] = progress['history'][-50:]
    
    session['progress'] = progress
    session.modified = True
    
    return progress


def get_progress_data():
    """Get formatted progress data for display."""
    init_progress()
    progress = session['progress']
    
    # Calculate overall accuracy
    accuracy = 0
    if progress['total_attempts'] > 0:
        accuracy = round((progress['correct_answers'] / progress['total_attempts']) * 100, 1)
    
    # Build shape progress
    shapes_data = {}
    shapes_mastered = 0
    
    for shape, data in progress['shapes'].items():
        levels_data = {}
        for level, level_info in data['levels'].items():
            level_accuracy = 0
            if level_info['attempts'] > 0:
                level_accuracy = round((level_info['correct'] / level_info['attempts']) * 100)
            
            levels_data[level] = {
                'unlocked': level_info['unlocked'],
                'completed': level_info['completed'],
                'attempts': level_info['attempts'],
                'correct': level_info['correct'],
                'accuracy': level_accuracy,
                'config': LEVELS[level]
            }
        
        shapes_data[shape] = {
            'current_level': data['current_level'],
            'mastered': data['mastered'],
            'levels': levels_data
        }
        
        if data['mastered']:
            shapes_mastered += 1
    
    return {
        'accuracy': accuracy,
        'total_attempts': progress['total_attempts'],
        'correct_answers': progress['correct_answers'],
        'wrong_answers': progress['wrong_answers'],
        'shapes': shapes_data,
        'shapes_mastered': shapes_mastered,
        'history': progress.get('history', [])[-10:]
    }


# ============== ROUTES ==============

@app.route('/')
def index():
    if 'student_id' not in session:
        session['student_id'] = os.urandom(16).hex()
        init_progress()
        logger.info(f"New session: {session['student_id']}")
    
    ai_greeting = get_ai_response('welcome')
    return render_template('index.html', ai_tutor=ai_greeting)


@app.route('/start')
def start():
    if 'student_id' not in session:
        return redirect(url_for('index'))
    init_progress()
    shapes = ontology_handler.get_all_shapes()
    progress = get_progress_data()
    return render_template('shape_select.html', shapes=shapes, progress=progress)


@app.route('/learn/<shape_name>')
@require_session
def learn(shape_name):
    lesson = get_lesson(shape_name)
    session['current_shape'] = shape_name
    progress = get_progress_data()
    return render_template('learn.html', lesson=lesson, shape=shape_name, progress=progress, levels=LEVELS)


@app.route('/practice/<shape_name>')
@require_session
def practice(shape_name):
    init_progress()
    progress = session['progress']
    
    # Get current level for this shape
    current_level = progress['shapes'][shape_name]['current_level']
    level_config = LEVELS[current_level]
    level_index = LEVEL_ORDER.index(current_level)
    
    # Generate question for current level
    question = generate_question(shape_name, current_level)
    session['current_question'] = question
    session.modified = True
    
    # Get AI tutor message
    ai_message = get_ai_response('start_level', level_index)
    
    # Get level progress
    level_progress = check_level_progress(shape_name, current_level)
    
    return render_template('practice.html', 
                         question=question, 
                         shape=shape_name, 
                         level=current_level,
                         level_config=level_config,
                         level_progress=level_progress,
                         ai_tutor=ai_message,
                         levels=LEVELS)


@app.route('/api/submit-answer', methods=['POST'])
@require_session
def submit_answer():
    try:
        data = request.get_json()
        user_answer = float(data['user_answer'])
        question = session.get('current_question')
        
        if not question:
            return jsonify({'error': 'No active question'}), 400
        
        correct = question['correct_answer']
        shape = question['shape']
        level = question['level']
        error = abs(user_answer - correct) / correct if correct != 0 else abs(user_answer - correct)
        
        is_correct = error <= 0.02  # 2% tolerance
        is_close = error <= 0.10 and not is_correct  # Within 10%
        
        # Update progress
        question['user_answer'] = user_answer
        progress = update_progress(shape, level, is_correct, question)
        
        # Check level progress
        level_status = check_level_progress(shape, level)
        
        # Determine AI response
        level_up_data = None
        if is_correct:
            if level_status['can_advance']:
                # Student passed the level!
                advance_result = advance_level(shape)
                if advance_result['shape_mastered']:
                    ai_response = get_ai_response('level_complete')
                else:
                    ai_response = get_ai_response('level_up')
                level_up_data = advance_result
            else:
                ai_response = get_ai_response('correct')
        elif is_close:
            ai_response = get_ai_response('close')
        elif level_status['needs_help']:
            ai_response = get_ai_response('struggling')
        else:
            ai_response = get_ai_response('wrong')
        
        # Build response
        response = {
            'is_correct': is_correct,
            'is_close': is_close,
            'correct_answer': round(correct, 2),
            'user_answer': round(user_answer, 2),
            'formula': question.get('formula', ''),
            'steps': question.get('steps', []),
            'ai_tutor': ai_response,
            'level_status': level_status,
            'level_up': level_up_data,
            'progress': {
                'level': level,
                'level_attempts': level_status['attempts'],
                'level_correct': level_status['correct'],
                'level_required': level_status['required'],
                'level_accuracy': round(level_status['accuracy'] * 100, 1),
                'total_attempts': progress['total_attempts'],
                'total_correct': progress['correct_answers']
            }
        }
        
        logger.info(f"Answer for {shape}/{level}: {'correct' if is_correct else 'wrong'}")
        return jsonify(response), 200
        
    except ValueError as e:
        logger.error(f"Invalid answer: {e}")
        return jsonify({'error': 'Please enter a valid number'}), 400
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress')
@require_session
def get_progress():
    """API endpoint to get current progress."""
    try:
        progress = get_progress_data()
        return jsonify(progress), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/shape-progress/<shape_name>')
@require_session
def get_shape_progress(shape_name):
    """Get detailed progress for a specific shape."""
    try:
        progress = get_progress_data()
        shape_data = progress['shapes'].get(shape_name)
        if shape_data:
            return jsonify(shape_data), 200
        return jsonify({'error': 'Shape not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results')
@require_session
def results():
    """Results/Progress page."""
    progress = get_progress_data()
    return render_template('results.html', progress=progress, levels=LEVELS)


@app.route('/reset')
def reset():
    """Reset all progress."""
    session.clear()
    logger.info("Session cleared")
    return redirect(url_for('index'))


@app.route('/reset-shape/<shape_name>')
@require_session
def reset_shape(shape_name):
    """Reset progress for a specific shape."""
    init_progress()
    if shape_name in session['progress']['shapes']:
        session['progress']['shapes'][shape_name] = create_shape_progress()
        session.modified = True
    return redirect(url_for('practice', shape_name=shape_name))


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return render_template('error.html', error='Server error'), 500


if __name__ == '__main__':
    logger.info("Starting Geometry ITS with Level System")

    app.run(host='127.0.0.1', port=5000, debug=True)
