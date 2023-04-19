const tabBtn = document.querySelectorAll(".nav ul li");
const tab = document.querySelectorAll(".tab");
function tabs(panelIndex) {
  tab.forEach(function (node) {
    node.style.display = "none";
  });
  tab[panelIndex].style.display = "block";
  tabBtn.forEach(function (node) {
    if (node.classList.contains("active")) {
      node.classList.remove("active");
    }
  });
  tabBtn[panelIndex].classList.add("active");
}

tabBtn.forEach((el) => el.click());
tabs(0);

let bio = document.querySelector(".bio");
const bioMore = document.querySelector("#see-more-bio");
const bioLength = bio.innerText.length;
let collapped = false;

function bioText() {
  if (collapped) {
    bio.innerText = bio.innerText.substring(0, bio.innerText.length - 8);
  }
  bio.oldText = bio.innerText;
  if (bio.oldText.length > 100) {
    bio.innerText = bio.innerText.substring(0, 100) + "...";
    bio.innerHTML += `<span onclick='addLength()' id='see-more-bio'>See More</span>`;
  }
}

bioText();

function addLength() {
  collapped = true;
  bio.innerText = bio.oldText;
  bio.innerHTML +=
    "&nbsp;" + `<span onclick='bioText()' id='see-less-bio'>See Less</span>`;
}
// if (document.querySelector(".alert-message").innerText > 9) {
//   document.querySelector(".alert-message").style.fontSize = ".7rem";
// }

const followBtn = document.getElementById("follow-user");
followBtn.addEventListener("click", () => {
  if (document.getElementById("follow_icon") != null) {
    //Action: follow user
    followBtn.innerHTML = "Following";
  } else {
    //Action: unfollow user
    followBtn.innerHTML =
      '<i id="follow_icon" class="fa fa-plus" aria-hidden="false"></i> Follow';
  }
});

const container = document.querySelectorAll(".proflist--item");
const toggle = document.querySelectorAll(".toggle");
console.log(toggle);

function index(el, toggle) {
  i = 0;
  console.log(toggle);
  for (; i < toggle.length; i++) {
    if (toggle[i] == el) {
      return i;
    }
  }
  return -1;
}
toggle.forEach((el) =>
  el.addEventListener("click", () => {
    console.log("here");
    var ind = index(el, toggle);
    console.log(container);
    container[ind].classList.toggle("active");
  })
);

const pop = document.getElementById("pop-up");
function funcWind() {
  pop.classList.add("wind_height");
  console.log(pop);
}

function closeWind() {
  pop.classList.remove("wind_height");
  console.log(pop);
}

const editPasswordBtn = document.querySelector("#edit-password-btn");
const passwordChangeFields = document.querySelector("#password-change-fields");
editPasswordBtn.addEventListener("click", () => {
  passwordChangeFields.style.display = "block";
});

setTimeout(function () {
  var messages = document.getElementsByClassName("message")[0];
  messages.parentNode.removeChild(messages);
}, 3000);

function archiveFunction() {
  event.preventDefault(); // prevent form submit
  var form = event.target.form; // storing the form
  swal(
    {
      title: "Are you sure?",
      text: "But you will still be able to retrieve this file.",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Yes, archive it!",
      cancelButtonText: "No, cancel please!",
      closeOnConfirm: false,
      closeOnCancel: false,
    },
    function (isConfirm) {
      if (isConfirm) {
        form.submit(); // submitting the form when user press yes
      } else {
        swal("Cancelled", "Your imaginary file is safe :)", "error");
      }
    }
  );
}
