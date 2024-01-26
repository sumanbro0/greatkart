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


	document.querySelectorAll('a[data-state]').forEach(function (link) {
		link.addEventListener('click', function () {
			document.querySelectorAll('a[data-state]').forEach(function (link) {
				link.classList.remove('active');
			});

			this.classList.add('active');

			sessionStorage.setItem('state', this.getAttribute('data-state'));
		});
	});

	var logoutLink = document.getElementById('logout-link');
	if (logoutLink) {
		logoutLink.addEventListener('click', function () {
			sessionStorage.clear();
		});
	}

function handleState() {
    var state = sessionStorage.getItem('state');
    var linkSelector = state ? `a[data-state="${state}"]` : 'a[data-state]';
    var link = document.querySelector(linkSelector);
    if (link) {
        if (state) {
            link.click();
        }
        link.classList.add('active');
    }
}

window.addEventListener('htmx:onLoad', handleState);
window.addEventListener('DOMContentLoaded', handleState);

	document.body.addEventListener('htmx:afterSwap', function (event) {
		if ($('.modal').hasClass('in')) {
			$('body').addClass('modal-open');
		} else {
			$('body').removeClass('modal-open');
			$('body').css('padding-right', '0');
		}
	});






















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



