window.onload = function() {
  const button = document.querySelector('#add-tire').getElementsByClassName('order-btn-filled')[0];
  console.log(button);

  button.addEventListener('click', e => {
    console.log('clicked')
    const done = e.target.querySelector('.pre-text-done');
    done.style.transform = "translate(0px)";
    setTimeout(()=>{
      done.style.transform = "translate(-110%) skew(-40deg)";
    },1200);
    setTimeout(()=>{
      document.forms['add-tire'].submit()
    }, 1300);
  })
}