document.addEventListener('DOMContentLoaded', function() {
	// Get references to the elements
	const addCategoryLabel = document.querySelector(
		'label[for="new_category_input"]'
	);
	const catInputBlock = document.querySelector(".cat-input-block");

	// Hide the cat-input-block initially
	catInputBlock.style.display = "none";

	// Show the catInputBlock when "Add a new category" label is clicked
	addCategoryLabel.addEventListener("click", function () {
		if (catInputBlock.style.display === "none") {
			catInputBlock.style.display = "block";
		} else {
			catInputBlock.style.display = "none";
		}
	});
});

const addNewCatBtn = document.querySelector(".add-new-cat");
const newCategoryInput = document.getElementById("new-category-input");

const updateSelectParentField = (jsonResponse) => {
    const parentCat = document.getElementById("parent-cat");
    const selectField = jsonResponse.selectField;
    if (parentCat) {
        let tempDiv = document.createElement("div");
        tempDiv.innerHTML = selectField;

        let newParentCat = tempDiv.getElementsByTagName("select")[0];
        parentCat.parentNode.replaceChild(newParentCat, parentCat);
    }
}

const updateCategoryField = (jsonResponse) => {
    const categoryList = document.getElementById('categories');
    const newCategoryId = 'newCategoryId' in jsonResponse ? jsonResponse.newCategoryId : null;
    const newCategoryName = 'newCategoryName' in jsonResponse ? jsonResponse.newCategoryName : null;
    const newCategoryParentId = 'newCategoryParentId' in jsonResponse ? jsonResponse.newCategoryParentId : null;

    if (categoryList) {
        const newCheckbox = document.createElement('li'); // Create the new checkbox HTML
        newCheckbox.innerHTML = `
            <input id="categories-${newCategoryId}" name="categories" type="checkbox" value="${newCategoryId}" checked>
            <label for="categories-${newCategoryId}">${newCategoryName}</label>
            `;
        
        // If the new category is a child category, find its parent category and move it above the new checkbox
        if (newCategoryParentId) {
            const parentCategoryCheckbox = document.getElementById(`categories-${newCategoryParentId}`);
    
            // Find the parent category's <li> element
            const parentCategoryListItem = parentCategoryCheckbox.parentNode;
    
            // Find the parent category's <ul> element
            const parentCategoryList = parentCategoryListItem.querySelector('ul');
    
            // Insert the new checkbox as a child of the parent category's <ul> element
            parentCategoryList.prepend(newCheckbox);
    
            // Find the last parent ancestor of the new category
            let lastParentAncestor = parentCategoryCheckbox;
            while (lastParentAncestor.closest('.isChild')) {
                lastParentAncestor = lastParentAncestor.closest('.isChild').closest('li');
            }
    
            categoryList.insertBefore(lastParentAncestor, categoryList.querySelector('li'));
        } else {
            // Insert the new checkbox at the top of the list
            categoryList.prepend(newCheckbox);
        }
    }
}

function ajaxAddNewCategory(formData) {
    let status
    // Make the AJAX request to your Flask route
    fetch('/rs-admin/ajax/new-category', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then((response) => {
            if (response.status === 401) {
                // Redirect to login page
                const currentPath = window.location.pathname + window.location.search;
                window.location.replace(`/rs-admin/login?next=${currentPath}`);
            } else if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((jsonResponse) => {
            handleNewCategoryResponse(jsonResponse)
        })
        .catch((error) => {
            msg = 'Error creating New Category. Please try again. <br> if error persist, please contact technical team';
            status = 'error';
            toggleAlert(msg, status)
            throw error;
        })
        .finally(() => {
            toggleLoading(addNewCatBtn);
        });
}

function handleNewCategoryResponse(jsonResponse) {
    let msg = jsonResponse['msg'];
    let status
    if (jsonResponse.success === true) {
        status = 'success';
        console.log('New Category Created');
        
        updateSelectParentField(jsonResponse)
        updateCategoryField(jsonResponse)
        toggleAlert(msg, status)

    } else {
        status = 'error';
        toggleAlert(msg, status)
    }
}

addNewCatBtn.addEventListener('click', (e) => {
    e.preventDefault();

    // Get the values of newCategoryInput and parentCat fields
    const newCategoryValue = newCategoryInput.value;
    const parentCat = document.getElementById('parent-cat').value;

    const formData = new FormData(); // Create the formData object
    formData.append('name', newCategoryValue);
    formData.append('parent-cat', parentCat);
    

    if (newCategoryValue.trim() === '') {
        toggleAlert('New Category field cannot be empty', 'error')
        newCategoryInput.classList.add('error');
        newCategoryInput.focus();
        return; // Exit the function
    }
    
    toggleLoading(addNewCatBtn);

    ajaxAddNewCategory(formData)
});