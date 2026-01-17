document.addEventListener("DOMContentLoaded", function () {
    const openPopupBtn = document.getElementById("openPopup");
    const popup = document.getElementById("logoPopup");
    const closePopup = document.querySelector(".popup .close");
    const logoForm = document.getElementById("logoForm");
    const generatedLogo = document.getElementById("generatedLogo");
    const downloadBtn = document.getElementById("downloadBtn");
    const insightDiv = document.getElementById("brandInsight");
    const strategyDiv = document.getElementById("brandStrategy");

    // Abrir popup
    openPopupBtn.addEventListener("click", () => {
        popup.style.display = "block";
    });

    // Cerrar popup
    closePopup.addEventListener("click", () => {
        popup.style.display = "none";
    });

    window.addEventListener("click", (e) => {
        if (e.target === popup) popup.style.display = "none";
    });

    // Enviar formulario
    logoForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(logoForm);

        generatedLogo.src = "";
        insightDiv.textContent = "Generando logo e ideas...";
        strategyDiv.textContent = "";

        try {
            const response = await fetch("/generate", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                insightDiv.textContent = "Error: " + data.error;
                return;
            }

            generatedLogo.src = "data:image/png;base64," + data.logo;

            insightDiv.textContent = "Insight / Lema: " + data.brand_strategy.split("\n")[0];
            strategyDiv.textContent = data.brand_strategy;

            downloadBtn.onclick = () => {
                const a = document.createElement("a");
                a.href = generatedLogo.src;
                a.download = "logo.png";
                a.click();
            };
        } catch (err) {
            insightDiv.textContent = "Error al generar el logo: " + err.message;
        }
    });
});
