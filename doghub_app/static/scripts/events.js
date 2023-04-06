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
        b.firstChild.classList.remove('fa-solid');
        b.firstChild.classList.add('fa-regular');
        registered=false;
        b.classList.remove('registered')
        b.style.backgroundColor="#6f36a8"
        
      }
      else{   
        b.firstChild.classList.remove('fa-regula');
        b.firstChild.classList.add('fa-solid');
        b.classList.add('registered')
        registered=true;
        b.style.backgroundColor="#5886a8"
      }
    })
  })

const cards = document.querySelectorAll(".card-inner");
cards.forEach((card)=>card.addEventListener("click",(e)=>{
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

  if(card.classList.contains('flipped')){
    card.classList.remove('flipped')
    card.classList.add('flipped_back')
  }
  else{
    card.classList.add('flipped')
    card.classList.remove('flipped_back')
    console.log(card.classList);
  } 
}));
