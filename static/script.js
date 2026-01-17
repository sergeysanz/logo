const openPopupBtn = document.getElementById('openPopup');
const popup = document.getElementById('logoPopup');
const closeBtn = popup.querySelector('.close');
const form = document.getElementById('logoForm');
const generatedLogo = document.getElementById('generatedLogo');
const downloadBtn = document.getElementById('downloadBtn');

// Animación inicial GSAP
gsap.from(".logo", {opacity:0, y:-50, duration:1, ease:"power2.out"});
gsap.from(".site-title", {opacity:0, y:-20, delay:0.5, duration:1, ease:"power2.out"});
gsap.from(".hero-title", {opacity:0, y:30, delay:1, duration:1, ease:"power2.out"});
gsap.from(".hero-text", {opacity:0, y:30, delay:1.2, duration:1, ease:"power2.out"});
gsap.from(".btn-primary", {opacity:0, scale:0.8, delay:1.5, duration:0.8, ease:"back.out(1.7)"});

// Abrir popup
openPopupBtn.addEventListener('click', () => {
    popup.style.display = 'flex';
    gsap.to(".popup-content", {opacity:1, y:0, duration:0.5, ease:"power2.out"});
});

// Cerrar popup
closeBtn.addEventListener('click', () => {
    gsap.to(".popup-content", {opacity:0, y:-50, duration:0.3, ease:"power2.in", onComplete:()=>{popup.style.display='none';}});
});

// Formulario
form.addEventListener('submit', function(e){
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/generate',{
        method:'POST',
        body: formData
    })
    .then(res => {
        if(!res.ok) return res.json().then(err => {throw new Error(err.error)});
        return res.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        generatedLogo.src = url;
        gsap.to(".result", {opacity:1, duration:0.5});
    })
    .catch(err => alert(err));
});

// Descargar logo
downloadBtn.addEventListener('click', () => {
    const a = document.createElement('a');
    a.href = generatedLogo.src;
    a.download = 'logo.png';
    a.click();
});
