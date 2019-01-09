/*
This script will toggle the modal which includes the iframe for customizing items toppings
when an item has been selected to add to order or to edit the item that has already
been added to the order
*/

var addButtons = $("[id=customize-item-modal]")
var iFrame = document.getElementById("add-item-toppings-iframe");
var modalTitle = document.getElementById("exampleModalCenterTitle");

addButtons.click(function(){
  // the name attribute is the item
  modalTitle.innerHTML = `Customize your ${this.name}`

  if (this.getAttribute('class') == "btn btn-link add-item")
    type = 'add'
  else
    type = 'edit'

  // the value attribute is the item.id
  iFrame.setAttribute('src', `/orders/customize/${this.value}/${type}/`)
  console.log(iFrame.getAttribute('src'))
})
