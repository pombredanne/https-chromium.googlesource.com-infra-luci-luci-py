import './index.js'

(function(){

let display = document.getElementById('display');
// listen to event
document.addEventListener('sort-change', (e) => {
  console.log('sort change');
  let scs = document.querySelectorAll('sort-toggle');
  for (let i = 0; i < scs.length; i++) {
    scs[i].current = e.detail.key;
  }
});
})();