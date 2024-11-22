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
        fetch("/update_name", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    document.getElementById("currentName").innerText = name;
                    closeModal("nameModal");
                } else {
                    alert(data.message || "Failed to update name.");
                }
            });
    } else {
        alert("Please enter a valid name.");
    }
}


function savePassword() {
    const password = document.getElementById("passwordInput").value;
    if (password.trim() !== "") {
        fetch("/update_password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ password }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Password updated successfully!");
                    closeModal("passwordModal");
                } else {
                    alert(data.message || "Failed to update password.");
                }
            });
    } else {
        alert("Please enter a valid password.");
    }
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