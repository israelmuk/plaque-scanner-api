const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const result = document.getElementById('result');
const snapBtn = document.getElementById('snap');
const cameraSelect = document.getElementById('cameraSelect');
const uploadInput = document.getElementById('uploadInput');

// Charger les caméras disponibles
navigator.mediaDevices.enumerateDevices().then(devices => {
    devices.filter(device => device.kind === 'videoinput').forEach((camera, index) => {
        const option = document.createElement('option');
        option.value = camera.deviceId;
        option.text = camera.label || `Camera ${index + 1}`;
        cameraSelect.appendChild(option);
    });
});

// Démarrer la caméra sélectionnée
function startCamera(deviceId) {
    if (window.stream) {
        window.stream.getTracks().forEach(track => track.stop());
    }
    navigator.mediaDevices.getUserMedia({ video: { deviceId: deviceId ? { exact: deviceId } : undefined } })
        .then(stream => {
            window.stream = stream;
            video.srcObject = stream;
        });
}

cameraSelect.onchange = () => startCamera(cameraSelect.value);
startCamera();

// Capture la zone rouge (zone-crop)
snapBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 20, 90, 280, 60, 0, 0, 280, 60);
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'capture.png');
        sendToServer(formData);
    }, 'image/png');
});

// Upload manuel
uploadInput.addEventListener('change', (e) => {
    const formData = new FormData();
    formData.append('image', e.target.files[0]);
    sendToServer(formData);
});

// Envoie l'image au serveur
function sendToServer(formData) {
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        result.innerHTML = `<strong>Plaque :</strong> ${data.plaque}<br><strong>Propriétaire :</strong> ${data.proprietaire}`;
    });
}