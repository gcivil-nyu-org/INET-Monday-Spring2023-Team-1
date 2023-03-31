const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');
const errLs = document.getElementById('err_ls');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

if (errLs!=null){
  container.classList.add("right-panel-active");
}

// function checkDOMChange()
// {
//     // check for any new element being inserted here,
//     // or a particular node being modified

//     // call the function again after 100 milliseconds
//     setTimeout( checkDOMChange, 100 );
// }
const observer = new MutationObserver(function(mutations_list) {
	mutations_list.forEach(function(mutation) {
		mutation.addedNodes.forEach(function(added_node) {
			if(added_node.id == 'err_ls') {
				console.log('#child has been added');
        container.classList.add("right-panel-active");
				observer.disconnect();
			}
		});
	});
});


observer.observe(container, { subtree: true, childList: true });
