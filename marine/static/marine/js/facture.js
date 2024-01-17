var url = document.getElementById("printPageButton").href;
print()
window.addEventListener('afterprint', (event) => { location.href = url; });