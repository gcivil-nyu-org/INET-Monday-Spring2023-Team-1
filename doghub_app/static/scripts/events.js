const navs = document.querySelectorAll(".side-bar > ul > li");

navs.forEach((nav) => {
  nav.addEventListener("click", (e) => {
    document.querySelector(".nav-tab.active").classList.remove("active");
    nav.classList.add("active");

    // Hide active nav view
    document
      .querySelector('div[data-view-active="true"]')
      .setAttribute("data-view-active", false);

    const nav_view = nav.getAttribute("data-view-name");
    document
      .querySelector(`.${nav_view}`)
      .setAttribute("data-view-active", true);
  });
});



var registerBtnClicked=false;
var registered=false;
const registerBtns=document.querySelectorAll(".registerBtn")
  registerBtns.forEach((b)=>{
    b.addEventListener("click",()=>{
      registerBtnClicked=true;
      console.log(b.classList)
      console.log(b.firstChild)
      if(b.classList.contains('registered')){
        console.log("clicked_reg")
        b.firstChild.classList.remove('fa-solid');
        b.firstChild.classList.add('fa-regular');
        registered=false;
        b.classList.remove('registered')
        b.style.backgroundColor="#6f36a8"
        b.childNodes[1].nodeValue="RSVP"
      }
      else{   
        console.log(b.firstChild)
        b.firstChild.classList.remove('fa-regula');
        b.firstChild.classList.add('fa-solid');
        b.classList.add('registered')
        registered=true;
        b.style.backgroundColor="#5886a8"
        b.childNodes[1].nodeValue="Registered"
      }
    })
  })



function index(el,cards) {
    i = 0;
    console.log(cards)
    for (; i < cards.length; i++) {
        if (cards[i] == el) {
            return i;
        }
    }
    return -1;
}

const card_containers = document.querySelectorAll(".card");

const card_inners = document.querySelectorAll(".card-inner");
card_inners.forEach((card)=>card.addEventListener("click",(e)=>{
  if(registerBtnClicked){
    reg_icon= card.firstElementChild.nextElementSibling.firstElementChild.firstElementChild.nextElementSibling.firstElementChild
    console.log(registered)
    registerBtnClicked=false;
    if(registered){
      reg_icon.classList.remove('fa-regular');
      reg_icon.classList.add('fa-solid');
    }
    else{
      reg_icon.classList.add('fa-regular');
      reg_icon.classList.remove('fa-solid');
    }
    return
  }
  var back_content= card.firstElementChild.nextElementSibling
  var curInd = index(card, card_inners);
  var curCard = card_containers[curInd]
  if(card.classList.contains('flipped')){
    card.classList.remove('flipped')
    card.classList.add('flipped_back')
    curCard.classList.remove('card_flipped')
    curCard.classList.add('card_flipped_back')
    back_content.classList.add('back_content_flipped_back')
    back_content.classList.remove('back_content_flipped')
  }
  else{
    card.classList.add('flipped')
    card.classList.remove('flipped_back')
    console.log(card.classList);
    curCard.classList.add('card_flipped')
    curCard.classList.remove('card_flipped_back')
    back_content.classList.add('back_content_flipped')
    back_content.classList.remove('back_content_flipped_back')
  } 
}));

