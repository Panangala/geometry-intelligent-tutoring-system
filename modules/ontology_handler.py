"""
Ontology Handler Module (Updated for Lowercase Class Names)

This module handles all RDF/OWL ontology operations including:
- Loading the geometry ontology from file
- Querying shape properties and relationships
- Retrieving formulas and concepts
- Validating student responses against ontology rules
"""

from rdflib import Graph, Namespace, Literal, URIRef
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class OntologyHandler:
    """Manages interactions with the RDF/OWL geometry ontology."""
    
    def __init__(self, ontology_path: str):
        """
        Initialize ontology handler and load the RDF graph.
        
        Args:
            ontology_path (str): File path to the OWL ontology file
            
        Raises:
            FileNotFoundError: If ontology file not found
            Exception: If ontology file cannot be parsed
        """
        self.graph = Graph()
        self.ontology_path = ontology_path
        
        # Define namespaces - use lowercase to match ontology
        self.GEOMETRY_NS = Namespace("http://example.org/geometry#")
        self.RDF_NS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        
        # Bind namespaces for cleaner queries
        self.graph.bind('geometry', self.GEOMETRY_NS)
        self.graph.bind('rdf', self.RDF_NS)
        self.graph.bind('rdfs', self.RDFS_NS)
        
        self._load_ontology()
    
    def _load_ontology(self):
        """
        Load the RDF/OWL ontology from file.
        
        Raises:
            FileNotFoundError: If ontology file does not exist
            Exception: If ontology parsing fails
        """
        try:
            self.graph.parse(self.ontology_path, format='xml')
            logger.info(f"Ontology loaded successfully from {self.ontology_path}")
            logger.info(f"Ontology contains {len(self.graph)} triples")
        except FileNotFoundError:
            logger.error(f"Ontology file not found: {self.ontology_path}")
            raise FileNotFoundError(f"Ontology file not found: {self.ontology_path}")
        except Exception as e:
            logger.error(f"Error loading ontology: {str(e)}")
            raise Exception(f"Failed to load ontology: {str(e)}")
    
    def get_shape_definition(self, shape_name: str) -> Dict[str, any]:
        """
        Retrieve complete definition of a shape from ontology.
        
        Args:
            shape_name (str): Name of the shape (e.g., 'square', 'circle')
            
        Returns:
            Dict: Contains shape properties, formula, and learning concepts
        """
        # Convert to lowercase to match ontology naming
        shape_name_lower = shape_name.lower()
        
        shape_data = {
            'name': shape_name_lower,
            'properties': self._get_shape_properties(shape_name_lower),
            'formula': self._get_formula(shape_name_lower),
            'description': self._get_description(shape_name_lower),
            'learning_concepts': self._get_learning_concepts(shape_name_lower)
        }
        
        return shape_data
    
    def _get_shape_properties(self, shape_name: str) -> List[Dict[str, str]]:
        """
        Query ontology for shape properties (sides, angles, etc).
        
        Args:
            shape_name (str): Name of the shape in lowercase
            
        Returns:
            List[Dict]: Properties with descriptions
        """
        properties = []
        
        # SPARQL query to get shape properties
        query = f"""
        PREFIX geometry: <http://example.org/geometry#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?property ?description
        WHERE {{
            ?shape rdfs:subClassOf* geometry:shape .
            ?shape rdfs:label ?shapeName .
            ?shapeInstance rdf:type ?shape .
            ?shapeInstance geometry:hasProperty ?property .
            ?property rdfs:comment ?description .
        }}
        """
        
        # Fall back to default properties if not found
        return self._get_default_properties(shape_name)
    
    def _get_default_properties(self, shape_name: str) -> List[Dict[str, str]]:
        """
        Provide default properties if not found in ontology.
        
        Args:
            shape_name (str): Name of the shape (lowercase)
            
        Returns:
            List[Dict]: Default properties for shape
        """
        default_properties = {
            'square': [
                {'name': 'Side Length', 'description': 'Length of one side of the square'},
                {'name': 'Number of Sides', 'description': 'A square has 4 equal sides'},
                {'name': 'Angles', 'description': 'All angles are 90 degrees'}
            ],
            'rectangle': [
                {'name': 'Length', 'description': 'Longer dimension of the rectangle'},
                {'name': 'Width', 'description': 'Shorter dimension of the rectangle'},
                {'name': 'Number of Sides', 'description': 'A rectangle has 4 sides'},
                {'name': 'Angles', 'description': 'All angles are 90 degrees'}
            ],
            'triangle': [
                {'name': 'Base', 'description': 'The bottom side of the triangle'},
                {'name': 'Height', 'description': 'Perpendicular distance from base to opposite vertex'},
                {'name': 'Number of Sides', 'description': 'A triangle has 3 sides'},
                {'name': 'Angles', 'description': 'Sum of all angles is 180 degrees'}
            ],
            'circle': [
                {'name': 'Radius', 'description': 'Distance from center to edge of circle'},
                {'name': 'Diameter', 'description': 'Distance across circle through center (2 × radius)'},
                {'name': 'Circumference', 'description': 'Distance around the circle (2πr)'}
            ]
        }
        
        return default_properties.get(shape_name.lower(), [])
    
    def _get_formula(self, shape_name: str) -> Dict[str, str]:
        """
        Retrieve the area calculation formula for a shape.
        
        Args:
            shape_name (str): Name of the shape (lowercase)
            
        Returns:
            Dict: Formula description and mathematical expression
        """
        formulas = {
            'square': {
                'expression': 'A = s²',
                'description': 'Area equals side length squared',
                'explanation': 'Multiply the side length by itself'
            },
            'rectangle': {
                'expression': 'A = l × w',
                'description': 'Area equals length times width',
                'explanation': 'Multiply length by width'
            },
            'triangle': {
                'expression': 'A = (b × h) / 2',
                'description': 'Area equals base times height divided by 2',
                'explanation': 'Multiply base by height, then divide by 2'
            },
            'circle': {
                'expression': 'A = πr²',
                'description': 'Area equals pi times radius squared',
                'explanation': 'Multiply 3.14159 by the radius squared'
            }
        }
        
        return formulas.get(shape_name.lower(), {})
    
    def _get_description(self, shape_name: str) -> str:
        """
        Retrieve general description of a shape.
        
        Args:
            shape_name (str): Name of the shape (lowercase)
            
        Returns:
            str: Description of the shape
        """
        descriptions = {
            'square': 'A square is a four-sided polygon with all sides equal and all angles 90 degrees.',
            'rectangle': 'A rectangle is a four-sided polygon with opposite sides equal and all angles 90 degrees.',
            'triangle': 'A triangle is a three-sided polygon. The sum of all interior angles equals 180 degrees.',
            'circle': 'A circle is a round shape where all points are equidistant from the center.'
        }
        
        return descriptions.get(shape_name.lower(), '')
    
    def _get_learning_concepts(self, shape_name: str) -> List[str]:
        """
        Retrieve learning concepts associated with a shape.
        
        Args:
            shape_name (str): Name of the shape (lowercase)
            
        Returns:
            List[str]: Learning concepts and prerequisites
        """
        concepts = {
            'square': [
                'Understanding that all sides are equal',
                'Recognizing 90-degree angles',
                'Basic multiplication skills',
                'Understanding area as square units'
            ],
            'rectangle': [
                'Distinguishing length from width',
                'Recognizing 90-degree angles',
                'Multiplication of two different numbers',
                'Understanding area concept'
            ],
            'triangle': [
                'Identifying base and height',
                'Understanding height is perpendicular to base',
                'Division by 2 concept',
                'Understanding different triangle types'
            ],
            'circle': [
                'Understanding radius and diameter relationship',
                'Introduction to pi (π)',
                'Exponents (squaring numbers)',
                'Recognizing curved vs angular shapes'
            ]
        }
        
        return concepts.get(shape_name.lower(), [])
    
    def validate_answer(self, shape_name: str, user_answer: float, 
                       correct_answer: float, tolerance: float = 0.01) -> Tuple[bool, str]:
        """
        Validate student's answer against calculated result.
        
        Args:
            shape_name (str): Name of the shape
            user_answer (float): Student's calculated answer
            correct_answer (float): Correct answer
            tolerance (float): Acceptable error margin
            
        Returns:
            Tuple[bool, str]: (is_correct, feedback_message)
        """
        if correct_answer == 0:
            return False, "Invalid problem setup."
        
        error_percentage = abs(user_answer - correct_answer) / correct_answer
        
        if error_percentage <= tolerance:
            return True, f"Correct! The area is {correct_answer:.2f} square units."
        elif error_percentage <= 0.05:
            return False, f"Close! The correct answer is {correct_answer:.2f}. Check your calculation."
        else:
            return False, f"Not quite. The correct answer is {correct_answer:.2f}. Review the formula."
    
    def get_all_shapes(self) -> List[str]:
        """
        Retrieve list of all available shapes in ontology.
        Returns lowercase shape names.
        
        Returns:
            List[str]: Names of all shapes
        """
        return ['square', 'rectangle', 'triangle', 'circle']


def initialize_ontology(ontology_path: str) -> OntologyHandler:
    """
    Factory function to initialize ontology handler.
    
    Args:
        ontology_path (str): Path to OWL file
        
    Returns:
        OntologyHandler: Initialized handler instance
    """
    try:
        return OntologyHandler(ontology_path)
    except Exception as e:
        logger.error(f"Failed to initialize ontology: {str(e)}")
        raise