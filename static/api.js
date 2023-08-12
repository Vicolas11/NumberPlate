var togglePassword = document.querySelector('#togglePassword');
var signup = document.getElementById('register-form');
var signin = document.getElementById('signin-form');
var logout = document.getElementById('logout-btn');
var profileUpdate = document.getElementById('profile_update');
var changePassword = document.getElementById('changePassword');
var spinner = document.getElementById('ajax-loader');
var alertMsg = document.querySelector('#alert');
var alertCPMsg = document.querySelector('#alert_change_psw');
var alertDeleteMsg = document.querySelector('#alertDelete');
var alertText = document.querySelector('#alert p');
var alertDash = document.querySelector('#alertDash');
var alertDashText = document.querySelector('#alertDash p');
var detectBtn = document.getElementById('detectBtn');
var alertMsgAvatar = document.querySelector('#avatar-alert');


function alertMessage(bg, msg, selector) {
    selector.innerHTML += `<div class="alert ${bg} text-white alert-dismissible fade show" role="alert">
                                <div class="d-flex justify-content-between">
                                    <p class="p-1">${msg}</p>
                                    <button type="button" class="close m-2" data-dismiss="alert" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                    </button>	
                                    </div>											
                            </div>`
}

//TogglePassword
function myFunctionToggle() {
    var password = document.querySelector('#password');
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    togglePassword.classList.toggle('fa-eye-slash');
}

// Toggled Changed Password
function changePasswordToggled(psd, toggled_id) {
    var password = document.querySelector("#"+psd);
    var togglePsd = document.querySelector("#"+toggled_id);
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    togglePsd.classList.toggle('fa-eye-slash');
}

//TitleCase
String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};


// Application Programming Interface (API) ***************************************************
var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

var csrftoken = getCookie('csrftoken');

if (signup) {
    signup.addEventListener('submit', function(event) {
        event.preventDefault();
        let form = document.getElementById('register-form');
        let email = document.getElementById('email');
        let password = document.getElementById('password');
        let password2 = document.getElementById('compsd');
        let first_name = document.getElementById('first_name');
        let last_name = document.getElementById('last_name');
        let gender = document.getElementById('gender');
        let contact = document.getElementById('contact');

        var newData =   {
            "email": email.value,
            "password": password.value,
            "first_name": first_name.value.toProperCase(),
            "last_name": last_name.value.toProperCase(),
            "gender": gender.value,
            "contact": contact.value
        };

        var dataJson = JSON.stringify(newData);
        console.log(dataJson);
        if (password.value != password2.value) {
            alertMessage("bg-danger","Password does not match!",alertMsg);
        } else if (password.value.length < 8) {
            alertMessage("bg-danger","Password must not be less than 8 characters",alertMsg);
        }
        else {
            $.ajax({
                type: "POST",
                beforeSend: function() {
                    spinner.style.visibility = 'visible';
                },        
                url: "/api/user/register/",        
                data: dataJson,  
                success: function(result) {
                    console.log(result);
                    document.title = "Registered Student";
                    alertMessage("bg-success",`${result["message"]}`, alertMsg)
                    form.reset();
                },
                error: function (xhr, status, error) {
                    err = xhr.responseText.split("\"")[3].replace(/"|'/g,);
                    if (xhr["status"] === 400) {
                        alertMessage("bg-danger",`${err}`, alertMsg);
                    }                    
                    if (xhr["status"] === 500) {
                        alertMessage("bg-danger","Internal Server Error!", alertMsg);
                    }
                },
                complete: function(){
                    spinner.style.visibility = 'hidden';
                },
                dataType: "json",
                contentType: "application/json"
            });  
        }        
    });
};


/*
// Signin
if (signup) {
    signup.addEventListener('submit', function(event) {
        event.preventDefault();
        let form = document.getElementById('register-form');
        let email = document.getElementById('email');
        let password = document.getElementById('password');
        let first_name = document.getElementById('first_name');
        let last_name = document.getElementById('last_name');
        let gender = document.getElementById('gender');
        let contact = document.getElementById('contact');

        var newData =   {
            "email": email.value,
            "password": password.value,
            "first_name": first_name.value.toProperCase(),
            "last_name": last_name.value.toProperCase(),
            "gender": gender.value,
            "contact": contact.value
        };

        var dataJson = JSON.stringify(newData);
        console.log(dataJson);

        $.ajax({
            type: "POST",
            beforeSend: function() {
                spinner.style.visibility = 'visible';
            },        
            url: "signup-api",       
            data: dataJson,  
            success: function(result) {
                console.log(result);
                document.title = "User Registered";
                alertMessage("bg-success",`${result["message"]}`, alertMsg)
                window.location.href = `${window.location.origin}/signin`;
                form.reset();
            },
            error: function (error) {
                console.log(error);                
                if (error["status"] === 400) {
                   if (error["responseJSON"]["email"][0]) {
                        alertMessage("bg-danger", `This user ${email.value} already exist.`, alertMsg);
                    } 
                }
                if (error["status"] === 500) {
                    alertMessage("bg-danger","Internal Server Error!", alertMsg);
                }                
            },
            complete: function(){
                spinner.style.visibility = 'hidden';
            },
            dataType: "json",
            contentType: "application/json"
        });
    });
};
/*
// Signup
if (signin) {
    signin.addEventListener('submit', function(event) {
        event.preventDefault();
        let form = document.getElementById('signin-form');
        let email = document.getElementById('email');
        let password = document.getElementById('password');
            
        var newData = {
            "email": email.value,
            "password": password.value
        };

        var dataJson = JSON.stringify(newData);
        console.log(dataJson);

        $.ajax({
            type: "POST",
            beforeSend: function() {
                spinner.style.visibility = 'visible';
            },        
            url: "/user/api/signin",
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: dataJson,
            success: function(result) {
                console.log(result);
                console.log(result.token);
                if (result['success'] == "True") {
                    window.location.href = `${window.location.origin}/dashboard`;
                    // alert("User Login succefully!");                        
                } else {
                    window.location.href
                }                
                form.reset();
            },
            error: function (error) {
                if (error['status'] === 500) {
                    alertMessage("bg-danger", `${error["statusText"]}`, alertMsg)
                }
                console.log(error); 
                console.log(error["responseJSON"]["non_field_errors"][0]);
                alertMessage("bg-danger", `${error["responseJSON"]["non_field_errors"][0]}`, alertMsg);                                     
            },
            complete: function(){
                spinner.style.visibility = 'hidden';
            },
            dataType: "json",
            contentType: "application/json"
        });
    });
}
/*
//Signout
function signout() {
    $.ajax({
        type: "POST",
        beforeSend: function() {
            spinner.style.visibility = 'visible';
        },   
        url: "/user/api/sigout",
        headers: {
            'X-CSRFToken': csrftoken,
        },
        success: function(result) {
            console.log(result);
            redirect_path = `${window.location.origin}`
            window.location.href = redirect_path
        },
        error: function (error) {
            console.log(error);
            console.log(error["responseText"]);
            console.log(error["responseJSON"]["detail"]);
        },
        complete: function(){
            spinner.style.visibility = 'hidden';
        },
        dataType: "json",
        contentType: "application/json"
    });
}

//Update Profile
if (profileUpdate) {
    profileUpdate.addEventListener('submit', function(event) {
        event.preventDefault();
        let first_name = document.getElementById('first_name');
        let last_name = document.getElementById('last_name')
        let gender = document.getElementById('gender');
        let contact = document.getElementById('contact');

        var newData = {
            "first_name": first_name.value.toProperCase(),
            "last_name": last_name.value.toProperCase(),
            "gender": gender.value,
            "contact": contact.value,
        };
        var dataJson = JSON.stringify(newData);
        console.log(dataJson)
        $.ajax({
            type: "PUT",
            beforeSend: function() {
                spinner.style.visibility = 'visible';
            },  
            url: "/user/api/profile_update",
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: dataJson,
            success: function(result) {
                // alert("Profile Updated Updated Successfully!")
                alertMessage("bg-success", "Profile Updated Successfully!", alertMsg);
            },
            error: function (error) {
                console.log(error);
                if (error["responseJSON"]["old_password"][0]) {
                    alertMessage("bg-danger", `${error["responseJSON"]["old_password"][0]}`, alertMsg); 
                }
            },
            complete: function(){
                spinner.style.visibility = 'hidden';
            },
            dataType: "json",
            contentType: "application/json"
        });
    });   
}

// Change Password
if (changePassword) {
    changePassword.addEventListener('submit', function(event) {
        event.preventDefault();
        let form = document.getElementById('changePassword');
        let old_password = document.getElementById('old_password');
        let new_password = document.getElementById('new_password');
        let confirm_password = document.getElementById('confirm_password');            
        var newData = {
            "old_password": old_password.value,
            "password": new_password.value,
            "password2": confirm_password.value        
        };
        var dataJson = JSON.stringify(newData);

        if (new_password.value !== confirm_password.value) {
            alertMessage("bg-danger", "Password fields didn't match.", alertCPMsg);
        } else {
            $.ajax({
                type: "PUT",
                beforeSend: function() {
                    spinner.style.visibility = 'visible';
                },     
                url: "/user/api/change_password",
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: dataJson,
                success: function(result) {
                    // alert("Password Updated Successfully!")
                    alertMessage("bg-success","Password Updated Successfully!", alertCPMsg);
                    form.reset()
                    
                },
                error: function (error) {
                    console.log(error);
                    console.log(error["responseText"]);
                    if (error["responseJSON"]["old_password"][0]) {
                        alertMessage("bg-danger",`${error["responseJSON"]["old_password"][0]}`, alertCPMsg);
                    }
                    form.reset()
                },
                complete: function(){
                    spinner.style.visibility = 'hidden';
                },
                dataType: "json",
                contentType: "application/json"
            });    
        }
    });   
}*/

/*
if (detectBtn) {
    detectBtn.addEventListener('click', function(event) {
        event.preventDefault();

        if ( /\.(jpe?g|png|gif)$/i.test(imageDisplay.getAttribute("src")) === false) { 
            //Validating the Image Type
            alertMessage('bg-danger','image must be jpg/png/gif!', alertMsgAvatar); 
        } 
        // else if (input.files[0].size > 1048576) {
        //     alertMessage('bg-danger','Image file larger than 1MB!',alertMsgAvatar);
        // } 
        else {
            $.ajax({
                type: "POST",
                beforeSend: function() {
                    spinner.style.visibility = 'visible';
                },   
                url: "/user/api/detect/",
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                contentType: false,
                processData: false,
                data: imageDisplay.getAttribute("src"),
                success: function(result) {
                    console.log("result *************", result['avatar']);
                    imageTag.src = result['avatar'];
                    document.title = "Detected";              
                    alertMessage('bg-success','Detected Successfully!', alertMsgAvatar);
                    // console.log(input.files[0].size);
                },
                error: function (error) {
                    console.log(error);
                    console.log(error["responseJSON"]["detail"]);
                    alertMessage('bg-danger','Error in Detection!', alertMsgAvatar);
                    if (error.status === 500) alertMessage('bg-danger','Server Error!',alertMsgAvatar);
                },
                complete: function(){
                    spinner.style.visibility = 'hidden';
                },
            });            
        }
        form.reset();        
    });   
}*/