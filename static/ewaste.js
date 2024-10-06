
document.querySelector('.sidebar2').classList.toggle('not');
document.querySelector('.sidebar').classList.toggle('not');
document.querySelector('.haml').addEventListener("click", () => {
    document.querySelector('.sidebar').classList.toggle('sow');
    document.querySelector('.body').classList.toggle('stop');
});
document.querySelector('.close').addEventListener("click", () => {
    document.querySelector('.sidebar').classList.toggle('sow');
    document.querySelector('.body').classList.toggle('stop');
});
document.querySelector('.haml2').addEventListener("click", () => {
    document.querySelector('.sidebar2').classList.toggle('sow');
    document.querySelector('.body').classList.toggle('stop');
});
document.querySelector('.close2').addEventListener("click", () => {
    document.querySelector('.sidebar2').classList.toggle('sow');
    document.querySelector('.body').classList.toggle('stop');
});
document.querySelector('.close3').addEventListener("click", () => {
    document.querySelector('.sidebar').classList.toggle('sow');
});
document.querySelector('.haml3').addEventListener("click", () => {
    document.querySelector('.sidebar2').classList.toggle('sow');
});
document.querySelector('.close4').addEventListener("click", () => {
    document.querySelector('.sidebar2').classList.toggle('sow');
});
document.querySelector('.haml4').addEventListener("click", () => {
    document.querySelector('.sidebar').classList.toggle('sow');
});
