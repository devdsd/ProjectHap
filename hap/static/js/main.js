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