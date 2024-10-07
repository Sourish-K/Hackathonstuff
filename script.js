// Variables for tracking star input in manual mode
let currentStarIndex = 0;
let stars = [];
let totalStars = 0;

document.getElementById("manual-btn").addEventListener("click", function () {
    document.getElementById("manual-input").classList.remove("hidden");
    document.getElementById("auto-input").classList.add("hidden");
    document.getElementById("submit-btn").classList.remove("hidden");

    // Listen for the number of stars input
    document.getElementById("total-stars").addEventListener("input", function () {
        totalStars = parseInt(this.value);
        stars = Array(totalStars).fill(null).map(() => ({ name: '', x: '', y: '', z: '' }));
        currentStarIndex = 0;
        if (totalStars > 0) displayStar(currentStarIndex);  // Initialize with the first star
    });
});

document.getElementById("auto-btn").addEventListener("click", function () {
    document.getElementById("auto-input").classList.remove("hidden");
    document.getElementById("manual-input").classList.add("hidden");
    document.getElementById("submit-btn").classList.remove("hidden");
});

document.getElementById("file-upload").addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        document.getElementById("file-name").textContent = file.name;  // Display file name
    }
});

// Function to display star input fields
function displayStar(index) {
    const starInputs = document.getElementById("star-inputs");
    const star = stars[index];

    starInputs.innerHTML = `
        <h3>Star ${index + 1}</h3>
        <label for="star-name-${index}">Name:</label>
        <input type="text" id="star-name-${index}" value="${star.name}" />
        <label for="star-x-${index}">X Coordinate:</label>
        <input type="number" id="star-x-${index}" value="${star.x}" />
        <label for="star-y-${index}">Y Coordinate:</label>
        <input type="number" id="star-y-${index}" value="${star.y}" />
        <label for="star-z-${index}">Z Coordinate:</label>
        <input type="number" id="star-z-${index}" value="${star.z}" />
    `;
}

// Save the current star input and update it in the array
function saveStar(index) {
    const name = document.getElementById(`star-name-${index}`).value;
    const x = document.getElementById(`star-x-${index}`).value;
    const y = document.getElementById(`star-y-${index}`).value;
    const z = document.getElementById(`star-z-${index}`).value;

    stars[index] = { name, x, y, z };
}

// Handle previous star navigation
document.getElementById("prev-star-btn").addEventListener("click", function () {
    if (currentStarIndex > 0) {
        saveStar(currentStarIndex);  // Save current star data
        displayStar(--currentStarIndex);
    }
});

// Handle next star navigation
document.getElementById("next-star-btn").addEventListener("click", function () {
    if (currentStarIndex < totalStars - 1) {
        saveStar(currentStarIndex);  // Save current star data
        displayStar(++currentStarIndex);
    }
});

// Submit button event listener
document.getElementById("submit-btn").addEventListener("click", function () {
    // Handle manual mode submission
    if (!document.getElementById("manual-input").classList.contains("hidden")) {
        saveStar(currentStarIndex);  // Save current star data before submission

        const lineWidth = document.getElementById("manual-line-width").value;
        const starSize = document.getElementById("manual-star-size").value;

        // Send data to the server
        fetch('/manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stars: stars,
                lineWidth: lineWidth,
                starSize: starSize
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log response from server
            document.getElementById('message').textContent = "Stars plotted successfully!";
        });
    }
    // Handle auto mode submission
    else {
        const fileInput = document.getElementById("file-upload").files[0];
        const lineWidth = document.getElementById("auto-line-width").value;
        const starSize = document.getElementById("auto-star-size").value;

        const formData = new FormData();
        formData.append('file', fileInput);
        formData.append('lineWidth', lineWidth);
        formData.append('starSize', starSize);

        fetch('/auto', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log response from server
            document.getElementById('message').textContent = "Stars detected and plotted successfully!";
        });
    }
});
