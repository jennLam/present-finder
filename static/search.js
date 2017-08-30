"use strict";


function showResults(results) {
  $("#searchResults").html("<h3>Search Results</h3>")
  var data = results.data;

  data.forEach(function(product) {
    $("#searchResults").append("<div style='display: inline-block; width: 200px; vertical-align: top;'><p>" + product["title"]+ "</p><img src=" + product["img_url"] + "></div>");
  });
  
}

function getResults(evt) {
  evt.preventDefault();

  var searchInputs = {
    "text": $("#textInput").val(),
    "cat": $("#catInput").val()
  };

  $.get("/search.json", searchInputs, showResults);


}

$("#searchBox").on("submit", getResults);

