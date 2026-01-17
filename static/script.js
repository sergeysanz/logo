document.getElementById('logoForm').addEventListener('submit', function(e){
    e.preventDefault();
    let formData = new FormData(this);

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
        document.getElementById('generatedLogo').src = url;
        document.getElementById('logoPopup').style.display = 'block';
    })
    .catch(err => alert(err));
});

function downloadLogo(){
    const img = document.getElementById('generatedLogo');
    const a = document.createElement('a');
    a.href = img.src;
    a.download = 'logo.png';
    a.click();
}

function closePopup(){
    document.getElementById('logoPopup').style.display = 'none';
}
