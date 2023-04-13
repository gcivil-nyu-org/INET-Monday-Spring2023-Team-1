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