"""
Learning Engine Module

This module implements the core tutoring system logic including:
- Student progress tracking
- Question generation based on ontology
- Difficulty adaptation
- Performance assessment
- Feedback generation
"""

from typing import Dict, List, Optional, Tuple
import random
import math
import logging

logger = logging.getLogger(__name__)


class LearningEngine:
    """Core tutoring system engine for geometry learning."""
    
    def __init__(self, ontology_handler):
        """
        Initialize learning engine with ontology handler.
        
        Args:
            ontology_handler: OntologyHandler instance for accessing ontology
        """
        self.ontology = ontology_handler
        self.student_session = {}
        self.difficulty_levels = ['easy', 'medium', 'hard']
    
    def initialize_student_session(self, student_id: str) -> Dict:
        """
        Create new student session for tracking progress.
        
        Args:
            student_id (str): Unique identifier for student
            
        Returns:
            Dict: Initialized session object
        """
        session = {
            'student_id': student_id,
            'current_shape': None,
            'current_lesson_stage': 'introduction',
            'difficulty': 'easy',
            'attempts': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'shape_progress': {shape: {'completed': False, 'score': 0} 
                               for shape in self.ontology.get_all_shapes()}
        }
        self.student_session = session
        return session
    
    def get_shape_lesson(self, shape_name: str) -> Dict:
        """
        Generate comprehensive lesson for a shape.
        
        Args:
            shape_name (str): Name of shape to learn
            
        Returns:
            Dict: Complete lesson structure
        """
        shape_data = self.ontology.get_shape_definition(shape_name)
        
        lesson = {
            'shape_name': shape_name,
            'introduction': self._generate_introduction(shape_data),
            'properties': shape_data.get('properties', []),
            'formula': shape_data.get('formula', {}),
            'examples': self._generate_examples(shape_name, difficulty='easy'),
            'learning_concepts': shape_data.get('learning_concepts', [])
        }
        
        self.student_session['current_shape'] = shape_name
        self.student_session['current_lesson_stage'] = 'learning'
        
        return lesson
    
    def _generate_introduction(self, shape_data: Dict) -> str:
        """
        Generate introductory text for shape lesson.
        
        Args:
            shape_data (Dict): Shape information from ontology
            
        Returns:
            str: Introduction text
        """
        shape_name = shape_data.get('name', 'Unknown')
        description = shape_data.get('description', '')
        
        intro = f"""
Welcome to learning about {shape_name.capitalize()}!

{description}

In this lesson, you will:
1. Understand the key properties of a {shape_name}
2. Learn the formula to calculate its area
3. Practice solving area problems
4. Apply your knowledge to word problems

Let's get started!
        """
        return intro.strip()
    
    def _generate_examples(self, shape_name: str, difficulty: str = 'easy', 
                          count: int = 3) -> List[Dict]:
        """
        Generate worked examples for a shape based on difficulty.
        
        Args:
            shape_name (str): Name of shape
            difficulty (str): Difficulty level (easy, medium, hard)
            count (int): Number of examples to generate
            
        Returns:
            List[Dict]: Worked examples with solutions
        """
        examples = []
        
        if shape_name.lower() == 'square':
            ranges = {'easy': (1, 5), 'medium': (5, 10), 'hard': (10, 20)}
            min_val, max_val = ranges.get(difficulty, (1, 5))
            
            for _ in range(count):
                side = random.uniform(min_val, max_val)
                area = side ** 2
                examples.append({
                    'problem': f'A square has a side length of {side:.1f} cm. What is its area?',
                    'given': {'side': side},
                    'solution': f'Area = side² = {side:.1f}² = {area:.2f} cm²',
                    'answer': area
                })
        
        elif shape_name.lower() == 'rectangle':
            ranges = {'easy': (2, 6), 'medium': (5, 12), 'hard': (8, 20)}
            min_val, max_val = ranges.get(difficulty, (2, 6))
            
            for _ in range(count):
                length = random.uniform(min_val, max_val)
                width = random.uniform(min_val, max_val)
                area = length * width
                examples.append({
                    'problem': f'A rectangle has length {length:.1f} cm and width {width:.1f} cm. What is its area?',
                    'given': {'length': length, 'width': width},
                    'solution': f'Area = length × width = {length:.1f} × {width:.1f} = {area:.2f} cm²',
                    'answer': area
                })
        
        elif shape_name.lower() == 'triangle':
            ranges = {'easy': (2, 6), 'medium': (4, 10), 'hard': (6, 15)}
            min_val, max_val = ranges.get(difficulty, (2, 6))
            
            for _ in range(count):
                base = random.uniform(min_val, max_val)
                height = random.uniform(min_val, max_val)
                area = (base * height) / 2
                examples.append({
                    'problem': f'A triangle has a base of {base:.1f} cm and height of {height:.1f} cm. What is its area?',
                    'given': {'base': base, 'height': height},
                    'solution': f'Area = (base × height) / 2 = ({base:.1f} × {height:.1f}) / 2 = {area:.2f} cm²',
                    'answer': area
                })
        
        elif shape_name.lower() == 'circle':
            ranges = {'easy': (1, 3), 'medium': (2, 5), 'hard': (3, 8)}
            min_val, max_val = ranges.get(difficulty, (1, 3))
            
            for _ in range(count):
                radius = random.uniform(min_val, max_val)
                area = math.pi * (radius ** 2)
                examples.append({
                    'problem': f'A circle has a radius of {radius:.1f} cm. What is its area?',
                    'given': {'radius': radius},
                    'solution': f'Area = π × r² = 3.14159 × {radius:.1f}² = {area:.2f} cm²',
                    'answer': area
                })
        
        return examples
    
    def generate_practice_question(self, shape_name: str) -> Dict:
        """
        Generate practice question for student.
        
        Args:
            shape_name (str): Name of shape to practice
            
        Returns:
            Dict: Practice question with answer
        """
        difficulty = self.student_session.get('difficulty', 'easy')
        
        examples = self._generate_examples(shape_name, difficulty, count=1)
        if not examples:
            return {}
        
        example = examples[0]
        
        question = {
            'problem': example['problem'],
            'given': example['given'],
            'correct_answer': example['answer'],
            'shape': shape_name,
            'difficulty': difficulty
        }
        
        return question
    
    def evaluate_answer(self, user_answer: float, correct_answer: float) -> Tuple[bool, str, float]:
        """
        Evaluate student's answer and provide feedback.
        
        Args:
            user_answer (float): Student's submitted answer
            correct_answer (float): Correct answer
            
        Returns:
            Tuple: (is_correct, feedback, score)
        """
        is_correct, feedback = self.ontology.validate_answer(
            self.student_session.get('current_shape', ''),
            user_answer,
            correct_answer,
            tolerance=0.02
        )
        
        score = 1.0 if is_correct else 0.0
        
        if is_correct:
            self.student_session['correct_answers'] += 1
        else:
            self.student_session['wrong_answers'] += 1
        
        self.student_session['attempts'] += 1
        
        return is_correct, feedback, score
    
    def adapt_difficulty(self):
        """
        Adapt difficulty based on student performance.
        Updates difficulty level in session based on recent performance.
        """
        total_attempts = self.student_session['attempts']
        
        if total_attempts == 0:
            return
        
        success_rate = self.student_session['correct_answers'] / total_attempts
        current_difficulty = self.student_session['difficulty']
        
        if success_rate > 0.8 and current_difficulty != 'hard':
            self.student_session['difficulty'] = 'hard'
            logger.info(f"Difficulty increased to hard for student {self.student_session['student_id']}")
        elif success_rate < 0.5 and current_difficulty != 'easy':
            self.student_session['difficulty'] = 'easy'
            logger.info(f"Difficulty decreased to easy for student {self.student_session['student_id']}")
        elif 0.5 <= success_rate <= 0.8 and current_difficulty != 'medium':
            self.student_session['difficulty'] = 'medium'
            logger.info(f"Difficulty set to medium for student {self.student_session['student_id']}")
    
    def get_student_progress(self) -> Dict:
        """
        Calculate and return student's overall progress.
        
        Returns:
            Dict: Student progress metrics
        """
        total_attempts = self.student_session['attempts']
        
        if total_attempts == 0:
            return {
                'accuracy': 0,
                'total_attempts': 0,
                'shapes_completed': 0,
                'next_shape': 'square'
            }
        
        accuracy = (self.student_session['correct_answers'] / total_attempts) * 100
        shapes_completed = sum(1 for shape in self.student_session['shape_progress'].values() 
                              if shape['completed'])
        
        progress = {
            'accuracy': round(accuracy, 2),
            'total_attempts': total_attempts,
            'correct_answers': self.student_session['correct_answers'],
            'wrong_answers': self.student_session['wrong_answers'],
            'shapes_completed': shapes_completed,
            'current_difficulty': self.student_session['difficulty'],
            'shape_progress': self.student_session['shape_progress']
        }
        
        return progress
    
    def mark_shape_completed(self, shape_name: str, score: float):
        """
        Mark a shape as completed in student's progress.
        
        Args:
            shape_name (str): Name of completed shape
            score (float): Final score for shape (0-100)
        """
        if shape_name in self.student_session['shape_progress']:
            self.student_session['shape_progress'][shape_name]['completed'] = True
            self.student_session['shape_progress'][shape_name]['score'] = score
            logger.info(f"Student {self.student_session['student_id']} completed {shape_name} with score {score}")