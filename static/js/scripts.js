/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/



// Function to toggle the display of replies
function toggleReplies(button) {
    var commentContainer = button.closest('.comment-container');
    var repliesContainer = commentContainer.querySelector('.replies-container');
    repliesContainer.style.display = (repliesContainer.style.display === 'none') ? 'block' : 'none';
}

function toggleVote(button, action) {
    var commentContainer = button.closest('.comment-container');
    var upvoteButton = commentContainer.querySelector('.upvote-button');
    var downvoteButton = commentContainer.querySelector('.downvote-button');
    
    // Get the current counts or set to 0 if not a valid number
    var upvoteCount = parseInt(upvoteButton.innerText) || 0;
    var downvoteCount = parseInt(downvoteButton.innerText) || 0;

    if (action === 'up') {
        upvoteCount++;
        upvoteButton.innerHTML = `&#9650; ${upvoteCount}`;
        downvoteButton.innerHTML = `&#9660; ${downvoteCount}`;
    } else if (action === 'down') {
        downvoteCount++;
        downvoteButton.innerHTML = `&#9660; ${downvoteCount}`;
        upvoteButton.innerHTML = `&#9650; ${upvoteCount}`;
    }
}

window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})


