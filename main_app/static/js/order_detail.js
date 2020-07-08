// Required to convert UTC to local time

const orderedAtEl = document.querySelector('.order-detail-ordered-at');
const utcText = orderedAtEl.childNodes[1].nodeValue;
const utc_moment = moment.utc(utcText, "LLL");
const local_moment = utc_moment.local().format('LLL');
orderedAtEl.childNodes[1].nodeValue = local_moment;

// ────────────────────────────────────────────────────────────────────────────────

// const orderStatusEls = document.querySelectorAll('.order-status')
// orderStatusEls.forEach((el) => {
//   if (el.innerText === 'In Progress') el.style.color = ('#1b66bb') // Blue
//   if (el.innerText === 'Cancelled') el.style.color = ('#e44e44') // Red
//   if (el.innerText === 'Fulfilled') el.style.color = ('#509553') // Green
// })