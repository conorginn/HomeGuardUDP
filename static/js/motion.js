function pollMessages() {
    fetch("/get_messages")
      .then(response => response.json())
      .then(data => {
        console.log("Messages:", data);
        if (data.length > 0) {
          const latest = data[0];
          document.getElementById("motion_id").innerText = `${latest.event} at ${latest.timestamp}`;
        } else {
          document.getElementById("motion_id").innerText = "No recent messages";
        }
      })
      .catch(err => console.error(err));
  }
  
  // Poll every 5 seconds
  setInterval(pollMessages, 5000);
  