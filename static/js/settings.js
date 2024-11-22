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
        fetch("/update_username", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name }), // Send the new name as JSON
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    document.getElementById("currentName").innerText = name; // Update the UI
                    closeModal("nameModal"); // Close the modal
                } else {
                    alert(data.message || "Failed to update name.");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred while updating the name.");
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
            body: JSON.stringify({ password }), // Send the new password as JSON
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Password updated successfully!");
                    closeModal("passwordModal"); // Close the modal
                } else {
                    alert(data.message || "Failed to update password.");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred while updating the password.");
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