document.querySelectorAll('.add-to-cart').forEach(button => {
  button.addEventListener('click', e => {
    console.log(e.target);
    button.classList.add('added');
    setTimeout(() => 
      button.classList.remove('added')
    ,3000)
  });
});
