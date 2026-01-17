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
        popup.style.display = "flex";
    });

    // Cerrar popup
    closePopup.addEventListener("click", () => {
        popup.style.display = "none";
    });
    window.addEventListener("click", e => {
        if (e.target === popup) popup.style.display = "none";
    });

    // Enviar formulario
    logoForm.addEventListener("submit", async e => {
        e.preventDefault();
        const formData = new FormData(logoForm);

        generatedLogo.src = "";
        insightDiv.textContent = "Generando logo e ideas...";
        strategyDiv.textContent = "";

        try {
            const response = await fetch("/generate", { method: "POST", body: formData });

            // Parseo seguro del JSON
            let data;
            try {
                data = await response.json();
            } catch {
                insightDiv.textContent = "Error: La respuesta del servidor no es JSON válido.";
                strategyDiv.textContent = "";
                return;
            }

            // Mostrar errores
            if (data.error) {
                insightDiv.textContent = "Error: " + data.error;
            }

            // Mostrar logo
            if (data.logo) {
                generatedLogo.src = "data:image/png;base64," + data.logo;
                downloadBtn.onclick = () => {
                    const a = document.createElement("a");
                    a.href = generatedLogo.src;
                    a.download = "logo.png";
                    a.click();
                };
            } else {
                generatedLogo.src = "";
            }

            // Mostrar insight y estrategia
            insightDiv.textContent = "Insight / Lema: " + (data.brand_strategy ? data.brand_strategy.split("\n")[0] : "No disponible");
            strategyDiv.textContent = data.brand_strategy || "No disponible";

        } catch (err) {
            insightDiv.textContent = "Error al generar el logo: " + err.message;
            strategyDiv.textContent = "";
        }
    });
});
