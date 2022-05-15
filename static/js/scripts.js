function alertMessage(bg,msg,selector) {
  selector.innerHTML += `<div class="alert ${bg} text-white alert-dismissible fade show" role="alert">
                              <div class="d-flex justify-content-between">
                                  <p class="p-1">${msg}</p>
                                  <button type="button" class="close m-2" data-dismiss="alert" aria-label="Close">
                                      <span aria-hidden="true">&times;</span>
                                  </button>	
                                  </div>											
                          </div>`
}

(function() {
    var currentDate = new Date()
      
    $('#detectBtn').click(function(e){
        e.preventDefault();
        var data_img = new FormData();
        const csrftoken = $('[name=csrfmiddlewaretoken]').val();
        data_img.append('myfile', $('#load_image')[0].files[0]);
        // Check if an Image is Uploaded      
        if (data_img.entries().next().value[1] !== 'undefined') {
          $.ajax({
            headers: {'X-CSRFToken': csrftoken},
            type: 'POST',
            beforeSend: function() {
              $('#ajax-loader').css('visibility','visible');
            },
            url: $(this).data('url'),
            processData: false,
            contentType: false,
            cache: false,
            mimeType: 'multipart/form-data',            
            data: data_img,
            success: function(result) {
                result = JSON.parse(result);
                console.log(result)
                
                if (result['status'] == 'true') {                    
                    $("#plateNo").text("Plate Number: " + result.plate);
                    $("#plateNoState").text(result.plate);
                    $("#access").html("<h1 class='text-success'><i class='fas fa-check'></i> Access Granted</h1>")
                    $("#license").text(result.plate);
                    $("#name").text(result.name);
                    $("#name_").text(result.name);
                    $("#age").text(result.age);
                    $("#model").text(result.model.toUpperCase());
                    $("#model_").text(result.model.toUpperCase());
                    $("#date").text(result.date);
                    $('#driverPassport').html('<img width="100" src="' + result.url + '" />'); 
                    $('#displayImgHolder').html('<img class="img-fluid img-thumbnail" src="'+result.imgurl+'" alt="Segmented Display"/>');
                    $('#displayImgHolder_').html('<img class="img-fluid img-thumbnail" src="'+result.roiurl+'" alt="Segmented Display"/>');
                } else {
                    // $('#displayImgHolder').html("<img class='img-fluid img-thumbnail' src='media/output.png' alt='Segmented Display'/>")                    
                    var selectors = ['#plateNoState','#access','#license','#name',"#name_","#age","#model","#model_","#date"]
                    selectors.forEach(idx => {
                        $(idx).text('None');
                    })
                    $("#plateNo").text("Plate Number: " + result.plate);
                    $('#driverPassport').html("<img width='100' src='static/assets/img/default.png' />");
                    $("#access").html("<h1 class='text-danger'><i class='fa fa-times'></i> Access Declined</h1>");
                    $('#displayImgHolder').html('<img class="img-fluid img-thumbnail" src="'+result.imgurl+'" alt="Segmented Display"/>');
                    $('#displayImgHolder_').html('<img class="img-fluid img-thumbnail" src="'+result.roiurl+'" alt="Segmented Display"/>');
                }
                // alertMessage("bg-success", "Uploaded Successfully!", $('#alert p'));
            },
            complete: function(result){
                // result = JSON.parse(result);  
                $('#ajax-loader').css('visibility','hidden');
                // $('#displayImgHolder').html('<img class="img-fluid img-thumbnail" src="'+result.imgurl+'" alt="Segmented Display"/>');
                // $('#displayImgHolder_').html("<img class='img-fluid img-thumbnail' src='media/License Plate.png' alt='License Display'/>");
            },       
          })
        } else {
          alert('Upload an Image!');
          alertMessage("bg-danger", "Please Upload and Image!", $('#alert p'))
        }
    })
  
  })()

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});


// Toggled Changed Password
function changePasswordToggled(psd, toggled_id) {
    var password = document.querySelector("#"+psd);
    var togglePsd = document.querySelector("#"+toggled_id);
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    togglePsd.classList.toggle('fa-eye-slash');
}
var load_image = document.querySelector("#load_image");
var imageDisplay = document.getElementById('display_image');
var imageDisplay_ = document.getElementById('displayImg');

// Display Uploaded Image
load_image.addEventListener("change", function(event) {
    imageDisplay.src = URL.createObjectURL(event.target.files[0]);
});