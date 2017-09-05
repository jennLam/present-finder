  function showBookmark(results) {
    console.log(results.data);
    var num = results.data;

      $("#bookmark" + num).css("color", "#c70039");
      // window.location.reload();
      // $("#bookmarkedPresents").load("#bookmarkedPresents")

  }

    function unBookmark(results) {
    console.log(results.data);
    var num = results.data;
   
      $("#bookmark" + num).css("color", "#454545");
      // window.location.reload();
      // $("#bookmarkedPresents").load()
 
  }

  function goBookmark(evt) {
    evt.preventDefault();
    var bookmarkInfo = {
      "product": $(this).data("productId"),
      "event": $(this).data("eventId"),
      "status": $(this).data("statusName"),

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