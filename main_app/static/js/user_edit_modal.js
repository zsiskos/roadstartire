// References on User Edit page
const btnSave = document.getElementById("btn-save");
const modalEditConfirm = document.getElementById("modal-edit-confirm"); 
const close = document.getElementById("close")

// SHOW THE MODAL
btnSave.addEventListener('click', () => {
  modalEditConfirm.style.display = 'block';
});

// CLOSE THE MODAL //
// 1. on the (x)
close.addEventListener('click', () => {
  modalEditConfirm.style.display = 'none';
});

// 2. outside the modal
window.onclick = function(event) {
  if (event.target == modalEditConfirm) {
    modalEditConfirm.style.display = "none";
  }
}