// Run after page loads
document.addEventListener("DOMContentLoaded", () => {
    console.log("Material DB JS Loaded");

    // Auto focus on material name input if exists
    const nameInput = document.querySelector("input[name='name']");
    if (nameInput) nameInput.focus();
});

/* =========================
   TABLE SEARCH / FILTER
   ========================= */
function searchMaterial() {
    let input = document.getElementById("searchInput");
    let filter = input.value.toUpperCase();
    let table = document.getElementById("materialTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        let td = rows[i].getElementsByTagName("td")[0];
        if (td) {
            let textValue = td.textContent || td.innerText;
            rows[i].style.display =
                textValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
        }
    }
}

/* =========================
   FORM VALIDATION
   ========================= */
function validateForm() {
    let inputs = document.querySelectorAll("input");
    for (let input of inputs) {
        if (input.value === "") {
            alert("Please fill all fields!");
            return false;
        }
    }
    return true;
}

/* =========================
   CONFIRM EXCEL UPLOAD
   ========================= */
function confirmUpload() {
    return confirm("Are you sure you want to upload this Excel file?");
}
