const mail_items = document.querySelectorAll(".cover")
mail_items.forEach((item)=>{
    item.addEventListener("click", ()=>{
        var content = item.nextElementSibling
        var env_icon = item.firstElementChild.firstElementChild
        console.log(env_icon)
        if(content.classList.contains("content_expand")){
            content.classList.remove("content_expand")
            if(env_icon.classList.contains("fa-envelope-open")){
                env_icon.classList.remove("fa-envelope-open")
                env_icon.classList.add("fa-envelope")
            }
        }
        else{
            content.classList.add("content_expand")
            if(env_icon.classList.contains("fa-envelope")){
                env_icon.classList.add("fa-envelope-open")
                env_icon.classList.remove("fa-envelope")
            }

        }
    })
})

const add_icon = document.querySelector('.add_message')
const sending_container = document.querySelector('.sending_container')
const send_content = document.querySelector('.sending_content')
const sending_cover = document.querySelector('.sending_cover')
const dropdown_friend= document.querySelector('.dropdown-friend')
const recipient = document.querySelector('.recipient')
const sending_text = document.getElementById("sending_text")
var receiver=null
add_icon.addEventListener('click', ()=>{
    console.log('clicked')
    sending_container.classList.toggle('drop_down')
    sending_cover.classList.toggle('drop_down')
    console.log(sending_container.classList)
    send_content.classList.toggle('sending_content_expand')
    recipient.classList.toggle('expand')
    document.getElementById('recipient_warning').style.opacity='0'
    document.getElementById('content_warning').style.opacity='0'
    if(dropdown_friend.classList.contains('expand')){
        dropdown_friend .classList.remove('expand')
    }
});



recipient.addEventListener('click',()=>{
    console.log(dropdown_friend.classList)
    dropdown_friend .classList.toggle('expand')
})

// const friendNames = document.querySelectorAll(".dropdown-friend > ul > li")
// friendNames.forEach((friend)=>{
//     friend.addEventListener('click',()=>{
//         console.log(recipient.innerHTML)
        
//         recipient.innerHTML=friend.innerHTML
//     })

// })

send_content.addEventListener('click',()=>{
    console.log(dropdown_friend .classList)
    if(dropdown_friend.classList.contains('expand')){
        dropdown_friend.classList.remove('expand')
        console.log(dropdown_friend .classList)
    }
});

function friendName(name, friend){
    console.log(friend)
    receiver=friend
    recipient.innerHTML=name.innerHTML

}

function send_message(token){
    console.log(receiver)
    console.log(sending_text.value)
    error=false
    if(receiver==null){
        document.getElementById('recipient_warning').style.opacity='1'
        error=true
    }
    if(sending_text.value==''){
        document.getElementById('content_warning').style.opacity='1'
        return
    }
    if(error) return
    receiver_post = receiver
    receiver=null
    $.ajax({
        url: 'inbox',
        type: 'POST',
        data: { 
        csrfmiddlewaretoken: token,
        receiver: receiver_post,
        message: sending_text.value
        },
        success: function (res) {
            sending_container.classList.toggle('drop_down')
            sending_cover.classList.toggle('drop_down')
            console.log(sending_container.classList)
            send_content.classList.toggle('sending_content_expand')
            recipient.innerHTML=''
            recipient.classList.toggle('expand')
            sending_text.value=''
            document.getElementById('recipient_warning').style.opacity='0'
            document.getElementById('content_warning').style.opacity='0'
            if(dropdown_friend.classList.contains('expand')){
                dropdown_friend.classList.remove('expand')
            }
            switchIcon(document.getElementById('add_icon'), '<i class="fa fa-check-circle" aria-hidden="true"></i>', 100)
            switchIcon(document.getElementById('add_icon'), '<i class="fa-solid fa-circle-plus"></i>', 800)
            sending_text.value=''
            receiver= null
            return null
        }
    });
  }


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

var card_containers = document.querySelectorAll(".container");
var ulList = document.getElementById('message_list')


function accept_request(token, thisButton, group_id,mem_id){
// content= thisButton.parentElement
// card= content.parentElement
// container = content.parentElement.parentElement

// console.log(mem_id)
// console.log('list')
// ulList.removeChild(container.parentElement)
// console.log(ulList.children)
$.ajax({
    url: 'my-groups/',
    type: 'POST',
    data: { 
    csrfmiddlewaretoken: token,
    group_id: group_id,
    member_id: mem_id,
    status:'accept'
    },
    success: function (res) {
        content= thisButton.parentElement
        card= content.parentElement
        container = content.parentElement.parentElement
        cur_idx = index(container, card_containers)
        icon=card.firstElementChild.firstElementChild
        console.log(content)
        console.log(content.classList)
        setTimeout(() => {
            content.classList.toggle('content_expand')
          }, 500)
        setTimeout(() => {
            container.style.opacity='0'
            container.style.height='0 rem'
            ulList.removeChild(container.parentElement)
        }, 1000)
        // content.classList.toggle('content_expand')
        switchIcon(icon, '<i class="fa fa-check-circle" aria-hidden="true" style="color: green"></i>', 100)
        return null    
    }
});
}


function decline_request(token, thisButton, group_id,mem_id){
    // content= thisButton.parentElement
    // card= content.parentElement
    // container = content.parentElement.parentElement
    // icon=card.firstElementChild.firstElementChild
    // console.log(content)
    // console.log(content.classList)
    // setTimeout(() => {
    //     content.classList.toggle('content_expand')
    //   }, 500)
    // setTimeout(() => {
    //     container.style.opacity='0'
    // }, 1000)
    // // content.classList.toggle('content_expand')
    // switchIcon(icon, '<i class="fa fa-check-circle" aria-hidden="true" style="color: red"></i>', 100)
    // return null
    $.ajax({
        url: 'my-groups/',
        type: 'POST',
        data: { 
        csrfmiddlewaretoken: token,
        group_id: group_id,
        member_id: mem_id,
        status:'reject'
        },
        success: function (res) {
            content= thisButton.parentElement
            card= content.parentElement
            container = content.parentElement.parentElement
            cur_idx = index(container, card_containers)
            icon=card.firstElementChild.firstElementChild
            console.log(content)
            console.log(content.classList)
            setTimeout(() => {
                content.classList.toggle('content_expand')
              }, 500)
            setTimeout(() => {
                container.style.opacity='0'
                container.style.height='0 rem'
                ulList.removeChild(container.parentElement)
            }, 1000)
            // content.classList.toggle('content_expand')
            switchIcon(icon, '<i class="fa fa-check-circle" aria-hidden="true" style="color: red"></i>', 100)
            return null    
        }
    });
}

  const switchIcon = (container,newHtml, timeout) => {
  
    setTimeout(() => {
      container.innerHTML = ''
      setTimeout(() => {
        container.innerHTML = newHtml
      }, 200)
    }, timeout)
    
  }
  
  
