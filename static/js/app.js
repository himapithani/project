async function switchLanguage(lang) {
  const response = await fetch(`/language/?lang=${lang}`);
  if (response.ok) location.reload();
}

function initWaveform() {
  const button = document.getElementById("voice-btn");
  const canvas = document.getElementById("waveform");
  if (!button || !canvas) return;

  button.addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();
    source.connect(analyser);
    analyser.fftSize = 256;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const ctx = canvas.getContext("2d");

    function draw() {
      requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      for (let i = 0; i < dataArray.length; i += 1) {
        const x = (i / dataArray.length) * canvas.width;
        const y = canvas.height - (dataArray[i] / 255) * canvas.height;
        ctx.lineTo(x, y);
      }
      ctx.strokeStyle = "#2563eb";
      ctx.stroke();
    }
    draw();
  });
}

document.addEventListener("DOMContentLoaded", initWaveform);
