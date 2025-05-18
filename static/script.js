const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const result = document.getElementById('result');
const snapBtn = document.getElementById('snap');

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => video.srcObject = stream);

snapBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'capture.png');

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            result.innerHTML = `<strong>Plaque :</strong> ${data.plaque}<br><strong>Propriétaire :</strong> ${data.proprietaire}`;
        });
    }, 'image/png');
});