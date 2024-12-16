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
    const fileInput = document.getElementById("audioUpload");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select an audio file to upload.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload_audio", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Audio file uploaded successfully!");
            document.getElementById("fileInfo").textContent = `Uploaded: ${file.name}`;
        } else {
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error("Error uploading file:", error);
        alert("An error occurred during file upload.");
    });
}

// Save Voice Changer
function saveVoiceChanger() {
    const voice = document.getElementById("voiceChangerSelect").value;
    document.getElementById("voiceSelected").innerText = voice;
    closeModal("voiceChangerModal");
}