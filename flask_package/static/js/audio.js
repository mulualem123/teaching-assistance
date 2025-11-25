//Audio Recording Script
//<script>
    let mediaRecorder;
    let audioChunks = [];
    let audioStream;

    const startAudioRecBtn = document.getElementById('startAudioRecBtn');
    const stopAudioRecBtn = document.getElementById('stopAudioRecBtn');
    const audioPlayback = document.getElementById('audioPlayback');
    const recordedAudioInp = document.getElementById('recordedAudio');

    if (startAudioRecBtn && stopAudioRecBtn && audioPlayback && recordedAudioInp) {
        startAudioRecBtn.addEventListener('click', async () => {
          try {
            // Request access to the microphone only
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(audioStream);
            audioChunks = [];
      
            mediaRecorder.ondataavailable = event => {
              if (event.data.size > 0) {
                audioChunks.push(event.data);
              }
            };
      
            mediaRecorder.onstop = () => {
              const audioBlob = new Blob(audioChunks, { type: 'audio/webm; codecs=opus' });
              const audioURL  = URL.createObjectURL(audioBlob);
              audioPlayback.style.display = 'block';
              audioPlayback.src = audioURL;
    
              const reader = new FileReader();
              reader.readAsDataURL(audioBlob);
              reader.onloadend = () => {
                // Store the audio data as base64 in the hidden input field
                recordedAudioInp.value = reader.result;
              };
    
              // Stop all tracks to free up resources
              audioStream.getTracks().forEach(track => track.stop());
            };
    
            mediaRecorder.start();
            startAudioRecBtn.disabled = true;
            stopAudioRecBtn.disabled = false;
          } catch (error) {
            console.error("Error accessing the microphone:", error);
            alert("Could not start audio recording. Please check your microphone settings.");
          }
        });
    
        stopAudioRecBtn.addEventListener('click', () => {
          if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            startAudioRecBtn.disabled = false;
            stopAudioRecBtn.disabled = true;
          }
        });
    }
//</script>