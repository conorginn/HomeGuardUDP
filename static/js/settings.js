function openModal(modalId) {
    document.getElementById(modalId).style.display = "flex";
}

// Close Modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// Save Name
function saveName() {
    const name = document.getElementById("nameInput").value;
    if (name.trim() !== "") {
        document.getElementById("currentName").innerText = name; // Correctly set the new name
    } else {
        alert("Please enter a valid name.");
    }
    closeModal("nameModal");
}

// Save Address
function savePassword() {
    const password = document.getElementById("passwordInput").value;
    if (password.trim() !== "") {
        document.getElementById("currentPassword").innerText = address; // Correctly set the new address
    } else {
        alert("Please enter a valid password.");
    }
    closeModal("passwordModal");
}

// Handle Audio Upload
function uploadAudio() {
    const fileInput = document.getElementById("audioUpload");
    const file = fileInput.files[0];

    if (file) {
        const fileInfo = document.getElementById("fileInfo");
        fileInfo.textContent = `Selected file: ${file.name}`;
        alert(`Audio file "${file.name}" uploaded successfully!`);
    } else {
        alert("Please select an audio file to upload.");
    }
    closeModal("messageModal");
}

// Save Voice Changer
function saveVoiceChanger() {
    const voice = document.getElementById("voiceChangerSelect").value;
    document.getElementById("voiceSelected").innerText = voice;
    closeModal("voiceChangerModal");
}