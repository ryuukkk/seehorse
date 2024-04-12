let localStream;
let remoteStream;
let videoStream;

async function liveStream() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });

    document.getElementById("localVideo").srcObject = stream;

    await videoStream.setRemoteDescription(answer);
  } catch (error) {
    console.error("Unable to get Video Asscess:", error);
  }
}

// function for to send the data to backend
function sendtranscript(transcription) {
  fetch("http://127.0.0.1:8000/vision/process_data/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrfToken,
    },
    body: "data=" + encodeURIComponent(transcription),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("Backend_response").innerText =
        "Backend Data: " + data.processed_data;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Call the liveStream function when the page loads
window.addEventListener("DOMContentLoaded", liveStream);

//improved speech recognition

///////////////////////////////////////////////////////////////////
const startRecordingButton = document.getElementById("startRecording");

const transcriptionOutput = document.getElementById("transcription");

let recognition;

// Check if the browser supports speech recognition
if ("webkitSpeechRecognition" in window) {
  recognition = new webkitSpeechRecognition();

  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onstart = function () {
    console.log("Speech recognition started");
  };
  // creating the transcipt and showing on the screen

  recognition.onresult = function (event) {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        transcript += event.results[i][0].transcript;
      }
    }
    transcriptionOutput.textContent = transcript;
    sendtranscript(transcript); //sending the Transcript to backend server
  };

  recognition.onerror = function (event) {
    console.error("Speech recognition error:", event.error);
  };

  recognition.onspeechend = function () {
    console.log("Speech ended");
    startTimer();
  };

  startRecordingButton.addEventListener("click", function () {
    recognition.start();
    console.log("Recording started");
  });
} else {
  console.error("Speech recognition not supported in this browser.");
  startRecordingButton.disabled = true;
}

let timer;

function startTimer() {
  clearTimeout(timer);
  timer = setTimeout(function () {
    console.log("No speech detected for 3 seconds. Stopping recognition.");
    recognition.stop();
  }, 3000);
}
