const mail_items = document.querySelectorAll(".cover")
mail_items.forEach((item)=>{
    item.addEventListener("click", ()=>{
        var content = item.nextElementSibling
        var env_icon = item.firstElementChild.firstElementChild
        console.log(env_icon)
        if(content.classList.contains("content_expand")){
            content.classList.remove("content_expand")
            env_icon.classList.remove("fa-envelope-open")
            env_icon.classList.add("fa-envelope")
        }
        else{
            content.classList.add("content_expand")
            env_icon.classList.add("fa-envelope-open")
            env_icon.classList.remove("fa-envelope")
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


  const switchIcon = (container,newHtml, timeout) => {
  
    setTimeout(() => {
      container.innerHTML = ''
      setTimeout(() => {
        container.innerHTML = newHtml
      }, 200)
    }, timeout)
    
  }
  
  
