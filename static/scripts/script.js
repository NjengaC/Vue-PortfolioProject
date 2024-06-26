function showCompanies() {
    var companyList = document.getElementById("company-list");
    if (companyList.style.display === "none") {
        fetchCompaniesFromFile().then(function(companies) {
            populateCompanyList(companies);
            companyList.style.display = "block";
        });
    } else {
        // If the company list is visible, hide it
        companyList.style.display = "none";
    }
}

function fetchCompaniesFromFile() {
    return fetch("/static/companies.json") // Replace with actual endpoint
        .then(function(response) {
            if (!response.ok) {
                throw new Error("Failed to fetch companies");
            }
            return response.json();
        });
}

function populateCompanyList(companies) {
    var companyList = document.getElementById("company-list");
    // Clear existing list items
    companyList.innerHTML = "";
    // Populate the list with company names
    companies.forEach(function(company) {
        var listItem = document.createElement("li");
        listItem.textContent = company.name;
        companyList.appendChild(listItem);
    });
}
//this is for the home page 
function showRiders() {
	    var riderList = document.getElementById('rider-list');
	    if (riderList.style.display === 'none') {
		            riderList.style.display = 'block';
		        } else {
				        riderList.style.display = 'none';
 }
}
function showCompanies() {
    var companyList = document.getElementById("company-list");
    if (companyList.style.display === "none") {
        fetchCompaniesFromFile().then(function(companies) {
            populateCompanyList(companies);
            companyList.style.display = "block";
        });
    } else {
        // If the company list is visible, hide it
        companyList.style.display = "none";
    }
}

function fetchCompaniesFromFile() {
    return fetch("/static/companies.json") // Replace with actual endpoint
        .then(function(response) {
            if (!response.ok) {
                throw new Error("Failed to fetch companies");
            }
            return response.json();
        });
}

function populateCompanyList(companies) {
    var companyList = document.getElementById("company-list");
    // Clear existing list items
    companyList.innerHTML = "";
    // Populate the list with company names
    companies.forEach(function(company) {
        var listItem = document.createElement("li");
        listItem.textContent = company.name;
        companyList.appendChild(listItem);
    });
}
//this is for the home page 
function showRiders() {
	    var riderList = document.getElementById('rider-list');
	    if (riderList.style.display === 'none') {
		            riderList.style.display = 'block';
		        } else {
				        riderList.style.display = 'none';
 });

jQuery(function($) {
    $(window).on('scroll', function() {
		if ($(this).scrollTop() >= 200) {
			$('.navbar').addClass('fixed-top');
		} else if ($(this).scrollTop() == 0) {
			$('.navbar').removeClass('fixed-top');
		}
	});
	
	function adjustNav() {
		var winWidth = $(window).width(),
			dropdown = $('.dropdown'),
			dropdownMenu = $('.dropdown-menu');
		
		if (winWidth >= 768) {
			dropdown.on('mouseenter', function() {
				$(this).addClass('show')
					.children(dropdownMenu).addClass('show');
			});
			
			dropdown.on('mouseleave', function() {
				$(this).removeClass('show')
					.children(dropdownMenu).removeClass('show');
			});
		} else {
			dropdown.off('mouseenter mouseleave');
		}
	}
	
	$(window).on('resize', adjustNav);
	
	adjustNav();
}); 

