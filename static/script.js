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
            const response = await fetch("/generate", {
                method: "POST",
                body: formData
            });

            let data;
            try {
                data = await response.json();
            } catch {
                insightDiv.textContent = "Error: La respuesta del servidor no es JSON válido.";
                return;
            }

            // Mostrar error backend
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
            }

            // Mostrar insight
            insightDiv.textContent = data.insight
                ? data.insight
                : "No se pudo generar insight.";

            // Mostrar estrategia
            if (data.marketing_strategy) {
                let strategyText = "";

                if (data.marketing_strategy.tone) {
                    strategyText += `Tono de comunicación:\n- ${data.marketing_strategy.tone}\n\n`;
                }

                if (data.marketing_strategy.social_media?.length) {
                    strategyText += "Estrategia en redes:\n";
                    data.marketing_strategy.social_media.forEach(i => {
                        strategyText += `- ${i}\n`;
                    });
                    strategyText += "\n";
                }

                if (data.marketing_strategy.events?.length) {
                    strategyText += "Estrategia de eventos:\n";
                    data.marketing_strategy.events.forEach(e => {
                        strategyText += `- ${e}\n`;
                    });
                }

                strategyDiv.textContent = strategyText.trim();
            } else {
                strategyDiv.textContent = "No se pudo generar estrategia.";
            }

        } catch (err) {
            insightDiv.textContent = "Error al generar el logo.";
            strategyDiv.textContent = err.message;
        }
    });
});
