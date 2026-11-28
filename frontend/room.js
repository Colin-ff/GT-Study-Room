'use strict';
const $ = s => document.querySelector(s);
const features=[
{id:'video',title:'Video Listening',sub:'Watch closely. Listen deeply.',description:'Build listening skills with focused video practice.',image:'video.webp',ready:false},
{id:'speaking',title:'AI Speaking Partner',sub:'Speak with confidence',description:'Practise conversations and build speaking confidence.',image:'speaking.webp',ready:false},
{id:'papers',title:'Past paper practice',sub:'Cambridge 14–20',description:'Reading & Writing · 4 tests per book',image:'papers.webp',ready:true},
{id:'writing',title:'AI Writing Feedback',sub:'Improve your essays',description:'Review your writing and explore clearer ways to express your ideas.',image:'writing.webp',ready:false},
{id:'dictation',title:'Word & Sentence Dictation',sub:'Listen, type and remember',description:'Strengthen vocabulary and listening through dictation.',image:'dictation.webp',ready:false}];
let featureIndex=2,bookIndex=3;
const books=Array.from({length:7},(_,i)=>i+14);
function relativeIndex(index,active,count){let d=(index-active+count)%count;if(d>count/2)d-=count;return d}
function featureRender(){
const stage=$('#feature-stage'),w=stage.clientWidth;const width=w<500?188:224;const spread=Math.min(170,Math.max(40,(w-width*.64)/4-6));
[...$('#feature-cards').children].forEach((card,i)=>{const d=relativeIndex(i,featureIndex,features.length),a=Math.abs(d),scale=[1,.83,.64][a];card.querySelector('h3').textContent=d===0?features[i].title:({speaking:'AI Speaking',writing:'AI Writing',dictation:'Dictation',video:'Video Listening',papers:'Past papers'}[features[i].id]);card.style.transform=`translateX(${d*spread}px) scale(${scale}) rotateY(${-Math.sign(d)*(a===1?14:23)}deg)`;card.style.zIndex=String(5-a);card.style.setProperty('--label-offset',d<0?'-20px':d>0?'20px':'0px');card.style.opacity=a===2?'.85':'1';card.classList.toggle('is-active',d===0);card.setAttribute('aria-pressed',String(d===0));});
[...$('#feature-dots').children].forEach((b,i)=>b.setAttribute('aria-pressed',String(i===featureIndex)));
const f=features[featureIndex];$('#feature-title').textContent=f.title;$('#feature-description').textContent=f.description;$('#feature-open').hidden=!f.ready;$('#feature-planned').hidden=f.ready;
}
features.forEach((f,i)=>{const card=document.createElement('button');card.type='button';card.className='feature-card';card.dataset.feature=f.id;card.setAttribute('aria-label',f.title+(f.ready?' — available':' — coming soon'));card.innerHTML=`<img class="feature-image" src="assets/${f.image}" alt="" draggable="false"><h3>${f.title}</h3><small>${f.sub}</small><span class="card-badge ${f.ready?'available':''}">${f.ready?'Available now':'Coming soon'}</span>`;card.onclick=()=>{if(featureIndex===i&&f.ready)location.hash='library';else{featureIndex=i;featureRender()}};$('#feature-cards').append(card);const dot=document.createElement('button');dot.type='button';dot.setAttribute('aria-label','Select '+f.title);dot.onclick=()=>{featureIndex=i;featureRender()};$('#feature-dots').append(dot)});
$('#feature-prev').onclick=()=>{featureIndex=(featureIndex+4)%5;featureRender()};$('#feature-next').onclick=()=>{featureIndex=(featureIndex+1)%5;featureRender()};
function readRecord(book,test){try{return JSON.parse(localStorage.getItem(`cambridge-${book}-gt-test-${test}-v2`))}catch{return null}}
const wordCount=text=>(String(text??'').trim().match(/\S+/g)||[]).length;
function moduleProgress(record,mode){const attempt=record?.attempts?.[mode];if(attempt?.submittedAt)return 100;if(!(attempt?.deadline||attempt?.timerPaused)&&Array.isArray(record?.history)&&record.history.some(e=>e.module===mode))return 100;if(mode==='reading'){const count=Object.values(attempt?.answers||{}).filter(v=>String(v??'').trim()).length;return count||attempt?.deadline||attempt?.timerPaused?Math.min(100,count*2.5):null}const words=(attempt?.drafts||[]).map(wordCount);return words.some(Boolean)||attempt?.deadline||attempt?.timerPaused?50*(Math.min(1,(words[0]||0)/150)+Math.min(1,(words[1]||0)/250)):null}
function bookProgress(book){let found=false,total=0;for(let t=1;t<=4;t++){const r=readRecord(book,t);for(const mode of ['reading','writing']){const p=moduleProgress(r,mode);if(p!==null)found=true;total+=p||0}}return found?Math.round(total/8):null}
function renderBooks() {
  const width = $('#book-stage').clientWidth;
  const spread = Math.min(184, width * .225);
  const cardWidth = $('#book-cards').firstElementChild?.offsetWidth || 155;
  const edgeCenter = Math.min(2, Math.max(0, (width / 2 - cardWidth * .65 - 22) / spread));
  const visibleCenter = width < 600 ? bookIndex : Math.max(edgeCenter, Math.min(books.length - 1 - edgeCenter, bookIndex));
  [...$('#book-cards').children].forEach((card, index) => {
    const distance = index - bookIndex;
    const active = distance === 0;
    card.style.transform = `translateX(${(index - visibleCenter) * spread}px) scale(${active ? 1.10 : .95})`;
    card.style.setProperty('--book-yaw', active ? '18deg' : '27deg');
    card.style.zIndex = String(10 - Math.abs(distance));
    const visible = Math.abs(index - visibleCenter) <= 3;
    card.style.opacity = visible ? '1' : '0';
    card.style.visibility = visible ? 'visible' : 'hidden';
    card.classList.toggle('is-active', active);
    card.setAttribute('aria-pressed', String(active));
  });
  [...$('#book-numbers').children].forEach((button, index) => button.setAttribute('aria-pressed', String(index === bookIndex)));
  const number = books[bookIndex];
  $('#selected-title').textContent = 'Cambridge IELTS ' + number;
  $('#book-open').href = `books/cambridge-${number}-gt.html`;
  const progress = bookProgress(number);
  $('#book-progress').value = progress || 0;
  $('#book-progress-label').textContent = progress === null ? 'Not practised' : `${progress}% practised`;
  $('#book-prev').disabled = bookIndex === 0;
  $('#book-next').disabled = bookIndex === books.length - 1;
}
books.forEach((number, index) => {
  const card = document.createElement('button');
  card.type = 'button';
  card.className = 'book-card';
  card.setAttribute('aria-label', 'Select Cambridge IELTS ' + number);
  card.style.setProperty('--cover-hue', [30, -10, 305, 0, 45, 140, 330][index] + 'deg');
  card.innerHTML = `<span class="book-volume">
    <span class="book-face book-front"><img class="cover-art" src="assets/cover-art.webp" alt="" draggable="false"><span class="cover-label"><small>Cambridge</small><strong>IELTS</strong><em>General Training</em><b>${number}</b><span class="cover-foot">Reading & Writing</span></span></span>
    <span class="book-face book-spine" aria-hidden="true"><img class="binding-art" src="assets/cover-art.webp" alt="" draggable="false"><span class="spine-label">CAMBRIDGE IELTS</span><b>${number}</b></span>
    <span class="book-face book-back" aria-hidden="true"><img class="binding-art" src="assets/cover-art.webp" alt="" draggable="false"></span>
    <span class="book-face book-page-edge" aria-hidden="true"><img src="assets/book-pages.webp" alt="" draggable="false"></span>
    <span class="book-face book-top-edge" aria-hidden="true"><img src="assets/book-pages.webp" alt="" draggable="false"></span>
  </span>`;
  card.onclick = () => { bookIndex = index; renderBooks(); };
  $('#book-cards').append(card);
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = number;
  button.setAttribute('aria-label', 'Cambridge IELTS ' + number);
  button.onclick = () => { bookIndex = index; renderBooks(); };
  $('#book-numbers').append(button);
});
$('#book-prev').onclick=()=>{bookIndex=Math.max(0,bookIndex-1);renderBooks()};$('#book-next').onclick=()=>{bookIndex=Math.min(6,bookIndex+1);renderBooks()};
function bindSwipe(el,prev,next){let start=null,moved=false;el.addEventListener('pointerdown',e=>{if(e.button!==0)return;start={x:e.clientX,y:e.clientY,id:e.pointerId};moved=false});el.addEventListener('pointermove',e=>{if(start&&Math.abs(e.clientX-start.x)>12){moved=true;if(!el.hasPointerCapture(e.pointerId))el.setPointerCapture(e.pointerId)}});el.addEventListener('pointerup',e=>{if(!start)return;const dx=e.clientX-start.x,dy=e.clientY-start.y;if(Math.abs(dx)>35&&Math.abs(dx)>Math.abs(dy))dx<0?next():prev();start=null});el.addEventListener('pointerleave',()=>{start=null});el.addEventListener('pointercancel',()=>{start=null});el.addEventListener('click',e=>{if(moved){e.preventDefault();e.stopImmediatePropagation();moved=false}},true);el.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();e.key==='ArrowLeft'?prev():next()}})}
bindSwipe($('#feature-stage'),()=>$('#feature-prev').click(),()=>$('#feature-next').click());bindSwipe($('#book-stage'),()=>$('#book-prev').click(),()=>$('#book-next').click());
function route(){const library=location.hash==='#library';$('#home-view').hidden=library;$('#library-view').hidden=!library;document.title=library?'Your bookshelf · G Study Room':'G Study Room · IELTS General Training';document.querySelectorAll('[data-nav]').forEach(a=>{if(a.dataset.nav===(library?'library':'home'))a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});requestAnimationFrame(()=>{featureRender();renderBooks()});window.scrollTo(0,0)}
window.addEventListener('hashchange',route);window.addEventListener('resize',()=>{featureRender();renderBooks()});
function updateResume(){let latest=null;for(const n of books){for(let t=1;t<=4;t++){const r=readRecord(n,t);for(const mode of ['reading','writing']){const a=r?.attempts?.[mode];if(moduleProgress(r,mode)===null)continue;const timestamps=[a?.submittedAt,a?.deadline,...Object.values(a?.answerTimestamps||{}),...Object.values(a?.draftTimestamps||{}),...(r?.history||[]).filter(e=>e.module===mode).map(e=>e.submittedAt)].map(Number).filter(Number.isFinite);const stamp=Math.max(0,...timestamps);if(!latest||stamp>latest.stamp)latest={n,t,mode,stamp}}}}document.querySelectorAll('a.resume').forEach(a=>{a.href=latest?`tests/cambridge-${latest.n}-gt/test-${latest.t}.html?mode=${latest.mode}`:'#library'});if(latest){$('.library-resume').hidden=false;$('.library-resume').textContent=`Continue Cambridge ${latest.n} · Test ${latest.t}`;bookIndex=books.indexOf(latest.n)}}
$('#book-vocabulary').onclick=()=>{const n=books[bookIndex];vocabulary.open({title:`Cambridge IELTS ${n} vocabulary`,tests:Array.from({length:4},(_,i)=>({key:`cambridge-${n}-gt/test-${i+1}`,label:`Test ${i+1}`,url:`tests/cambridge-${n}-gt/test-${i+1}.html?mode=reading`}))})};
const dialog=$('#info-dialog');document.querySelectorAll('[data-dialog]').forEach(b=>b.onclick=()=>{const forum=b.dataset.dialog==='forum';$('#dialog-title').textContent=forum?'Forum · Coming soon':'A room for General Training';$('#dialog-copy').textContent=forum?'A place to discuss questions, share study experiences and learn together. The forum is being planned.':'G Study Room brings Cambridge IELTS General Training Reading and Writing practice into one quiet space. Your answers, vocabulary and notes are saved in your own browser. The four new study tools are planned features.';dialog.showModal()});document.querySelectorAll('.dialog-close,.dialog-done').forEach(b=>b.onclick=()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const b=dialog.getBoundingClientRect();if(e.clientX<b.left||e.clientX>b.right||e.clientY<b.top||e.clientY>b.bottom)dialog.close()}});
window.addEventListener('pageshow',()=>{updateResume();renderBooks()});window.addEventListener('storage',()=>{updateResume();renderBooks()});updateResume();route();
