window.onload = function() {
  const buttons = Array.from(document.querySelectorAll('.add-to-order'));

  buttons.forEach(b => {
    b.addEventListener('click', e => {

      const itemId = e.target.dataset.id;
      const csrfToken = e.target.dataset.csrf;
      console.log(e.target.previousElementSibling.lastElementChild.firstElementChild.lastElementChild.value)
      const quantity = e.target.previousElementSibling.lastElementChild.firstElementChild.lastElementChild.value;
      const body = {
        "id": itemId,
        "quantity": quantity,
      }

      // Make request to add to cart
      fetch(`${window.location.origin}/add-to-cart/`, {
        "headers": {
          "X-CSRFToken": csrfToken,
          "accept": "application/json",
          "content-type": "application/json",
        },
        "body": JSON.stringify(body),
        "method": "POST",
        "mode": "cors",
        "credentials": "include"
      }).then(data => {
        const done = e.target.querySelector('.pre-text-done');
        done.style.transform = "translate(0px)";
        setTimeout(()=>{
          done.style.transform = "translate(-110%) skew(-40deg)";
        },1200);
        console.log('Success:', data);
        setTimeout(()=>{
          location.reload()
        }, 1300);
      }).catch((error) => {
        console.error('Error:', error);
      });
    });
  });
}
