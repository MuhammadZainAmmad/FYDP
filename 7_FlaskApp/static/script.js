const fileUpload = document.getElementById('file-upload');
const predictButton = document.getElementById('predict-button');
const storeButton = document.getElementById('store-button');
const previewImage = document.getElementById('preview-image');
const resultDiv = document.getElementById('result');

const labelMap = {
    0: 'Informal',
    1: 'Formal',
};

fileUpload.addEventListener('change', function () {
    if (fileUpload.files && fileUpload.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            previewImage.setAttribute('src', e.target.result);
        };

        reader.readAsDataURL(fileUpload.files[0]);
        predictButton.disabled = false;
        storeButton.disabled = false;
    }
});

predictButton.addEventListener('click', async () => {
    if (fileUpload.files && fileUpload.files[0]) {
        const formData = new FormData();
        formData.append('file', fileUpload.files[0]);

        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            const predictedLabel = labelMap[data.predicted_label];
            resultDiv.innerText = `Predicted Label: ${predictedLabel}`;
        } else {
            resultDiv.innerText = 'Failed to make a prediction.';
        }
    } else {
        resultDiv.innerText = 'Please choose an image first.';
    }
});

storeButton.addEventListener('click', async () => {
    if (fileUpload.files && fileUpload.files[0]) {
        const formData = new FormData();
        formData.append('file', fileUpload.files[0]);

        const predictResponse = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        if (predictResponse.ok) {
            const predictData = await predictResponse.json();
            const predictedLabel = labelMap[predictData.predicted_label];

            // Send both the image and predicted label together
            formData.append('predicted_label', predictedLabel);

            const storeResponse = await fetch('/store_image', {
                method: 'POST',
                body: formData
            });

            if (storeResponse.ok) {
                alert('Image and label stored successfully!');
            } else {
                alert('Failed to store image and label.');
            }
        } else {
            alert('Failed to make a prediction.');
        }
    } else {
        alert('Please choose an image first.');
    }
});
