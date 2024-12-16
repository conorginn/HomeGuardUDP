function openModal(modalId) {
    console.log("Opening modal: " + modalId);
    document.getElementById(modalId).style.display = "flex";
}

// Close Modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// Save Name
function saveName() {
    const username = document.getElementById("nameInput").value;

    if (username.trim() !== "") {
        fetch("/update_username", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username }), // Send the new name as JSON
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    document.getElementById("currentName").innerText = username; // Update the UI
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

function uploadAudio() {
    const audioNameInput = document.getElementById("audioNameInput");
    const fileInput = document.getElementById("audioUpload");
    const fileInfo = document.getElementById("fileInfo");

    const audioName = audioNameInput.value.trim();
    const file = fileInput.files[0];

    // Validation
    if (!audioName) {
        alert("Please enter a name for the audio.");
        return;
    }
    if (!file) {
        alert("Please select an audio file.");
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append("audio_name", audioName);
    formData.append("file", file);

    fetch("/upload_audio", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert("Audio uploaded successfully!");
                fileInfo.textContent = `Uploaded: ${file.name}`;
                location.reload(); // Reload to show updated messages
            } else {
                alert(data.message || "Failed to upload audio.");
            }
        })
        .catch((error) => {
            console.error("Error uploading audio:", error);
            alert("An error occurred while uploading the file.");
        });
}

// Save Voice Changer
function saveVoiceChanger() {
    const voice = document.getElementById("voiceChangerSelect").value;
    document.getElementById("voiceSelected").innerText = voice;
    closeModal("voiceChangerModal");
}