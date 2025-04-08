document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const feedbackText = document.getElementById('feedback-text');
    const statusIndicator = document.querySelector('.status-indicator');
    let feedbackEventSource;

    function startSession() {
        feedbackEventSource = new EventSource('/get_feedback');
        
        feedbackEventSource.onmessage = function(e) {
            const data = JSON.parse(e.data);
            feedbackText.textContent = data.feedback;
            feedbackText.classList.add('fade-in');
            setTimeout(() => feedbackText.classList.remove('fade-in'), 500);
            statusIndicator.classList.add('active');
        };
        
        startBtn.disabled = true;
        stopBtn.disabled = false;
        startBtn.classList.add('btn-disabled');
        stopBtn.classList.remove('btn-disabled');
    }

    function stopSession() {
        if (feedbackEventSource) {
            feedbackEventSource.close();
        }
        feedbackText.textContent = "Session stopped";
        statusIndicator.classList.remove('active');
        startBtn.disabled = false;
        stopBtn.disabled = true;
        startBtn.classList.remove('btn-disabled');
        stopBtn.classList.add('btn-disabled');
    }

    startBtn.addEventListener('click', startSession);
    stopBtn.addEventListener('click', stopSession);
    
    stopBtn.disabled = true;
    stopBtn.classList.add('btn-disabled');

    // Add subtle animation for feedback text
    const style = document.createElement('style');
    style.textContent = `
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .btn-disabled {
            opacity: 0.6;
            transform: scale(0.95);
        }
    `;
    document.head.appendChild(style);
});