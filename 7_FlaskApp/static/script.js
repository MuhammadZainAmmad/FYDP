const fileUpload = document.getElementById('file-upload');
const cameraButton = document.getElementById('camera-button');
const predictButton = document.getElementById('predict-button');
const storeButton = document.getElementById('store-button');
const previewImage = document.getElementById('preview-image');
const resultDiv = document.getElementById('result');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');

// const labelMap = {
//     0: 'Informal',
//     1: 'Formal',
// };

const usageLabelMap = {
    0: 'Informal',
    1: 'Formal',
};

const articleTypeLabelMap = {
    0: 'Shirt',
    1: 'Tshirt',
    2: 'Trouser',
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
        await predictAndDisplayLabels(fileUpload.files[0]);
    } else if (previewImage.src) {
        const imgBlob = await fetch(previewImage.src).then(response => response.blob());
        await predictAndDisplayLabels(imgBlob);
    } else {
        resultDiv.innerText = 'Please choose an image first.';
    }
});

storeButton.addEventListener('click', async () => {
    if (fileUpload.files && fileUpload.files[0]) {
        const formData = createFormData(fileUpload.files[0]);
        await predictStoreAndDisplayResult(formData);
    } else if (previewImage.src) {
        const dataURL = previewImage.src;
        const blob = dataURItoBlob(dataURL);
        const formData = createFormData(blob);
        await predictStoreAndDisplayResult(formData);
    } else {
        alert('Please choose an image first.');
    }
});

cameraButton.addEventListener('click', async () => { 
    // Use the getUserMedia API to capture image from camera
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    const track = stream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(track);

    try {
        const blob = await imageCapture.takePhoto();

        // Convert the captured image to a base64 data URL
        const base64Image = await blobToBase64(blob);

        // Display the captured image in the preview area
        previewImage.setAttribute('src', base64Image);

        // Enable predict and store buttons
        predictButton.disabled = false;
        storeButton.disabled = false;

    } catch (error) {
        console.error('Error capturing image:', error);
    }
});

searchButton.addEventListener('click', async () => {
    const searchQuery = searchInput.value.toLowerCase();
    if (searchQuery) {
        window.location.href = `/search_result?search=${searchQuery}`;
    } else {
        window.location.href = '/search_result';
    }
});

// Add this code in your script.js file
if (searchButton) {
    searchButton.addEventListener('click', async () => {
        const searchQuery = searchInput.value.toLowerCase();
        if (searchQuery) {
            window.location.href = `/search_result?search=${searchQuery}`;
        } else {
            window.location.href = '/search_result';
        }
    });
}



// async function predictAndDisplayLabel(imageData) {
//     const formData = createFormData(imageData);
//     const response = await fetch('/predict', {
//         method: 'POST',
//         body: formData
//     });

//     if (response.ok) {
//         const data = await response.json();
//         const predictedLabel = labelMap[data.predicted_label];
//         resultDiv.innerText = `Predicted Label: ${predictedLabel}`;
//     } else {
//         resultDiv.innerText = 'Failed to make a prediction.';
//     }
// }

async function predictAndDisplayLabels(imageData) {
    const formData = createFormData(imageData);
    const response = await fetch('/predict', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        const predictedUsageLabel = data.predicted_label_usage;
        const predictedArticleTypeLabel = data.predicted_label_article_type;
        
        resultDiv.innerText = `Uploaded article is "${predictedUsageLabel} ${predictedArticleTypeLabel}"`;
    } else {
        resultDiv.innerText = 'Failed to make a prediction.';
    }
}

async function predictStoreAndDisplayResult(formData) {
    const predictResponse = await fetch('/predict', {
        method: 'POST',
        body: formData
    });

    if (predictResponse.ok) {
        const predictData = await predictResponse.json();
        const predictedLabel = predictData.predicted_label;
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
}

function createFormData(file) {
    const formData = new FormData();
    formData.append('file', file);
    return formData;
}

async function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            resolve(reader.result);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}
