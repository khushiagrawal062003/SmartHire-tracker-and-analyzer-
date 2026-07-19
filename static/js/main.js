// SmartHire main application logic

document.addEventListener("DOMContentLoaded", function () {
    // Sidebar toggle functionality for mobile responsiveness
    const sidebarCollapse = document.getElementById("sidebarCollapse");
    const sidebar = document.querySelector(".sidebar");
    
    if (sidebarCollapse && sidebar) {
        sidebarCollapse.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }

    // Auto-dismiss Django notifications after 5 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            // Using bootstrap native close trigger if available
            const closeBtn = alert.querySelector(".btn-close");
            if (closeBtn) {
                closeBtn.click();
            } else {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 500);
            }
        }, 5000);
    });

    // Drag and Drop File Upload visualization
    const uploadArea = document.getElementById("uploadArea");
    const fileInput = document.getElementById("fileInput");

    if (uploadArea && fileInput) {
        // Clicking on the upload area triggers file input click
        uploadArea.addEventListener("click", () => fileInput.click());

        // Highlight upload area on dragover
        uploadArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            uploadArea.classList.add("dragover");
        });

        // Remove highlight on dragleave/drop
        ["dragleave", "drop"].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove("dragover");
            });
        });

        // Handle file drop
        uploadArea.addEventListener("drop", (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateUploadUI(e.dataTransfer.files[0].name);
            }
        });

        // Handle file selection via explorer
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length) {
                updateUploadUI(fileInput.files[0].name);
            }
        });
    }

    function updateUploadUI(fileName) {
        const uploadText = document.getElementById("uploadText");
        const uploadSubtext = document.getElementById("uploadSubtext");
        if (uploadText) {
            uploadText.innerText = "Selected file: " + fileName;
            uploadText.classList.add("text-success", "fw-bold");
        }
        if (uploadSubtext) {
            uploadSubtext.innerText = "Click upload button or select another file to replace.";
        }
    }
});
