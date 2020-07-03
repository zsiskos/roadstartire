// Required to convert UTC to local time

const orderedAtEl = document.querySelector('.order-detail-ordered-at');
const utcText = orderedAtEl.childNodes[1].nodeValue;
const utc_moment = moment.utc(utcText, "LLL");
const local_moment = utc_moment.local().format('LLL');
orderedAtEl.childNodes[1].nodeValue = local_moment;