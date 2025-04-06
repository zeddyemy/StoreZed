(function() {
	("use strict");

	// Initialize Flow bite Accordions
	const accordionInstances = new Map();

	// Track all menu items
	let menuItems = new Map();

	// Initialize existing menu items from backend
	function initializeExistingItems() {
		document.querySelectorAll(".menu-item").forEach((itemEl) => {
			const item = {
				key: itemEl.dataset.key,
				ref_id: parseInt(itemEl.dataset.refId),
				type: itemEl.dataset.type,
				name: itemEl.querySelector(".menu-item-name").textContent,
				label: itemEl.querySelector("input[name='menu-item-name']")
					.value,
				parent_key: itemEl.querySelector(".parent-select").value || null,
				order:
					parseInt(itemEl.querySelector(".order-select").value) ||
					menuItems.size + 1,
				url: itemEl.querySelector(".menu-url-input")?.value || null,
				// Add database ID if it exists (for existing items)
				db_id: itemEl.dataset.dbId || null,
			};

			// Add to menuItems map
			menuItems.set(item.key, item);

			// Initialize Flow bite accordion
			const accordion = new Accordion(itemEl, {
				alwaysOpen: false,
				activeClasses: "bg-gray-100 dark:bg-gray-800",
				inactiveClasses: "",
			});
			accordionInstances.set(item.key, accordion);
		});
	}

	// Call this on DOM load
	document.addEventListener("DOMContentLoaded", () => {
        initializeExistingItems();
		initDragAndDrop();
		setupEventListeners();
	});

    function setupEventListeners() {

        // Add to menu button handler
        const menuAccordion = document.querySelector(".available-items");
        menuAccordion.addEventListener("click", (e) => {
            const target = e.target;

            const accordionItem = target.closest(".accordion-item");
            const accordionBody = accordionItem.querySelector(".accordion-content");
            const addToMenuBtn = accordionItem.querySelector(".add-to-menu-btn");

			const addBtn = target.closest(".add-to-menu-btn");
            
            if (target === addToMenuBtn) {
                e.preventDefault();
				const type = addBtn.dataset.type;
				addSelectedItems(type);
                return;
			}

            if (target.matches('input[type="checkbox"].select-all')) {
                const type = target.dataset.type
                
                const checkboxes = accordionItem.querySelectorAll(
					`input[data-type="${type}-checkbox"]`
				);
                

                checkboxes.forEach((checkbox) => {
					checkbox.checked = target.checked;
				});

                // Remove indeterminate state when manually toggled
                target.indeterminate = false;
                return;
            }

            // Handle individual checkbox changes
            if (target.matches('[data-type$="-checkbox"]')) {
                const type = target.dataset.type.replace('-checkbox', '');
                const selectAll = accordionItem.querySelector(`.select-all[data-type="${type}"]`);
                const checkboxes = accordionItem.querySelectorAll(
                    `[data-type="${type}-checkbox"]`
                );

                const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                const someChecked = Array.from(checkboxes).some(cb => cb.checked);

                selectAll.checked = allChecked;
                selectAll.indeterminate = !allChecked && someChecked;
            }
		});

        const menuItemsList = document.querySelector(".menu-items-list");
        menuItemsList.addEventListener("click", (e) => {
			const target = e.target;

			const removeItemBtn = target.closest(".remove-item-btn");

			if (target === removeItemBtn) {
				e.preventDefault();
				const menuItem = removeItemBtn.closest(".menu-item");
				const itemKey = menuItem.dataset.key;

				// Remove from UI
				menuItem.remove();

				// Remove from data stores
				menuItems.delete(itemKey);
				accordionInstances.delete(itemKey);

				// Update parent selectors
				updateParentSelectors();

				// Update orders
				updateItemOrders();
				toggleNoMenuMsg();
			}
		});

        menuItemsList.addEventListener("change", (e) => {
            const target = e.target;

			if (target.classList.contains('parent-select')) {
				const menuItem = target.closest(".menu-item");
				const itemKey = menuItem.dataset.key;
				const newParentKey = target.value;

				// Update selected attribute
				Array.from(target.options).forEach((option) => {
					option.removeAttribute("selected");
				});
				const selectedOption = Array.from(target.options).find(
					(opt) => opt.value === newParentKey
				);
				if (selectedOption) {
					selectedOption.setAttribute("selected", "selected");
				}

				// Update data structure
				const item = menuItems.get(itemKey);
				if (item) {
					item.parent_key = newParentKey || null;
				}

				// Move item in DOM
				moveItemToParent(menuItem, newParentKey);

				// Update order selects for both old and new parent contexts
				updateOrderSelectsForContext(menuItem);
			}

            const orderSelect = target.closest(".order-select");
            if (orderSelect) {
				const menuItem = orderSelect.closest(".menu-item");
				const newOrder = parseInt(orderSelect.value);
				const itemKey = menuItem.dataset.key;
				const item = menuItems.get(itemKey);

				// Update selected attribute
				Array.from(orderSelect.options).forEach((option) => {
					option.removeAttribute("selected");
				});
				const selectedOption = orderSelect.querySelector(
					`option[value="${newOrder}"]`
				);
				if (selectedOption) {
					selectedOption.setAttribute("selected", "selected");
				}

				// Find the correct container based on parent
				let container;
				if (item.parent_key) {
					const parentEl = document.querySelector(
						`[data-key="${item.parent_key}"]`
					);
					container = parentEl.querySelector(".children");
				} else {
					container = document.querySelector(".menu-items-list");
				}

				if (!menuItem || !container) return;

				// Get siblings from the correct container
				const siblings = Array.from(container.children);
				const totalItems = siblings.length;
				const currentIndex = siblings.indexOf(menuItem);

				// Calculate new index based on siblings count
				const newIndex = Math.min(
					Math.max(newOrder - 1, 0),
					totalItems - 1
				);

				// Get current total items BEFORE removal
				const allMenuItems = container.querySelectorAll(".menu-item");
				const currentItems = Array.from(allMenuItems);

				// Remove the item temporarily
				const clone = menuItem.cloneNode(true);
				menuItem.remove();

				// Insert at correct position
				if (newIndex >= siblings.length) {
					container.appendChild(clone);
				} else if (currentIndex > newIndex) {
					const nextItem = siblings[newIndex];
					container.insertBefore(clone, nextItem);
				} else {
					const nextItem = siblings[newIndex];
					container.insertBefore(clone, nextItem.nextSibling);
				}

				// Update orders and reinitialize
				updateOrderSelectsForContext(clone);

				const accordion = new Accordion(clone, {
					alwaysOpen: false,
					activeClasses: "",
					inactiveClasses: "",
				});
				accordionInstances.set(clone.dataset.id, accordion);

				reinitializeFlowBite();
			}
        });

        const saveBtn = document.querySelector(".structured-menu-foot .btn");
        
        if (saveBtn) {
			saveBtn.addEventListener("click", (e) => {
				e.preventDefault();
                try {
					toggleLoadingBtn(saveBtn); // Show loading state
                    saveMenu()
                } catch (error) {
                    toggleAlert("Network error - please try again", "error");
                    console.error("saving error:", error);
                } finally {
                    toggleLoadingBtn(saveBtn);
                }
			});
		}
    }

	function addSelectedItems(type) {

		const checkboxes = document.querySelectorAll(
			`[data-type="${type}-checkbox"]:checked`
		);

		if (type === "custom") {
            // Handle custom links
			const urlInput = document.querySelector("#custom-url");
			const textInput = document.querySelector("#custom-link-text");

			if (!urlInput.value || !textInput.value) {
				toggleAlert("URL and Link Text required", "error");
				return;
			}

			const refId = Date.now();
			const itemKey = `custom-${refId}`;
			const menuItem = {
				key: itemKey,
				ref_id: refId,
				type: type,
				name: textInput.value.trim(),
				label: textInput.value.trim(),
				url: urlInput.value,
				parent_key: null,
				order: menuItems.size + 1,
			};

			menuItems.set(itemKey, menuItem);
			renderMenuItem(menuItem);

			// Clear form
			urlInput.value = "";
			textInput.value = "";
		} else {
            // Handle checkboxes
            checkboxes.forEach((checkbox) => {
                const itemKey = `${checkbox.id}`;
				const refId = Number(itemKey.split('-').pop());
				
                if (!menuItems.has(itemKey)) {
                    const menuItem = {
						key: itemKey,
						ref_id: refId,
						type: type,
						name: checkbox.nextElementSibling.textContent.trim(),
						label: checkbox.nextElementSibling.textContent.trim(),
						parent_key: null,
						order: menuItems.size + 1,
					};
    
                    menuItems.set(itemKey, menuItem);
                    renderMenuItem(menuItem);
                }
            });
        }


        toggleNoMenuMsg();
        return;
	}

    function toggleNoMenuMsg() {
        const noMenuItems = document.querySelector(".no-menu-items");
        if (menuItems.size > 0) {
			noMenuItems.classList.add("hidden");
		} else {
			noMenuItems.classList.remove("hidden");
		}
    }

	function renderMenuItem(item) {
		const existingEl = document.querySelector(`[data-key="${item.key}"]`);
		if (existingEl) return;

		const itemHTML = `
            <div class="menu-item"
                data-key="${item.key}"
                data-type="${item.type}"
				data-ref-id="${item.ref_id}"
            >
				<div class="accordion border border-gray-400" data-accordion="collapse">
					<div class="item-header px-3 py-3 flex items-center justify-between gap-4 bg-gray-200">
						<span class="menu-item-name flex-1">${item.name}</span>
						<span class="menu-type"> ${item.type} </span>
						<span 
							data-accordion-target="#${item.key}-body"
							aria-expanded="false"
							aria-controls="${item.key}-body"
							class="menu-type cursor-pointer p-2"
						>
							<svg data-accordion-icon class="w-3 h-3 rotate-180 shrink-0" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
								<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5 5 1 1 5"/>
							</svg>
						</span>
					</div>

					<div id="${item.key}-body" class="item-body hidden px-3 py-2">
						<div class="form grid gap-4 sm:grid-cols-2 sm:gap-6 mb-4">
							<div class="form-group !mb-0 sm:col-span-2">
								<label for="" class="block mb-2 text-sm font-medium text-gray-500"> 
									Navigation Label
								</label>

								<input type="text"
									name="menu-item-name"
									value="${item.label}"
									class="form-control text-sm rounded-lg shadow-sm-light border dark:border-2 dark:focus:border-2 border-outline-clr focus:ring-theme-clr focus:border-theme-clr block w-full p-2 py-1.5 placeholder-gray-400 outline-none bg-gray-50 text-gray-900"
								>
							</div>

							<div class="form-group !mb-0">
								<label for="" class="block mb-2 text-sm font-medium text-gray-500">
									Menu Parent
								</label>

								<select name="parent-select" id="" class="parent-select form-control text-sm rounded-lg shadow-sm-light border dark:border-2 dark:focus:border-2 border-outline-clr focus:ring-theme-clr focus:border-theme-clr block w-full p-2 py-1.5 placeholder-gray-400 outline-none bg-gray-50 text-gray-900">
									<option value="">-- No Parent --</option>
									${Array.from(menuItems.values())
										.filter((i) => i.key !== item.key)
										.map(
											(i) =>
												`<option value="${i.key}">${i.name}</option>`
										)
										.join("")}
								</select>
							</div>

							<div class="form-group !mb-0">
								<label for="" class="block mb-2 text-sm font-medium text-gray-500">
									Menu Order
								</label>
								<select name="order-select" id="" class="order-select form-control text-sm rounded-lg shadow-sm-light border dark:border-2 dark:focus:border-2 border-outline-clr focus:ring-theme-clr focus:border-theme-clr block w-full p-2 py-1.5 placeholder-gray-400 outline-none bg-gray-50 text-gray-900">
									${Array.from(
										{
											length:
												document.querySelectorAll(
													".menu-item"
												).length + 1,
										},
										(_, i) => `
										<option value="${i + 1}" ${i + 1 === item.order ? "selected" : ""}>
											${i + 1}
										</option>
										`
									).join("")}
								</select>
							</div>
						</div>

						<div class="item-controls my-4">
							<a href="#" class="btn remove-item-btn border border-theme-danger-solid rounded-md py-1 px-4 text-sm text-alert-danger-solid hover:text-white hover:bg-theme-danger-solid">Remove</a>
						</div>
					</div>
				</div>
            </div>
        `;

		const container = document.querySelector(".menu-items-list");
		container.insertAdjacentHTML("beforeend", itemHTML);

		// Initialize Flow bite Accordion
		const newItem = document.querySelector(
			`[data-key="${item.key}"]`
		);
		const accordionOptions = {
			alwaysOpen: false,
			activeClasses: "",
			inactiveClasses: "",
		};

		const accordion = new Accordion(newItem, accordionOptions);
		accordionInstances.set(item.key, accordion);

		reinitializeFlowBite();

		// Update parent selectors
		updateParentSelectors();

		// Only update order selects for root level items
		updateRootOrderSelects();

		initDragAndDrop();
	}

	function updateRootOrderSelects() {
		const rootItems = document.querySelectorAll(
			".menu-items-list > .menu-item"
		);
		rootItems.forEach((rootItem, index) => {
			const orderSelect = rootItem.querySelector(".order-select");
			orderSelect.innerHTML = Array.from(
				{ length: rootItems.length },
				(_, i) => `
                <option value="${i + 1}" ${
					i + 1 === index + 1 ? "selected" : ""
				}>
                    ${i + 1}
                </option>
            `
			).join("");

			// Update menuItems data
			const itemKey = rootItem.dataset.key;
			const menuItem = menuItems.get(itemKey);
			if (menuItem) {
				menuItem.order = index + 1;
			}
		});
	}

	function moveItemToParent(itemEl, parentKey) {
		const container = document.querySelector(".menu-items-list");
		const parentEl = parentKey
			? document.querySelector(`[data-key="${parentKey}"]`)
			: null;

		if (parentEl) {
			// Check if parent already has a children container
			let childrenContainer = parentEl.querySelector(".children");
			if (!childrenContainer) {
				childrenContainer = document.createElement("div");
				childrenContainer.className = "children pl-8 pt-2 space-y-2";
				parentEl.appendChild(childrenContainer);
			}

			// Move item to children container
			childrenContainer.appendChild(itemEl);
		} else {
			// Move to root level if no parent
			container.appendChild(itemEl);
		}

		updateRootOrderSelects();
	}

    // Update parent selectors for all items
    function updateParentSelectors() {
        document.querySelectorAll('.parent-select').forEach(select => {
			const menuItem = select.closest(".menu-item");
			const currentKey = menuItem.dataset.key;
			const currentParentKey = select.value;
			const currentItemRefId = parseInt(menuItem.dataset.refId);
			const existingItems = Array.from(menuItems.values());

			// Clear existing options except "No Parent"
			select.innerHTML = '<option value="">-- No Parent --</option>';

			// Add options for all items except self and children
			const possibleParents = existingItems.filter((item) => {
				// Exclude self
				if (item.key === currentKey) return false;

				// Exclude children (to prevent circular references)
				let parent = menuItems.get(item.parent_key);
				while (parent) {
					if (parent.key === currentKey) return false;
					parent = menuItems.get(parent.parent_key);
				}
				return true;
			});
			possibleParents.forEach((item) => {
				const option = document.createElement("option");
				option.value = item.key;
				option.textContent = item.name;
				option.selected = item.key === currentParentKey;
				select.appendChild(option);
			});
		});
    }

	// Implement drag-and-drop with Sortable.js
	function initDragAndDrop() {
        const menuItemsList = document.querySelector(".menu-items-list");

        if (menuItemsList) {
			new Sortable(menuItemsList, {
				handle: ".drag-handle",
				animation: 150,
				onUpdate: (event) => updateItemOrders(),
			});
		}
	}

    // FUNCTION TO UPDATE ALL ORDER SELECTS
    function updateItemOrders() {
		const items = Array.from(document.querySelectorAll(".menu-item"));
		items.forEach((el, index) => {
            const order = index + 1;
			const orderSelect = el.querySelector(".order-select");
			const itemKey = el.dataset.key;
			const item = menuItems.get(itemKey);

			if (item) {
				item.order = order;
				orderSelect.value = order;
			}
			updateOrderSelectsForContext(el);
		});
	}

	function updateOrderSelectsForContext(menuItem) {
		const parentKey = menuItem.querySelector(".parent-select").value;
		let siblings;

		console.log("parentKey", parentKey);

		if (parentKey) {
			console.log("Has parentKey");
			// Get siblings under same parent
			const parentEl = document.querySelector(
				`[data-key="${parentKey}"]`
			);
			siblings = parentEl
				.querySelector(".children")
				.querySelectorAll(":scope > .menu-item");
		} else {
			console.log("No parentKey");
			// Get root level items
			siblings = document.querySelectorAll(
				".menu-items-list > .menu-item"
			);
		}

		// Update order selects for all siblings
		siblings.forEach((sibling, index) => {
			const orderSelect = sibling.querySelector(".order-select");
			orderSelect.innerHTML = Array.from(
				{ length: siblings.length },
				(_, i) =>
					`<option value="${i + 1}" ${
						i + 1 === index + 1 ? "selected" : ""
					}>${i + 1}</option>`
			).join("");

			// Update menuItems data
			const siblingKey = sibling.dataset.key;
			const siblingItem = menuItems.get(siblingKey);
			if (siblingItem) {
				siblingItem.order = index + 1;
			}
		});
	}

	// Reinitialize all accordions when new items are added
	function reinitializeFlowBite() {
		window.dispatchEvent(new Event("load"));
		window.dispatchEvent(new Event("resize"));
	}

    function saveMenu() {
		// re initialize menu items
		initializeExistingItems();

		// Convert menuItems Map to an array
		const itemsArray = Array.from(menuItems.values());

		// Include any additional properties if needed
		const payload = {
			items: itemsArray,
		};

		const navMenuSlug = document.querySelector(".manage-menus .menu-info")
			.dataset.menuSlug;

		fetch(`/api/admin/nav-menus/${navMenuSlug}/save-items`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(payload),
		})
			.then((response) => {
				if (!response.ok) {
					throw new Error("Error saving menu");
				}
				return response.json();
			})
			.then((data) => {
				toggleAlert(data.message, "success");
			})
			.catch((error) => {
				console.error(error);
				toggleAlert("Failed to save the navigation menu.", "error");
			});
	}
})();