const form = document.querySelector('#form');
const launchBtn = document.querySelector('#launch-btn');
const goToFormButton = document.querySelector('#go-to-form-btn');


goToFormButton.addEventListener('click', function (e) {
    e.preventDefault();
    form.scrollIntoView();
});


goToReadmeButton.addEventListener('click', function (e) {
    e.preventDefault();
    form.scrollIntoView();
});
