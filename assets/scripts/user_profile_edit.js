const signUpButton = document.getElementById('addDogProfile');
const signInButton = document.getElementById('addUserProfile');
const container = document.getElementById('container');

// signUpButton.addEventListener('click', () => {
//     console.log("here3");
//     container.classList.add("right-panel-active");
// });

// signInButton.addEventListener('click', () => {
//     container.classList.remove("right-panel-active");
// });


const upload = document.getElementById("upload");
const preview = document.getElementById("preview");
const avatar = document.getElementById("avatar");

const upload_human = document.getElementById("upload_human");
const preview_human= document.getElementById("preview_human");
const avatar_human = document.getElementById("avatar_human");


/** Handle uploading of files */
function handleFiles(upload, preview,avatar){
  console.log(upload)
  var files = upload.files;
  for (var i = 0; i < files.length; i++) {
    console.log('here')
    var file = files[i];
    var imageType = /^image\//;

    if (!imageType.test(file.type)) {
      avatar.classList.add("avatar--upload-error");
      setTimeout(function() {
        avatar.classList.remove("avatar--upload-error");
      }, 1200);
      continue;
    }

    avatar.classList.remove("avatar--upload-error");

    while (preview.firstChild) {
      preview.removeChild(preview.firstChild);
    }

    var img = document.createElement("img");
    img.file = file;
    img.src = window.URL.createObjectURL(file);
    img.className = "avatar_img";

    /* Clear focus and any text editing mode */
    document.activeElement.blur();
    window.getSelection().removeAllRanges();
    preview.appendChild(img);
  }
}

upload_human.addEventListener("change", ()=>{handleFiles(upload_human,preview_human, avatar_human)}, false);
// upload.addEventListener("change", handleFiles, false);