$(function () {
  $("#doingInput").focus();
});

$("span.delBtn").on("click", function (e) {
  $(this).parent().hide();
  e.preventDefault();
  var id = $(this).parent().attr("id").split("_")[1];
  console.log(`Deleted task with id = ${id}`);
  $.getJSON(`/delete/${id}`, function (data) {
    //do nothing
  });
  return false;
});

$(".todo-list .todo-item span.todoTitle").on("click", function (e) {
  e.preventDefault();
  var id = $(this).parent().attr("id").split("_")[1];
  console.log(`Updated task with id = ${id}`);
  $.getJSON(`/update/${id}`, function (data) {
    //do nothing
  });
  return false;
});

$(".todo-list .todo-item span.todoTitle").click(function () {
  console.log("click");
  $(this).parent().toggleClass("complete");
});

$(".todo-nav .all-task").click(function () {
  $(".todo-list").removeClass("only-active");
  $(".todo-list").removeClass("only-complete");
  $(".todo-nav li.active").removeClass("active");
  $(this).addClass("active");
});

$(".todo-nav .active-task").click(function () {
  $(".todo-list").removeClass("only-complete");
  $(".todo-list").addClass("only-active");
  $(".todo-nav li.active").removeClass("active");
  $(this).addClass("active");
});

$(".todo-nav .completed-task").click(function () {
  $(".todo-list").removeClass("only-active");
  $(".todo-list").addClass("only-complete");
  $(".todo-nav li.active").removeClass("active");
  $(this).addClass("active");
});
