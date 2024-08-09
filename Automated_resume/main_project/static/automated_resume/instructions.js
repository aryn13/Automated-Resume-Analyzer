document.getElementById("quiz-form").onsubmit = function() {
    // Disable the button
    document.getElementById("oneclick").disabled = true;

    // Do some validation stuff

    // Allow the form to be submitted
    return true;
};

