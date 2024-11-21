const modal = document.getElementById('messageModal');
const messageItems = document.querySelectorAll('.modal-content ul li');

function openModal() {
    modal.style.display = 'flex';
}

function closeModal() {
    modal.style.display = 'none';
}

const toggle = document.querySelector('.toggle');
toggle.addEventListener('click', () => {
    toggle.classList.toggle('active');
});


function toggleMicrophone() {
    const micButton = document.querySelector('.mic-button');
    micButton.classList.toggle('active');
}

messageItems.forEach(item => {
    item.addEventListener('click', () => {
        closeModal(); 
    });
});


const micButton = document.querySelector('.mic-button');

// Turn green while pressed
micButton.addEventListener('mousedown', () => {
    micButton.classList.add('pressed');
});

// Turn back to default when released
micButton.addEventListener('mouseup', () => {
    micButton.classList.remove('pressed');
});

// Also handle the case where the mouse leaves the button while pressed
micButton.addEventListener('mouseleave', () => {
    micButton.classList.remove('pressed');
});

