// Required to convert UTC to local time

const dateJoinedEl = document.getElementById('date-joined');
const orderedAtEls = document.querySelectorAll('.account-ordered-at');

const utcText = dateJoinedEl.innerText;
const utc_moment = moment.utc(utcText, "LLL");
const localMoment = utc_moment.local().format('LLL');
dateJoinedEl.innerHTML = localMoment;

orderedAtEls.forEach((el) => {
  // const utcText = el.innerText;
  const utcText = el.childNodes[1].nodeValue; // Need to extract date text this way to ignore parent text
  const utcMoment = moment.utc(utcText, "LLL");
  const localMoment = utcMoment.local().format('LLL');
  // el.innerHTML = localMoment;
  el.childNodes[1].nodeValue = localMoment;
});