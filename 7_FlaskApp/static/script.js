const fileUpload = document.getElementById('file-upload');
const predictButton = document.getElementById('predict-button');
const previewImage = document.getElementById('preview-image');
const resultDiv = document.getElementById('result');

fileUpload.addEventListener('change', function () {
    if (fileUpload.files && fileUpload.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            previewImage.setAttribute('src', e.target.result);
        };

        reader.readAsDataURL(fileUpload.files[0]);
        predictButton.disabled = false;
    }
});

document.getElementById('predict-button').addEventListener('click', async () => {
    const formData = new FormData();
    formData.append('file', fileUpload.files[0]);
    const response = await fetch('/predict', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    resultDiv.innerText = `Predicted Label: ${data.predicted_label}`;
});
