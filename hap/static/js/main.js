function checkForm(form)
{
  form.deleteBtn.disabled = true;
  return true;
}

function readURL(input) {
  if (input.files && input.files[0]) {
      var reader = new FileReader();
      
      reader.onload = function (e) {
          $('#eventBanner-preview').attr('src', e.target.result);
      }
      
      reader.readAsDataURL(input.files[0]);
  }
}

$("#imageFile").change(function(){
  readURL(this);
});

function count_up(obj) {
  var count = document.getElementById("countEventNameChar")
  document.getElementById("count-cont").style.display = "block";
  count.style.color = "red";
  count.innerHTML = obj.value.length;
  if(obj.value.length > 2) {
    count.style.color = "gray";
  }
  if(obj.value.length > 80) {
    count.style.color = "red";
  }
}