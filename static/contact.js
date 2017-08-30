"use strict";

function showContact(results) {
  var contact = results.contact;
  var events = results.events;
  var interests = results.interests;

  $("#searchResults").html("<h3>" + contact.fname + " " + contact.lname + "</h3>");
  $("#searchResults").append("<h4>Events</h4>");

  events.forEach(function(evt) {
    $("#searchResults").append("<a href='/' data-event-id=" + evt.event_id + " class='event-link'>" + evt.event_name + "</a> - " + evt.date + "<br/>");
  });

  $("#searchResults").append("<h4>Interests <button type='button' class='interest-button btn btn-info btn-lg' data-toggle='modal' data-contact-id='" + contact.contact_id + "' data-target='#addInterest'>Add Interest</button></h4>");

  interests.forEach(function(interest) {
    $("#searchResults").append(interest.name + "<br/>");
  });

}

function getContact(event) {
  event.preventDefault();
  var contactId = {"contact": $(this).data("contactId")};
  // console.log(contactId)

  $.get("/contact.json", contactId, showContact);

}

// $(".contact-link").on("click", getContact);
$(document).on("click", ".contact-link", getContact);








$(".interest-button").on("click", function () {
  var contactId = $(this).data("contactId");
  $(".modal-body #contactId").val(contactId);
});
