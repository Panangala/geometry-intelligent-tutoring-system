document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    const answerForm = document.getElementById('answer-form');
    if (answerForm) {
        answerForm.addEventListener('submit', handleAnswerSubmission);
    }
    
    const nextBtn = document.getElementById('next-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', handleNextProblem);
    }
    
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', handleGoBack);
    }
}

function handleAnswerSubmission(event) {
    event.preventDefault();
    
    const userAnswerInput = document.getElementById('user-answer');
    const userAnswer = parseFloat(userAnswerInput.value);
    
    if (isNaN(userAnswer)) {
        showErrorMessage('Please enter a valid number');
        return;
    }
    
    disableForm(true);
    showLoadingState();
    
    const requestData = {
        user_answer: userAnswer,
        shape: getShapeFromURL()
    };
    
    fetch('/api/submit-answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        displayFeedback(data);
        disableForm(false);
        showLoadingState(false);
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('An error occurred while checking your answer. Please try again.');
        disableForm(false);
        showLoadingState(false);
    });
}

function displayFeedback(data) {
    const feedbackBox = document.getElementById('feedback-box');
    const feedbackContent = document.getElementById('feedback-content');
    const nextBtn = document.getElementById('next-btn');
    
    if (!feedbackBox || !feedbackContent) {
        return;
    }
    
    const feedbackClass = data.is_correct ? 'correct' : 'incorrect';
    const feedbackTitle = data.is_correct ? 'Correct!' : 'Not quite right';
    
    let html = `
        <div class="feedback-message ${feedbackClass}">
            <h3>${feedbackTitle}</h3>
            <p>${data.feedback}</p>
            <p><strong>Your answer:</strong> ${data.user_answer}</p>
            <p><strong>Correct answer:</strong> ${data.correct_answer}</p>
        </div>
    `;
    
    feedbackContent.innerHTML = html;
    feedbackBox.style.display = 'block';
    
    if (nextBtn) {
        nextBtn.style.display = 'inline-block';
    }
    
    feedbackBox.scrollIntoView({ behavior: 'smooth' });
}

function handleNextProblem() {
    location.reload();
}

function handleGoBack() {
    const shape = getShapeFromURL();
    if (shape) {
        window.location.href = `/learn/${shape}`;
    } else {
        window.location.href = '/start';
    }
}

function getShapeFromURL() {
    const match = window.location.pathname.match(/\/(learn|practice)\/([^\/]+)/);
    return match ? match[2] : '';
}

function disableForm(disabled) {
    const form = document.getElementById('answer-form');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => {
        input.disabled = disabled;
    });
}

function showLoadingState(show = true) {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (!submitBtn) return;
    
    if (show) {
        submitBtn.textContent = 'Checking...';
        submitBtn.classList.add('loading');
    } else {
        submitBtn.textContent = 'Check Answer';
        submitBtn.classList.remove('loading');
    }
}

function showErrorMessage(message) {
    const feedbackBox = document.getElementById('feedback-box');
    const feedbackContent = document.getElementById('feedback-content');
    
    if (!feedbackBox || !feedbackContent) {
        alert(message);
        return;
    }
    
    const html = `
        <div class="feedback-message incorrect">
            <h3>Error</h3>
            <p>${message}</p>
        </div>
    `;
    
    feedbackContent.innerHTML = html;
    feedbackBox.style.display = 'block';
    feedbackBox.scrollIntoView({ behavior: 'smooth' });
}

function updateProgressDisplay() {
    fetch('/api/progress')
        .then(response => response.json())
        .then(data => {
            console.log('Progress updated:', data);
        })
        .catch(error => console.error('Error fetching progress:', error));
}