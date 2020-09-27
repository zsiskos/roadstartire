document.querySelectorAll('.add-to-cart').forEach(button => {
  button.addEventListener('click', e => {
    console.log(e.target);
  
    const itemId = e.target.dataset.id;
    const quantity = e.target.previousElementSibling.value;

    // Start animation
    e.target.classList.add('added');

    // Make request to add to cart
    fetch(`${window.location.origin}/add-to-cart/?id=${itemId}&quantity=${quantity}`, {
      "headers": {
        "accept": "application/json",
        "content-type": "application/json",
      },
      "body": "csrfmiddlewaretoken=xuc39aPfpOSO20vGhkYWuunVmSKQFn4PP5UGy45fgZClS40mxiCUZy1rHkezlZf3&quantity=1&id=12&submit=ADD+TO+CART",
      "method": "POST",
      "mode": "cors",
      "credentials": "include"
    });
  });
});
