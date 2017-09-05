  function showBookmark(results) {
    console.log(results.id);
    var num = results.id;

      $("#bookmark" + num).css("color", "#c70039");
      // window.location.reload();
      // $("#bookmarkedPresents").load("#bookmarkedPresents")
      $("#bookmarkedPresents").append("<div class='product-display' id='prod'" + results.id +"><p><img class='img-responsive' src='" + results.image + "'></p><div class='product-display-title'><a class='display-title-link' href='/product-details/" + results.id + "?event_id="+ results.event +"'><p>"+ results.title +"</p></a></div></div>");

  }

    function unBookmark(results) {
    console.log(results.id);
    var num = results.id;
   
      $("#bookmark" + num).css("color", "#454545");
      $("#bookmarkedPresents").remove("#prod" + num);
      window.location.reload();
      // $("#bookmarkedPresents").load()
 
  }

  function goBookmark(evt) {
    evt.preventDefault();
    var bookmarkInfo = {
      "product": $(this).data("productId"),
      "event": $(this).data("eventId"),
      "status": $(this).data("statusName"),
      "image": $(this).data("productImgurl"),
      "url": $(this).data("productUrl"),
      "title": $(this).data("productTitle")

    };
    console.log(bookmarkInfo);

    if(! $(this).data("bookmark")) {

      console.log("bookmark")
      $(this).data('bookmark', 1);
      $.post("/bookmark.json", bookmarkInfo, showBookmark);
    }
    
    else {
 
      console.log("unbookmark")
      $(this).data('bookmark', null);
      $.post("/unbookmark.json", bookmarkInfo, unBookmark);
    }

  }


  $(".bookmark-link").on("click", goBookmark);


  function setBookmark(results) {
    var bookmarked = results.bookmarked

    for (var i = 0; i < bookmarked.length; i ++) {

      $("#bookmark" + bookmarked[i]).css("color", "#c70039");
      $("#bookmark" + bookmarked[i]).parent().data("bookmark", 1);

    }
  }

  function checkBookmark() {

    var prod = {
      "event": $(".bookmark-link").data("eventId"),
      "status": $(".bookmark-link").data("statusName")
    };

    $.get("/exists.json", prod, setBookmark);

  }

  $(document).ready(checkBookmark);