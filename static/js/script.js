function handleEvents() {
    document.addEventListener('click', function (event) {
        var target = event.target;
        if (target.tagName === 'I') {
            target = target.parentNode;
        }
        if (target.classList.contains('button-plus')) {
            handleQuantityChange(target, 1);
        } else if (target.classList.contains('button-minus')) {
            handleQuantityChange(target, -1);
        }
    });

    function handleQuantityChange(button, delta) {
        var input = button.closest('.input-spinner').querySelector("input[name='quantity']");
        var value = parseInt(input.value);
        if (!isNaN(value)) {
            var newValue = Math.max(value + delta, 1);
            input.value = newValue;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}

document.addEventListener('DOMContentLoaded', handleEvents);
document.body.addEventListener('htmx:afterOnload', handleEvents);

// if(window.location.href.includes("product")){

//     let reviewForm = document.querySelector("#addReviewForm")
//     if (reviewForm){
//         reviewForm.addEventListener("submit", function (event) {
//         $("#addReviewModal").modal("hide");
//         $(".modal-backdrop").remove();
//         });
//     }


// }
































// // some scripts

// // jquery ready start

// $(document).ready(function() {
// 	// jQuery code


//     /* ///////////////////////////////////////

//     THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
//     For sliders, interactions and other

//     */ ///////////////////////////////////////
    

// 	//////////////////////// Prevent closing from click inside dropdown
//     $(document).on('click', '.dropdown-menu', function (e) {
//       e.stopPropagation();
//     });


//     $('.js-check :radio').change(function () {
//         var check_attr_name = $(this).attr('name');
//         if ($(this).is(':checked')) {
//             $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
//             $(this).closest('.js-check').addClass('active');
//            // item.find('.radio').find('span').text('Add');

//         } else {
//             item.removeClass('active');
//             // item.find('.radio').find('span').text('Unselect');
//         }
//     });


//     $('.js-check :checkbox').change(function () {
//         var check_attr_name = $(this).attr('name');
//         if ($(this).is(':checked')) {
//             $(this).closest('.js-check').addClass('active');
//            // item.find('.radio').find('span').text('Add');
//         } else {
//             $(this).closest('.js-check').removeClass('active');
//             // item.find('.radio').find('span').text('Unselect');
//         }
//     });



// 	//////////////////////// Bootstrap tooltip
// 	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
// 		$('[data-toggle="tooltip"]').tooltip()
// 	} // end if




    
// }); 
// // jquery end



