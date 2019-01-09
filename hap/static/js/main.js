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
          $('#image-preview').attr('src', e.target.result);
          $('#profpic-preview').attr('src', e.target.result);
          $('#settingsProfPic').attr('src', e.target.result);
      }
      
      reader.readAsDataURL(input.files[0]);
  }
}

$("#eventBanner-preview").change(function(){
  readURL(this);
});

$("#imageFile").change(function(){
  readURL(this);
});

$("#profPic").change(function(){
  readURL(this);
  document.getElementById("gettingstarted-btn").value = "Hop In";
});

$("#picture").change(function(){
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

;(function (factory) {
  if (typeof define === 'function' && define.amd) {
      // AMD. Register as an anonymous module.
      define(['jquery'], factory);
  } else {
      // Browser globals
      factory(jQuery);
  }
}) (function($) {
  $.fn.funcToggle = function(type, data) {
      var dname = "jqp_eventtoggle_" + type + (new Date()).getTime(),            
          funcs = Array.prototype.slice.call(arguments, 2),
          numFuncs = funcs.length,
          empty = function() {},
          false_handler = function() {return false;};

      if(typeof type === "object") {
          for( var key in type) {
              $.fn.funcToggle.apply(this, [key].concat(type[key]));
          }
          return this;
      }
      if($.isFunction(data) || data === false) {
          funcs = [data].concat(funcs);
          numFuncs += 1;
          data = undefined;
      }
      
      funcs = $.map(funcs, function(func) {
          if(func === false) {
              return false_handler;
          }
          if(!$.isFunction(func)) {
              return empty;
          }
          return func;
      });

      this.data(dname, 0);
      this.bind(type, data, function(event) {
          var data = $(this).data(),
              index = data[dname];
          funcs[index].call(this, event);
          data[dname] = (index + 1) % numFuncs;
      });
      return this;
  };
});

$(document).ready(function() {
  var followedInterests = new Array();

  var elements = document.getElementsByClassName("interestBtn");
  for (var i = 0, len = elements.length; i < len; i++) {
    var dict = {};

    dict['id'] = parseInt(elements[i].id);
    
    if(elements[i].classList.contains('followBtn')) {
      dict['bool'] = "False";
    }
    else if(elements[i].classList.contains('unfollowBtn')) {
      dict['bool'] = "True";
    }

    followedInterests.push(dict);
  }

  $('#followInterests').click(function(){
    for (i = 0; i < followedInterests.length; i++) { 
      if(followedInterests[i]["bool"] == "True") {
        req = $.ajax({
          url : '/follow',
          type : 'POST',
          data : { category_id : parseInt(followedInterests[i]["id"]) }
        });
      }
      else if(followedInterests[i]["bool"] == "False") {
        req = $.ajax({
          url : '/unfollow',
          type : 'POST',
          data : { category_id : parseInt(followedInterests[i]["id"]) }
        });
      }
    }
  });

  $('.followBtn').funcToggle('click', function() {
    var catId = $(this).attr('id');

    for (i = 0; i < followedInterests.length; i++) {
      if(followedInterests[i]["id"] == parseInt(catId)){
        followedInterests[i]["bool"] = "True";
      }
    }

    $(this).addClass('unfollowBtn').removeClass('followBtn');
    $(this).addClass('btn-warning').removeClass('btn-outline-warning');
  
  }, function() {
    var catId = $(this).attr('id');

    for (i = 0; i < followedInterests.length; i++) {
      if(followedInterests[i]["id"] == parseInt(catId)){
        followedInterests[i]["bool"] = "False";
      }
    }

    $(this).addClass('followBtn').removeClass('unfollowBtn');
    $(this).addClass('btn-outline-warning').removeClass('btn-warning');
  
  });
  
  $('.unfollowBtn').funcToggle('click', function() {
    var catId = $(this).attr('id');

    for (i = 0; i < followedInterests.length; i++) {
      if(followedInterests[i]["id"] == parseInt(catId)){
        followedInterests[i]["bool"] = "False";
      }
    }

    $(this).addClass('followBtn').removeClass('unfollowBtn');
    $(this).addClass('btn-outline-warning').removeClass('btn-warning');
  
  }, function() {
    var catId = $(this).attr('id');
    
    for (i = 0; i < followedInterests.length; i++) {
      if(followedInterests[i]["id"] == parseInt(catId)){
        followedInterests[i]["bool"] = "True";
      }
    }

    $(this).addClass('unfollowBtn').removeClass('followBtn');
    $(this).addClass('btn-warning').removeClass('btn-outline-warning');
  
  });  

});

$(document).ready(function() {
  $('.joinBtn').funcToggle('click', function() {
    var eventId = $(this).attr('event_id');
    var bottomBlock = $(this).attr('bottom_block');

    req = $.ajax({
      url : '/event/' + eventId + '/bottomblockaction=bb' + bottomBlock + '/join',
      type : 'POST',
      data : { event_id : parseInt(eventId) }
    });

    $(this).html('Unjoin')
    $(this).addClass('unjoinBtn').removeClass('joinBtn');
    $(this).addClass('btn-outline-secondary').removeClass('btn-outline-success');
    
    
  }, function() {
    var eventId = $(this).attr('event_id');
    var bottomBlock = $(this).attr('bottom_block');

    req = $.ajax({
      url : '/event/' + eventId + '/bottomblockaction=bb' + bottomBlock + '/unjoin',
      type : 'POST',
      data : { event_id : parseInt(eventId) }
    });

    $(this).html('Join')
    $(this).addClass('joinBtn').removeClass('unjoinBtn');
    $(this).addClass('btn-outline-success').removeClass('btn-outline-secondary');
  
  });
  
  $('.unjoinBtn').funcToggle('click', function() {
    var eventId = $(this).attr('event_id');
    var bottomBlock = $(this).attr('bottom_block');

    req = $.ajax({
      url : '/event/' + eventId + '/bottomblockaction=bb' + bottomBlock + '/unjoin',
      type : 'POST',
      data : { event_id : parseInt(eventId) }
    });

    $(this).html('Join')
    $(this).addClass('joinBtn').removeClass('unjoinBtn');
    $(this).addClass('btn-outline-success').removeClass('btn-outline-secondary');
  
  }, function() {
    var eventId = $(this).attr('event_id');
    var bottomBlock = $(this).attr('bottom_block');

    req = $.ajax({
      url : '/event/' + eventId + '/bottomblockaction=bb' + bottomBlock + '/join',
      type : 'POST',
      data : { event_id : parseInt(eventId) }
    });

    $(this).html('Unjoin')
    $(this).addClass('unjoinBtn').removeClass('joinBtn');
    $(this).addClass('btn-outline-secondary').removeClass('btn-outline-success');
  
  });  

});

$(document).click(function() {
  if(this != $(".dropdown-menu")[0]) {
    $(".dropdown").removeClass("show");
    $(".dropdown-menu").removeClass("show");
    $(".dropdown-toggle").attr("aria-expanded", "false");
  }
  else {
    $("#navbar-dropdown").addClass("show");
    $("#navbar-loginBox").addClass("show");
    $("#dropdownMenuButton").attr("aria-expanded", "true");
  }
});



