"use strict";

  function showEvent(results) {
    var contact = results.contact
    var bookmarked = results.bookmarked
    var event = results.event

    $("#searchResults").html("<h3>Event Details</h3>");
    $("#searchResults").append("<a href='/' data-contact-id=" + contact.contact_id + " class='contact-link'>" + contact.fname + " " + contact.lname + "'s</a> " + event.event_name + " - " + event.date)

    $("#searchResults").append("<h4>Selected Presents</h4>")
      results.selected.forEach(function(present) {
    $("#searchResults").append("<div style='display: inline-block; width: 200px; vertical-align: top;'><p>" + present.present_name+ "</p><img src=" + present.img_url + "></div>");
  });

    $("#searchResults").append("<h4>Past Presents</h4>")
    results.past.forEach(function(present) {
    $("#searchResults").append("<div style='display: inline-block; width: 200px; vertical-align: top;'><p>" + present.present_name+ "</p><img src=" + present.img_url + "></div>");
     });

    $("#searchResults").append("<h4>Bookmarked Presents</h4>")
    results.bookmarked.forEach(function(present) {
    $("#searchResults").append("<div style='display: inline-block; width: 200px; vertical-align: top;'><p>" + present.present_name+ "</p><img src=" + present.img_url + "></div>");
     });

    $("#searchResults").append("<h4>Suggested Presents</h4>")

    results.products.forEach(function(data) {
      data.forEach(function(product) {
    $("#searchResults").append("<div style='display: inline-block; width: 200px; vertical-align: top;'><p>" + product.title + "</p><img src=" + product.img_url + "></div>");

  });
  });
  

  }

  function getEvent(evt) {
    evt.preventDefault();
    var eventId = {"event": $(this).data("eventId")};

    $.get("/event.json", eventId, showEvent)

  }

  // $(".event-link").on("click", getEvent);
  $(document).on("click", ".event-link", getEvent);


