const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');
const errLs = document.getElementById('err_ls');
const signUpPostBtn = document.getElementById('signUpPost');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

if (errLs!=null){
  container.style.animation="0.1s";
  container.classList.add("right-panel-active");

}
// signUpPostBtn.addEventListener('click',()=>{
//   const formData = new FormData();
//   // console.log(formData)
//   formData.append('reg_uemail',document.getElementById('reg_uemail').value )
//   formData.append('reg_psw',document.getElementById('reg_psw').value )
//   console.log(document.getElementById('reg_uemail').value)
//   console.log(formData)
//   const request = new XMLHttpRequest();
//   request.open("POST", '/register');
//   csrftoken=document.getElementsByName('csrfmiddlewaretoken')[0].value;
//   request.setRequestHeader("X-CSRFToken", csrftoken); 
//   request.setRequestHeader("Content-Type", "text/plain;charset=UTF-8"); 
//   request.send();
// })



const observer = new MutationObserver(function(mutations_list) {
	mutations_list.forEach(function(mutation) {
		mutation.addedNodes.forEach(function(added_node) {
			if(added_node.id == 'err_ls') {
        document.querySelector('.container.right-panel-active .sign-up-container ').transition="0.1s"
        container.classList.add("right-panel-active");
				observer.disconnect();
			}
		});
	});
});


observer.observe(container, { subtree: true, childList: true });
