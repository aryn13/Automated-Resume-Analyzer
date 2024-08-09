document.addEventListener('DOMContentLoaded', (event) => {
    let timeLeft = 30; // 30 seconds for each question
    const timerElement = document.getElementById('timer');

    function updateTimer() {
        if (timeLeft <= 0) {
            // Time's up, submit the form with a 'nil' value
            submitQuizWithNil();
        } else {
            timerElement.textContent = `Time left: ${timeLeft} seconds`;
            timeLeft--;
        }
    }

    const timerInterval = setInterval(updateTimer, 1000);

    function submitQuizWithNil() {
        clearInterval(timerInterval);
        let form = document.querySelector('form');
        let fakeOption = document.createElement('input');
        fakeOption.type = 'hidden';
        fakeOption.name = 'option';
        fakeOption.value = 'nil'; // Special value to indicate timeout
        form.appendChild(fakeOption);
        form.submit();
    }
    function handleFormSubmit(){
        clearInterval(timerInterval);
    }
    // document.getElementById("form").addEventListener("submit", handleFormSubmit);
    // Request to make the page full screen when the quiz starts
    // function requestFullScreen(element) {
    //     if (element.requestFullscreen) {
    //         element.requestFullscreen();
    //     } else if (element.mozRequestFullScreen) { // Firefox
    //         element.mozRequestFullScreen();
    //     } else if (element.webkitRequestFullscreen) { // Chrome, Safari, and Opera
    //         element.webkitRequestFullscreen();
    //     } else if (element.msRequestFullscreen) { // IE/Edge
    //         element.msRequestFullscreen();
    //     }
    // }

    // Detect when the user leaves the full-screen mode
    function onFullScreenChange() {
        if (!document.fullscreenElement && !document.webkitFullscreenElement &&
            !document.mozFullScreenElement && !document.msFullscreenElement) {
            // User has exited full-screen mode
            blockInteractions();
        }
    }
    function blockInteractions(){
        document.body.style.pointerEvents = 'none';
    }

    function enableInteractions(){
        document.body.style.pointerEvents = 'auto';
    }

    document.addEventListener('fullscreenchange', onFullScreenChange);
    document.addEventListener('webkitfullscreenchange', onFullScreenChange);
    document.addEventListener('mozfullscreenchange', onFullScreenChange);
    document.addEventListener('MSFullscreenChange', onFullScreenChange);
    // Automatically submit the quiz if the user switches tabs
    function submitQuiz() {
        // Find the form and simulate submission with a garbage value for remaining questions
        let form = document.getElementById('form');
        let options = document.getElementById('input[name="option"]');
        if (options.length > 0) {
            // Choose a garbage value option
            options[0].value = 'z';
            options[0].checked = true;
        } else {
            // Create a hidden input if no options are available (edge case)
            let fakeOption = document.createElement('input');
            fakeOption.type = 'hidden';
            fakeOption.name = 'option';
            fakeOption.value = 'z'; // Garbage value
            form.appendChild(fakeOption);
        }
        form.submit();
    }

    // Listen for visibility change to detect tab switching
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') {
            submitQuiz();
        }
    });

    // Listen for full-screen change events

    // Make the page full screen initially
    // requestFullScreen(document.documentElement);

});
