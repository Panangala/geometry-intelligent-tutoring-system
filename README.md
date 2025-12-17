# Geometry Intelligent Tutoring System

## Overview

This is an intelligent tutoring system for teaching geometry. The main focus is on area calculations for four basic shapes: square, rectangle, triangle, and circle. The system uses semantic web technologies (OWL ontologies) and adapts to each student's performance level.

The basic idea is to combine formal knowledge representation using ontologies with adaptive learning that changes the difficulty of problems based on how well the student is doing.

## What This System Does

The system has several main components:

1. Ontology-Based Knowledge: The geometry knowledge is stored in an OWL ontology file instead of being written directly into the code. This makes it easier to add new shapes or update formulas without changing the application itself.

2. Adaptive Difficulty: The system tracks student performance. If a student gets 80% or more problems correct, it moves them to harder problems. If they drop below 50%, it goes back to easier problems. This is based on research showing that students learn best when they get about 70-80% of problems right.

3. Problem Generation: Problems are automatically generated with random parameters. The system pulls what measurements are needed from the ontology, so for a circle it knows it needs a radius.

4. Web Interface: There is a simple web-based interface where students select a shape, read a lesson about it, then practice solving problems. They can see their progress on a dashboard.

## How to Install

You need Python 3.7 or later with pip. Then follow these steps:

Clone the repository:
```
[git clone https://github.com/YOUR_USERNAME/geometry-intelligent-tutoring-system.git
cd geometry-intelligent-tutoring-system]
```

Install the required packages:
```
pip install -r requirements.txt
```

Run the application:
```
python app.py
```

Then open a browser and go to http://localhost:5000

## Files in This Project

- geometry_ontology.owl - The ontology file containing the geometry knowledge. It has classes for shapes, measurements, properties, formulas, and learning concepts.
- config.py - Configuration and environment variables (thresholds, difficulty parameters, settings)

- app.py - The main Flask application that runs the web server

- modules/learning_engine.py - Pedagogical algorithms for problem generation, answer evaluation, and adaptive difficulty

- modules/ontology_handler.py - Handles queries to the OWL ontology using SPARQL and RDFLib

- modules/__init__.py - Package initialization

- geometry_ontology.owl - The OWL knowledge base containing geometry classes, properties, and formulas

- geometry_owl_dotfile.dot - Ontology visualization in DOT format

- templates/ - HTML templates for the user interface
  - base.html - Base layout template
  - index.html - Home page and shape selection
  - lesson.html - Educational content display
  - practice.html - Practice problem interface
  - results.html - Performance dashboard

- static/ - CSS styling and JavaScript files
  - css/style.css - Responsive design stylesheet
  - js/script.js - Client-side AJAX and interactions
  - images/ - Icons and illustrations

- requirements.txt - Python package dependencies (Flask, RDFLib, etc.)

## The Ontology

The ontology has five main classes:

1. shape - The four geometric shapes (square, rectangle, triangle, circle)

2. measurement - The measurements needed for each shape (area, radius, length, width, height, base, diameter)

3. property - Characteristics of shapes (number of sides, side length, angle measure)

4. formula - Mathematical formulas for calculating area

5. LearningConcept - Learning goals (understanding area, identifying properties, applying formulas, solving problems)

The classes have relationships:
- hasProperty - shapes have properties
- requiresMeasurement - shapes need specific measurements
- usesFormula - shapes use formulas
- hasPrerequisite - some learning concepts depend on others

## How It Works

When a student starts, they see a home page with four shape buttons. They pick a shape and see a lesson explaining that shape and how to calculate its area. Then they go to the practice section to solve problems.

The learning engine generates random problems using parameters from the ontology. For a square at easy level, it picks random numbers between 1 and 5 for the side. For medium it uses 5-10, for hard it uses 10-20.

When the student submits an answer, the system calculates the correct answer using the formula from the ontology and compares it with what the student entered. It allows a 2% tolerance for rounding errors.

The system tracks correct and incorrect answers. If the student gets 80% or more correct, it moves to a harder level. If they get less than 50%, it moves to an easier level.

## Features

Problem Generation: The system uses SPARQL to ask the ontology which measurements a shape needs. For example, asking "what measurements does a circle need?" returns "radius". Then it generates random values for those measurements.

Answer Evaluation: When a student submits an answer, the system looks up the formula for that shape, calculates the right answer, and compares it. The 2% tolerance handles rounding differences.

Adaptive Mechanism: The system keeps track of correct and incorrect answers. When accuracy goes above 80%, it advances to harder problems. When it drops below 50%, it retreats to easier ones. This is based on research showing students learn best when challenged but not overwhelmed.

Session Management: Student progress is stored in the Flask session during their visit. When they close the browser, the data is not saved.

## Using the System

1. Home page - Click the shape you want to learn
2. Lesson page - Read about the shape and see the formula
3. Practice page - Solve problems that are shown with specific measurements
4. Enter your answer and submit
5. Dashboard - See your progress, current difficulty, and accuracy percentage

## Current Limitations

The current version has some limitations:

- Data is not saved after the session ends. If a student closes the browser, their progress is lost.

- The system only tracks how many problems they get right. It doesn't try to identify specific misconceptions.

- Feedback is simple and uses templates. It doesn't give customized explanations based on specific errors.

- It is designed for one student at a time.

- There is no database, so no student accounts or long-term progress tracking.

These are things that could be added in the future.

## Technologies

Frontend:
- HTML5 for page structure
- CSS3 for styling with responsive design
- JavaScript for interactive elements

Backend:
- Python 3 with Flask framework
- RDFLib for handling the OWL ontology
- SPARQL for querying the ontology

## Deployment

For testing you can run the Flask development server with python app.py. For a real deployment you would want to:

- Use a production server like Gunicorn instead of the Flask development server
- Set up a database to store student information
- Use HTTPS for security
- Add user authentication
- Set up load balancing if many students will use it

## Possible Improvements

Some ideas for making this better:

1. Database integration to save student records and track progress over time

2. Better user modeling to detect specific misconceptions

3. More advanced adaptive algorithms using item response theory

4. Natural language generation for more varied feedback

5. Support for multiple students using the system at once

6. Analytics tools for teachers

## References

The design of this system is based on learning science research:

- Kulik and Fletcher (2016) showed intelligent tutoring systems are effective
- Sweller et al. (2011) showed students learn best at about 70-80% success rate (cognitive load theory)
- Bittencourt et al. (2020) showed benefits of using ontologies in tutoring systems
- Research shows that variety in problems helps students learn and transfer knowledge better

## Author

Developed by Isuru Lakindu Panangala Perera as part of an MSc Computer Science program at York St John University, London Campus.

## License

Academic use only. This was developed for a university assignment.

## Notes

The ontology file (geometry_ontology.owl) was created using Protégé, a standard tool for building ontologies. The ontology was checked for consistency using Protégé's validation tools.

This system shows that you can build a working intelligent tutoring system using semantic web technologies. The separation between the knowledge (in the ontology) and the learning logic (in the Python code) makes it flexible and easy to maintain.
