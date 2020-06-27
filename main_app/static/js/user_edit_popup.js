// References on User Edit page
const btnSave = document.getElementById("btn-save");
const popupEditConfirm = document.getElementById("popup-edit-confirm"); 
const close = document.getElementById("close")

// SHOW THE MODAL
btnSave.addEventListener('click', () => {
  popupEditConfirm.style.display = 'block';
});

// CLOSE THE MODAL //
// 1. on the (x)
close.addEventListener('click', () => {
  popupEditConfirm.style.display = 'none';
});

// 2. outside the modal
window.onclick = function(event) {
  if (event.target == popupEditConfirm) {
    poupEditConfirm.style.display = "none";
  }
}