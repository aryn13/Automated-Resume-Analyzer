// document.addEventListener('DOMContentLoaded', (event) => {
//     console.log("hi")
//     document.getElementById("form").addEventListener("submit", handleFormSubmit);
//     console.log("hi gakln")
//     // Request to make the page full screen when the quiz starts
//     function requestFullScreen(element) {
//          console.log("hi hee")
//         if (element.requestFullscreen) {
//             element.requestFullscreen();
//         } else if (element.mozRequestFullScreen) { // Firefox
//             element.mozRequestFullScreen();
//         } else if (element.webkitRequestFullscreen) { // Chrome, Safari, and Opera
//             element.webkitRequestFullscreen();
//         } else if (element.msRequestFullscreen) { // IE/Edge
//             element.msRequestFullscreen();
//         }
//     }
//      console.log("hi jsfxs")
//     // Detect when the user leaves the full-screen mode
//     function onFullScreenChange() {
//         console.log("onfullscreen")
//         if (!document.fullscreenElement && !document.webkitFullscreenElement &&
//             !document.mozFullScreenElement && !document.msFullscreenElement) {
//             // User has exited full-screen mode
//             blockInteractions();
//         }
//         console.log("onfullscreenend")
//     }
//     function blockInteractions(){
//         document.body.style.pointerEvents = 'none';
//     }
//
//     function enableInteractions(){
//         document.body.style.pointerEvents = 'auto';
//     }
//
//     document.addEventListener('fullscreenchange', onFullScreenChange);
//     document.addEventListener('webkitfullscreenchange', onFullScreenChange);
//     document.addEventListener('mozfullscreenchange', onFullScreenChange);
//     document.addEventListener('MSFullscreenChange', onFullScreenChange);
//     // Automatically submit the quiz if the user switches tabs
//
//     // Listen for visibility change to detect tab switching
//
//     // Listen for full-screen change events
//
//     // Make the page full screen initially
//     requestFullScreen(document.documentElement);
// });



// function enterFullscreen() {
//             const element = document.documentElement; // Use the entire document to cover the entire screen
//             if (element.requestFullscreen) {
//                 element.requestFullscreen().catch(err => {
//                     console.error('Error attempting to enter fullscreen mode: ${err.message} (${err.name})');
//                 });
//             } else if (element.mozRequestFullScreen) { // Firefox
//                 element.mozRequestFullScreen().catch(err => {
//                     console.error('Error attempting to enter fullscreen mode: ${err.message} (${err.name})');
//                 });
//             } else if (element.webkitRequestFullscreen) { // Chrome, Safari and Opera
//                 element.webkitRequestFullscreen().catch(err => {
//                     console.error('Error attempting to enter fullscreen mode: ${err.message} (${err.name})');
//                 });
//             } else if (element.msRequestFullscreen) { // IE/Edge
//                 element.msRequestFullscreen().catch(err => {
//                     console.error('Error attempting to enter fullscreen mode: ${err.message} (${err.name})');
//                 });
//             }
//         }
//
//         // Attempt to enter fullscreen mode when the page loads
//         window.addEventListener('load', () => {
//             enterFullscreen();
//         });

// function toggleFullScreen() {
//   if (!document.fullscreenElement &&    // alternative standard method
//       !document.mozFullScreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement ) {  // current working methods
//     if (document.documentElement.requestFullscreen) {
//       document.documentElement.requestFullscreen();
//     } else if (document.documentElement.msRequestFullscreen) {
//       document.documentElement.msRequestFullscreen();
//     } else if (document.documentElement.mozRequestFullScreen) {
//       document.documentElement.mozRequestFullScreen();
//     } else if (document.documentElement.webkitRequestFullscreen) {
//       document.documentElement.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
//     }
//   } else {
//     if (document.exitFullscreen) {
//       document.exitFullscreen();
//     } else if (document.msExitFullscreen) {
//       document.msExitFullscreen();
//     } else if (document.mozCancelFullScreen) {
//       document.mozCancelFullScreen();
//     } else if (document.webkitExitFullscreen) {
//       document.webkitExitFullscreen();
//     }
//   }
// }
//
// toggleFullScreen();
// function enterFullscreen() {
//             const fullscreenElement = document.getElementById('element');
//              fullscreenElement.requestFullscreen().catch(err => {
//                     console.error("Error attempting to enable fullscreen mode: ${err.message} (${err.name})");
//                 });
//         }

function openFullScreen() {
    const fullscreenElement = document.getElementById('fullscreen-element');
    fullscreenElement.requestFullscreen().catch(err => {
        console.error(`${err.message} (${err.name})`);
    });
}

window.addEventListener('mousedown',openFullScreen);
window.addEventListener('keypress',openFullScreen);
window.addEventListener('touchstart', openFullScreen);
window.addEventListener('resize', openFullScreen);
window.addEventListener('pointerdown', openFullScreen);