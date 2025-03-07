(function () {
    const tagsBox = document.getElementById('tag-list');
    const addTagBtn = document.getElementById('add-tag-btn');
    const tagsInput = document.querySelector('input[name="prod_tags_entry"]');
    const productTagsInput = document.querySelector('input[name="product_tags"]'); // hidden input
    const suggsBox = document.getElementById('tag-suggestions');
    
    // keep track of the currently selected suggestion
    let selectedIndex = -1;
    
    const handleClickOutside = (e) => {
        if (!suggsBox.contains(e.target)) {
            suggsBox.classList.add('hidden');
        }
    }
    
    // Function to add a tag to the tagsInput field
    const addTagToInput = (tag) => {
        const values = tagsInput.value.split(',').map(value => value.trim());
        values[values.length - 1] = `${tag}, `;
        tagsInput.value = values.join(', ');
    
        hideSuggestions();
        tagsInput.focus();  // Keep focus on the tagsInput field
    }
    
    // Function to fetch tag suggestions from the server based on user input
    const fetchTagSuggestions = async (input) => {
        try {
            const response = await fetch(
				`/api/admin/tags/suggestions?term=${input}`
			);
            if (!response.ok) {
                throw new Error('Failed to fetch tag suggestions');
            }
            const data = await response.json();
            
            return data.data.suggestions;
        } catch (error) {
            console.error(error);
            return [];
        }
    }
    
    // Function to display tag suggestions
    const showTagSuggestions = (suggestions) => {
        suggsBox.innerHTML = ''; // Clear any existing suggestions
        if (suggestions.length === 0) {
            hideSuggestions();
        } else {
            suggsBox.classList.remove('hidden');
            // Create and append suggestion elements
            suggestions.forEach(suggestion => {
                const suggestionElement = createSuggestionElement(suggestion);
                suggsBox.appendChild(suggestionElement);
            });
        }
    }
    const createSuggestionElement = (suggestion) => {
        const suggestionElement = document.createElement('li');
        suggestionElement.classList.add('tag-suggestion');
        suggestionElement.textContent = suggestion;
        suggestionElement.addEventListener('click', () => {
            addTagToInput(suggestion);
            suggsBox.innerHTML = '';
        });
        return suggestionElement;
    }
    
    // Function to add a tag to hidden input and tagsBox
    const addTag = (tag) => {
        // Check if the tag already exists in tagsBox
        const existingTagElements = Array.from(tagsBox.getElementsByClassName('title'));
        const existingTags = existingTagElements.map(element => element.textContent);
        if (existingTags.includes(tag)) {
            return; // Skip adding the duplicate tag
        }
    
        const tagContent = `
            <span title="${tag}" class="title">${tag}</span>
            <button aria-label="Remove ${tag}" class="tag-del-btn btn inline-flex items-center"></button>
        `;
    
        const tagElement = document.createElement('div');
        tagElement.classList.add(
			"tag-list-item",
			"inline-flex",
			"gap-2",
            "items-center",
		);
        tagElement.innerHTML = tagContent;
        tagsBox.appendChild(tagElement);
    
        // Get the existing tag values from the hidden input
        const existingTagValues = productTagsInput.value.split(',').map(value => value.trim()).filter((tag) => tag.trim() !== '');
    
        // Check if the tag already exists in productTagsInput and skip adding duplicate
        if (existingTagValues.includes(tag)) {
            return;
        }
    
        const allTags = existingTagValues.concat(tag); // Concatenate the existing tags with the new tag
        productTagsInput.value = allTags.join(', '); // Update the value of the hidden input with all the tags
    }
    const removeTag = (tagElement) => {
        const tagTextElement = tagElement.querySelector('.title');
        const tagText = tagTextElement.textContent;
        tagsBox.removeChild(tagElement);
    
        // Update the hidden input value by removing the tag
        const tags = productTagsInput.value.split(',').filter((tag) => tag.trim() !== tagText);
        productTagsInput.value = tags.join(',');
    }
    
    const handleAddTag = async (e) => {
        e.preventDefault();
        const tagValue = tagsInput.value.trim();
        if (tagValue !== '') {
            const tags = tagValue.split(',').map((tag) => tag.trim()).filter((tag) => tag !== '');
            tags.forEach(addTag);
            tagsInput.value = '';
            tagsInput.focus();
        }
    }
    
    const handleTagInput = async (e) => {
        const values = e.target.value.split(',');
        const lastValue = values[values.length - 1].trim();
        const inputValue = tagsInput.value.trim();
    
        suggsBox.innerHTML = ''; // Clear existing suggestions
        hideSuggestions();
        selectedIndex = -1;
    
        if (lastValue.length >= 2) {
            const suggestions = await fetchTagSuggestions(lastValue);
            showTagSuggestions(suggestions);
        }
    }
    
    const handleTagInputKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            selectedIndex = (selectedIndex + 1) % suggsBox.children.length; // Move the selection down the list
        } else if (e.key === 'ArrowUp') {
            // Move the selection up the list
            selectedIndex = (selectedIndex - 1 + suggsBox.children.length) % suggsBox.children.length;
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIndex > -1) {
                const suggestion = suggsBox.children[selectedIndex].textContent;
                addTagToInput(suggestion);
                suggsBox.innerHTML = '';
                selectedIndex = -1;
            } else {
                handleAddTag(e);
            }
        }
    
        updateSelectedSuggestions();
    }
    const updateSelectedSuggestions = () => {
        const suggestionElements = suggsBox.getElementsByClassName('tag-suggestion');
        Array.from(suggestionElements).forEach((element, index) => {
            element.classList.toggle('selected', index === selectedIndex);
        });
    }
    
    const handleSuggestionMouseOver = (e) => {
        const suggestionElements = suggsBox.getElementsByClassName('tag-suggestion');
        Array.from(suggestionElements).forEach((element, index) => {
            if (element === e.target) {
                selectedIndex = index;
                element.classList.add('selected');
            } else {
                element.classList.remove('selected');
            }
        });
    }
    
    const handleSuggestionMouseOut = () => {
        const suggestionElements = suggsBox.getElementsByClassName('tag-suggestion');
        Array.from(suggestionElements).forEach(element => {
            element.classList.remove('selected');
        });
    }
    
    const handleTagContainerClick = (e) => {
        const clickedElement = e.target;
        if (clickedElement.classList.contains('tag-del-btn')) {
            removeTag(clickedElement.parentNode);
        }
    }
    
    const hideSuggestions = () => {
        suggsBox.innerHTML = '';
        suggsBox.classList.add('hidden');
    }
    
    document.addEventListener('click', handleClickOutside);
    addTagBtn.addEventListener('click', handleAddTag); // Event listener for the Add Tag button
    tagsInput.addEventListener('input', handleTagInput); // Event listener for tag input changes
    tagsInput.addEventListener('keydown', handleTagInputKeyDown); // Event listener for key press on tag input
    suggsBox.addEventListener('mouseover', handleSuggestionMouseOver); // Event listener for mouseover on suggestion elements
    suggsBox.addEventListener('mouseout', handleSuggestionMouseOut);// Event listener for mouseout on suggestion elements
    tagsBox.addEventListener('click', handleTagContainerClick);
})();